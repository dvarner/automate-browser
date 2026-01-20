// Background Service Worker for Workflow Recorder
// Manages recording state and coordinates between popup and content scripts

let recordingState = {
  isRecording: false,
  actions: [],
  startUrl: null,
  tabId: null
};

// Template Builder State
let templateState = {
  isBuilding: false,
  fields: [],  // { name, selector, attribute, required }
  containerSelector: null,
  detectedItems: [],
  paginationSelector: null,
  tabId: null
};

// Region Extract State
let regionExtractState = {
  isSelecting: false,
  selectedRegion: null,  // { x, y, width, height }
  extractedText: [],     // Array of text elements
  tabId: null
};

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'GET_RECORDING_STATE':
      sendResponse(recordingState);
      break;

    case 'START_RECORDING':
      startRecording(message.tabId, message.url);
      sendResponse({ success: true, state: recordingState });
      break;

    case 'STOP_RECORDING':
      stopRecording();
      sendResponse({ success: true, state: recordingState });
      break;

    case 'CLEAR_ACTIONS':
      recordingState.actions = [];
      sendResponse({ success: true });
      break;

    case 'ACTION_CAPTURED':
      // Action captured from content script
      console.log('[Background] Action captured:', message.action);
      recordingState.actions.push(message.action);
      console.log('[Background] Total actions:', recordingState.actions.length);
      // Notify popup to update UI
      chrome.runtime.sendMessage({ type: 'ACTIONS_UPDATED', actions: recordingState.actions })
        .catch(err => console.log('[Background] Popup closed, action stored'));
      sendResponse({ success: true });
      break;

    case 'DELETE_ACTION':
      if (message.index >= 0 && message.index < recordingState.actions.length) {
        recordingState.actions.splice(message.index, 1);
        sendResponse({ success: true, actions: recordingState.actions });
      } else {
        sendResponse({ success: false, error: 'Invalid index' });
      }
      break;

    case 'UPDATE_ACTION':
      if (message.index >= 0 && message.index < recordingState.actions.length) {
        recordingState.actions[message.index] = message.action;
        sendResponse({ success: true, actions: recordingState.actions });
      } else {
        sendResponse({ success: false, error: 'Invalid index' });
      }
      break;

    // Template Builder Messages
    case 'GET_TEMPLATE_STATE':
      sendResponse(templateState);
      break;

    case 'START_TEMPLATE_BUILDING':
      startTemplateBuilding(message.tabId, message.url);
      sendResponse({ success: true, state: templateState });
      break;

    case 'STOP_TEMPLATE_BUILDING':
      stopTemplateBuilding();
      sendResponse({ success: true });
      break;

    case 'ADD_TEMPLATE_FIELD':
      templateState.fields.push(message.field);
      chrome.runtime.sendMessage({ type: 'TEMPLATE_UPDATED', state: templateState })
        .catch(() => {});
      sendResponse({ success: true });
      break;

    case 'SET_CONTAINER':
      templateState.containerSelector = message.selector;
      templateState.detectedItems = message.items || [];
      sendResponse({ success: true });
      break;

    // Region Extract Messages
    case 'GET_REGION_STATE':
      sendResponse(regionExtractState);
      break;

    case 'START_REGION_SELECTION':
      startRegionSelection(message.tabId, message.url);
      sendResponse({ success: true, state: regionExtractState });
      break;

    case 'STOP_REGION_SELECTION':
      stopRegionSelection();
      sendResponse({ success: true });
      break;

    case 'REGION_SELECTED':
      regionExtractState.selectedRegion = message.region;
      sendResponse({ success: true });
      break;

    case 'TEXT_EXTRACTED':
      regionExtractState.extractedText = message.textElements;
      regionExtractState.selectedRegion = message.region;
      // Notify popup to update UI
      chrome.runtime.sendMessage({ type: 'REGION_EXTRACT_UPDATED', state: regionExtractState })
        .catch(() => {});
      sendResponse({ success: true });
      break;

    case 'CLEAR_EXTRACTED_TEXT':
      regionExtractState.extractedText = [];
      regionExtractState.selectedRegion = null;
      sendResponse({ success: true });
      break;
  }

  return true; // Keep message channel open for async response
});

// Start recording
async function startRecording(tabId, url) {
  // Check if URL is valid for content script injection
  if (!url || url.startsWith('chrome://') || url.startsWith('chrome-extension://') ||
      url.startsWith('edge://') || url.startsWith('about:')) {
    console.error('[Background] Cannot inject into system page:', url);
    throw new Error('Cannot record on system pages (chrome://, edge://, about:). Please navigate to a web page.');
  }

  recordingState = {
    isRecording: true,
    actions: [{
      action: 'navigate',
      url: url,
      timestamp: Date.now()
    }],
    startUrl: url,
    tabId: tabId
  };

  console.log('[Background] Added initial navigate action:', url);

  // Inject content script into the active tab
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: ['content-script.js']
    });

    console.log('[Background] Content script injected');

    // Send message to content script to start recording
    await chrome.tabs.sendMessage(tabId, { type: 'START_RECORDING' });
    console.log('[Background] Recording started');

  } catch (error) {
    console.error('[Background] Error injecting content script:', error);
    recordingState.isRecording = false;
    throw error;
  }
}

// Stop recording
async function stopRecording() {
  if (recordingState.tabId) {
    try {
      // Check if tab still exists
      const tab = await chrome.tabs.get(recordingState.tabId);

      // Tell content script to stop recording
      await chrome.tabs.sendMessage(recordingState.tabId, { type: 'STOP_RECORDING' });
      console.log('[Background] Stop message sent to content script');
    } catch (error) {
      // Tab might be closed or navigated away - that's okay
      console.log('[Background] Could not send stop message (tab may be closed):', error.message);
    }
  }

  recordingState.isRecording = false;
  console.log('[Background] Recording stopped');
}

// Listen for tab updates (navigation)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (recordingState.isRecording && tabId === recordingState.tabId) {
    if (changeInfo.status === 'complete' && tab.url) {
      // Check if URL is valid for injection
      if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://') ||
          tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
        console.log('[Background] Navigated to system page, stopping recording');
        stopRecording();
        return;
      }

      // Page navigated to valid URL
      const action = {
        action: 'navigate',
        url: tab.url,
        timestamp: Date.now()
      };
      recordingState.actions.push(action);
      console.log('[Background] Navigation captured:', tab.url);

      // Notify popup
      chrome.runtime.sendMessage({ type: 'ACTIONS_UPDATED', actions: recordingState.actions })
        .catch(err => console.log('[Background] Popup closed'));

      // Re-inject content script after navigation
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content-script.js']
      }).then(() => {
        console.log('[Background] Content script re-injected after navigation');
        return chrome.tabs.sendMessage(tabId, { type: 'START_RECORDING' });
      }).then(() => {
        console.log('[Background] Recording restarted on new page');
      }).catch(err => console.error('[Background] Error re-injecting:', err));
    }
  }
});

// === Template Building Functions ===

async function startTemplateBuilding(tabId, url) {
  templateState = {
    isBuilding: true,
    fields: [],
    containerSelector: null,
    detectedItems: [],
    tabId: tabId
  };

  await chrome.scripting.executeScript({
    target: { tabId: tabId },
    files: ['content-script.js']
  });

  await chrome.tabs.sendMessage(tabId, { type: 'START_TEMPLATE_BUILDING' });
}

async function stopTemplateBuilding() {
  if (templateState.tabId) {
    try {
      await chrome.tabs.sendMessage(templateState.tabId, { type: 'STOP_TEMPLATE_BUILDING' });
    } catch (e) {
      console.log('[Background] Could not stop template building on tab:', e.message);
    }
  }
  templateState.isBuilding = false;
}

// === Region Extract Functions ===

async function startRegionSelection(tabId, url) {
  regionExtractState = {
    isSelecting: true,
    selectedRegion: null,
    extractedText: [],
    tabId: tabId
  };

  await chrome.scripting.executeScript({
    target: { tabId: tabId },
    files: ['content-script.js']
  });

  await chrome.tabs.sendMessage(tabId, { type: 'START_REGION_SELECTION' });
}

async function stopRegionSelection() {
  if (regionExtractState.tabId) {
    try {
      await chrome.tabs.sendMessage(regionExtractState.tabId, { type: 'STOP_REGION_SELECTION' });
    } catch (e) {
      console.log('[Background] Could not stop region selection on tab:', e.message);
    }
  }
  regionExtractState.isSelecting = false;
}

// Keep service worker alive
chrome.runtime.onInstalled.addListener(() => {
  console.log('Workflow Recorder extension installed');
});
