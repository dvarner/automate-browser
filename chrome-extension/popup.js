// Tab Session Exporter & Workflow Recorder - Main Logic

let currentTabsData = null;
let currentGroupsData = null;
let recordingState = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
  await loadTabsInfo();
  setupEventListeners();
  generateDefaultSessionName();
  await loadRecordingState();
  await loadTemplateState();
  setupTabSwitching();
});

// Setup event listeners
function setupEventListeners() {
  document.getElementById('export-btn').addEventListener('click', handleExport);
  document.getElementById('preview-btn').addEventListener('click', handlePreview);
  document.getElementById('session-name').addEventListener('input', validateSessionName);
}

// Generate default session name based on timestamp
function generateDefaultSessionName() {
  const now = new Date();
  const timestamp = now.toISOString().split('T')[0].replace(/-/g, '');
  const time = now.toTimeString().split(':').slice(0, 2).join('');
  const defaultName = `session-${timestamp}-${time}`;
  document.getElementById('session-name').value = defaultName;
}

// Validate session name (alphanumeric, dash, underscore only)
function validateSessionName() {
  const input = document.getElementById('session-name');
  const value = input.value;
  const isValid = /^[a-zA-Z0-9-_]+$/.test(value) && value.length > 0;

  document.getElementById('export-btn').disabled = !isValid;

  return isValid;
}

// Load tabs and groups information
async function loadTabsInfo() {
  try {
    const includeAllWindows = document.getElementById('include-all-windows').checked;

    // Get tabs
    let tabs;
    if (includeAllWindows) {
      tabs = await chrome.tabs.query({});
    } else {
      tabs = await chrome.tabs.query({ currentWindow: true });
    }

    // Get tab groups
    const groups = await chrome.tabGroups.query({});

    // Store for later use
    currentTabsData = tabs;
    currentGroupsData = groups;

    // Update UI
    document.getElementById('tab-count').textContent = tabs.length;

    const groupedTabs = tabs.filter(tab => tab.groupId !== chrome.tabGroups.TAB_GROUP_ID_NONE);
    const uniqueGroups = new Set(groupedTabs.map(tab => tab.groupId));
    document.getElementById('group-count').textContent = uniqueGroups.size;

    const windowCount = new Set(tabs.map(tab => tab.windowId)).size;
    document.getElementById('window-info').textContent = includeAllWindows
      ? `All windows (${windowCount})`
      : 'Current only';

  } catch (error) {
    console.error('Error loading tabs:', error);
    showStatus('Error loading tabs: ' + error.message, 'error');
  }
}

// Handle include all windows checkbox change
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('include-all-windows').addEventListener('change', loadTabsInfo);
});

// Convert tabs and groups to session manager format
function convertToSessionFormat(sessionName, tabs, groups) {
  const now = new Date().toISOString();

  // Create a map of group IDs to group info
  const groupMap = {};
  groups.forEach(group => {
    groupMap[group.id] = {
      name: group.title || `Group ${group.id}`,
      color: group.color
    };
  });

  // Separate tabs by group
  const groupedTabsMap = {};
  const ungroupedTabs = [];

  tabs.forEach((tab, index) => {
    const tabData = {
      order: index + 1,
      url: tab.url,
      title: tab.title || 'Untitled'
    };

    // Check if tab is in a group
    if (tab.groupId !== chrome.tabGroups.TAB_GROUP_ID_NONE && groupMap[tab.groupId]) {
      const groupName = groupMap[tab.groupId].name;
      if (!groupedTabsMap[groupName]) {
        groupedTabsMap[groupName] = [];
      }
      groupedTabsMap[groupName].push(tabData);
    } else {
      ungroupedTabs.push(tabData);
    }
  });

  // Build session data
  const sessionData = {
    session_name: sessionName,
    created_at: now
  };

  // If we have groups, use grouped format
  if (Object.keys(groupedTabsMap).length > 0) {
    sessionData.groups = [];

    // Add groups
    Object.entries(groupedTabsMap).forEach(([groupName, groupTabs]) => {
      sessionData.groups.push({
        name: groupName,
        tabs: groupTabs.map((tab, idx) => ({
          order: idx + 1,
          url: tab.url,
          title: tab.title
        }))
      });
    });

    // Add ungrouped tabs if any
    if (ungroupedTabs.length > 0) {
      sessionData.ungrouped_tabs = ungroupedTabs.map((tab, idx) => ({
        order: idx + 1,
        url: tab.url,
        title: tab.title
      }));
    }
  } else {
    // No groups, use flat format
    sessionData.tabs = tabs.map((tab, idx) => ({
      order: idx + 1,
      url: tab.url,
      title: tab.title || 'Untitled'
    }));
  }

  return sessionData;
}

// Handle export
async function handleExport() {
  if (!validateSessionName()) {
    showStatus('Please enter a valid session name', 'error');
    return;
  }

  const sessionName = document.getElementById('session-name').value;

  try {
    showStatus('Exporting session...', 'info');

    // Convert to session format
    const sessionData = convertToSessionFormat(sessionName, currentTabsData, currentGroupsData);

    // Create JSON blob
    const jsonString = JSON.stringify(sessionData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });

    // Create download
    const url = URL.createObjectURL(blob);
    const filename = `${sessionName}.json`;

    // Trigger download
    await chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    });

    // Calculate stats
    let totalTabs = 0;
    if (sessionData.groups) {
      totalTabs = sessionData.groups.reduce((sum, g) => sum + g.tabs.length, 0);
      totalTabs += (sessionData.ungrouped_tabs || []).length;
    } else {
      totalTabs = sessionData.tabs.length;
    }

    showStatus(`✓ Exported ${totalTabs} tabs successfully! Save to: tab-session-manager/sessions/`, 'success');

    // Clean up
    setTimeout(() => URL.revokeObjectURL(url), 1000);

  } catch (error) {
    console.error('Export error:', error);
    showStatus('Export failed: ' + error.message, 'error');
  }
}

// Handle preview
function handlePreview() {
  if (!validateSessionName()) {
    showStatus('Please enter a valid session name', 'error');
    return;
  }

  const sessionName = document.getElementById('session-name').value;

  try {
    const sessionData = convertToSessionFormat(sessionName, currentTabsData, currentGroupsData);

    // Build preview HTML
    let previewHTML = '';

    if (sessionData.groups) {
      // Grouped format
      sessionData.groups.forEach(group => {
        previewHTML += `<div class="preview-group">`;
        previewHTML += `<div class="preview-group-name">📁 ${group.name} (${group.tabs.length} tabs)</div>`;
        group.tabs.forEach(tab => {
          previewHTML += `<div class="preview-tab">• ${tab.title}</div>`;
        });
        previewHTML += `</div>`;
      });

      // Ungrouped tabs
      if (sessionData.ungrouped_tabs && sessionData.ungrouped_tabs.length > 0) {
        previewHTML += `<div class="preview-group">`;
        previewHTML += `<div class="preview-group-name">📄 Ungrouped (${sessionData.ungrouped_tabs.length} tabs)</div>`;
        sessionData.ungrouped_tabs.forEach(tab => {
          previewHTML += `<div class="preview-tab">• ${tab.title}</div>`;
        });
        previewHTML += `</div>`;
      }
    } else {
      // Flat format
      previewHTML += `<div class="preview-group">`;
      previewHTML += `<div class="preview-group-name">📄 All Tabs (${sessionData.tabs.length})</div>`;
      sessionData.tabs.forEach(tab => {
        previewHTML += `<div class="preview-tab">• ${tab.title}</div>`;
      });
      previewHTML += `</div>`;
    }

    // Show preview
    document.getElementById('preview-content').innerHTML = previewHTML;
    document.getElementById('preview').classList.remove('hidden');

    showStatus('Preview generated', 'info');

  } catch (error) {
    console.error('Preview error:', error);
    showStatus('Preview failed: ' + error.message, 'error');
  }
}

// Show status message
function showStatus(message, type) {
  const statusEl = document.getElementById('status');
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  statusEl.classList.remove('hidden');

  // Auto-hide after 5 seconds for success/info
  if (type === 'success' || type === 'info') {
    setTimeout(() => {
      statusEl.classList.add('hidden');
    }, 5000);
  }
}

// ============================================================================
// WORKFLOW RECORDER FUNCTIONALITY
// ============================================================================

// Setup tab switching
function setupTabSwitching() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;

      // Update buttons
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Update content
      tabContents.forEach(content => {
        if (content.id === `${tabName}-tab`) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });
    });
  });

  // Setup recorder event listeners
  document.getElementById('start-record-btn').addEventListener('click', handleStartRecording);
  document.getElementById('stop-record-btn').addEventListener('click', handleStopRecording);
  document.getElementById('clear-actions-btn').addEventListener('click', handleClearActions);
  document.getElementById('preview-yaml-btn').addEventListener('click', handlePreviewYAML);
  document.getElementById('export-yaml-btn').addEventListener('click', handleExportYAML);

  // Setup scraper event listeners
  document.getElementById('start-template-btn').addEventListener('click', handleStartTemplateBuilding);
  document.getElementById('stop-template-btn').addEventListener('click', handleStopTemplateBuilding);
  document.getElementById('detect-items-btn').addEventListener('click', handleDetectItems);
  document.getElementById('preview-template-btn').addEventListener('click', handlePreviewTemplate);
  document.getElementById('export-template-btn').addEventListener('click', handleExportTemplate);
}

// Load recording state from background
async function loadRecordingState() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_RECORDING_STATE' });
    recordingState = response;
    console.log('[Popup] Loaded recording state:', recordingState);
    console.log('[Popup] Actions count:', recordingState.actions?.length || 0);
    updateRecordingUI();
  } catch (error) {
    console.error('[Popup] Error loading state:', error);
  }
}

// Update recording UI based on state
function updateRecordingUI() {
  console.log('[Popup] Updating UI with state:', recordingState);

  const statusEl = document.getElementById('recording-status');
  const startBtn = document.getElementById('start-record-btn');
  const stopBtn = document.getElementById('stop-record-btn');
  const actionsSection = document.getElementById('actions-section');

  if (!statusEl || !startBtn || !stopBtn || !actionsSection) {
    console.error('[Popup] UI elements not found!');
    return;
  }

  if (recordingState.isRecording) {
    statusEl.textContent = '🔴 Recording...';
    statusEl.className = 'status-recording';
    startBtn.disabled = true;
    stopBtn.disabled = false;
    console.log('[Popup] UI set to recording state');
  } else {
    statusEl.textContent = '⚪ Ready to Record';
    statusEl.className = 'status-idle';
    startBtn.disabled = false;
    stopBtn.disabled = true;
    console.log('[Popup] UI set to idle state');
  }

  // Show actions section if we have actions
  const hasActions = recordingState.actions && recordingState.actions.length > 0;
  console.log('[Popup] Has actions:', hasActions, 'Count:', recordingState.actions?.length);

  if (hasActions) {
    actionsSection.classList.remove('hidden');
    renderActions();
    console.log('[Popup] Actions section shown');
  } else {
    actionsSection.classList.add('hidden');
    console.log('[Popup] Actions section hidden (no actions)');
  }
}

// Start recording
async function handleStartRecording() {
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    console.log('[Popup] Starting recording on tab:', tab.url);

    // Check if we can record on this page
    if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://') ||
        tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
      alert('❌ Cannot record on system pages!\n\nPlease navigate to a web page (e.g., https://example.com) and try again.');
      return;
    }

    // Send start recording message to background
    const response = await chrome.runtime.sendMessage({
      type: 'START_RECORDING',
      tabId: tab.id,
      url: tab.url
    });

    if (response.success) {
      recordingState = response.state;
      updateRecordingUI();
      console.log('[Popup] Recording started successfully');
      // Close popup so user can interact with page
      // window.close(); // Commented out so popup stays open for debugging
    }
  } catch (error) {
    console.error('[Popup] Error starting recording:', error);
    alert('❌ Failed to start recording!\n\n' + error.message + '\n\nMake sure you\'re on a web page, not a chrome:// page.');
  }
}

// Stop recording
async function handleStopRecording() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'STOP_RECORDING' });

    if (response.success) {
      recordingState = response.state;
      updateRecordingUI();
    }
  } catch (error) {
    console.error('Error stopping recording:', error);
    alert('Failed to stop recording: ' + error.message);
  }
}

// Clear all actions
async function handleClearActions() {
  if (!confirm('Clear all captured actions?')) return;

  try {
    await chrome.runtime.sendMessage({ type: 'CLEAR_ACTIONS' });
    recordingState.actions = [];
    updateRecordingUI();
  } catch (error) {
    console.error('Error clearing actions:', error);
  }
}

// Render actions list
function renderActions() {
  const actionsList = document.getElementById('actions-list');
  const actionCount = document.getElementById('action-count');

  actionCount.textContent = recordingState.actions.length;

  if (!recordingState.actions || recordingState.actions.length === 0) {
    actionsList.innerHTML = '<p class="no-actions">No actions captured yet</p>';
    return;
  }

  let html = '';
  recordingState.actions.forEach((action, index) => {
    html += `
      <div class="action-item">
        <div class="action-number">${index + 1}</div>
        <div class="action-details">
          <div class="action-type">${action.action}</div>
          ${renderActionDetails(action)}
        </div>
        <button class="delete-action-btn" data-index="${index}">✕</button>
      </div>
    `;
  });

  actionsList.innerHTML = html;

  // Add delete listeners
  document.querySelectorAll('.delete-action-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const index = parseInt(e.target.dataset.index);
      const response = await chrome.runtime.sendMessage({
        type: 'DELETE_ACTION',
        index: index
      });
      if (response.success) {
        recordingState.actions = response.actions;
        renderActions();
      }
    });
  });
}

// Render action details
function renderActionDetails(action) {
  switch (action.action) {
    case 'navigate':
      return `<div class="action-detail">URL: ${action.url}</div>`;

    case 'click':
      return `
        <div class="action-detail">Selector: ${action.selector}</div>
        ${action.text ? `<div class="action-detail">Text: ${action.text}</div>` : ''}
      `;

    case 'fill':
      return `
        <div class="action-detail">Selector: ${action.selector}</div>
        <div class="action-detail">Value: ${action.value}</div>
      `;

    default:
      return `<div class="action-detail">${JSON.stringify(action)}</div>`;
  }
}

// Preview YAML
function handlePreviewYAML() {
  const workflowName = document.getElementById('workflow-name').value || 'recorded-workflow';
  const yaml = actionsToYAML(recordingState.actions, workflowName, 'chrome');

  const previewEl = document.getElementById('yaml-preview');
  previewEl.innerHTML = previewYAML(yaml);
  previewEl.classList.remove('hidden');
}

// Export YAML
function handleExportYAML() {
  const workflowName = document.getElementById('workflow-name').value || 'recorded-workflow';
  const yaml = actionsToYAML(recordingState.actions, workflowName, 'chrome');

  const filename = `${workflowName}.yaml`;
  downloadYAML(yaml, filename);

  alert(`✓ Exported to ${filename}\n\nSave to: workflow-engine/workflows/\n\nRun with:\npython workflow_runner.py workflows/${filename}`);
}

// Listen for action updates from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Popup] Received message:', message);
  if (message.type === 'ACTIONS_UPDATED') {
    console.log('[Popup] Actions updated, new count:', message.actions.length);
    recordingState.actions = message.actions;
    updateRecordingUI();
  } else if (message.type === 'TEMPLATE_UPDATED') {
    templateState = message.state;
    updateTemplateUI();
  }
  return true;
});

// ============================================================================
// TEMPLATE BUILDER FUNCTIONS
// ============================================================================

let templateState = null;

async function loadTemplateState() {
  const response = await chrome.runtime.sendMessage({ type: 'GET_TEMPLATE_STATE' });
  templateState = response;
  updateTemplateUI();
}

function updateTemplateUI() {
  if (!templateState) return;

  const statusEl = document.getElementById('scraper-status');
  const startBtn = document.getElementById('start-template-btn');
  const stopBtn = document.getElementById('stop-template-btn');
  const fieldsSection = document.getElementById('template-fields-section');

  if (templateState.isBuilding) {
    statusEl.textContent = '🎯 Building Template...';
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } else {
    statusEl.textContent = '⚪ Ready to Build Template';
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }

  if (templateState.fields && templateState.fields.length > 0) {
    fieldsSection.classList.remove('hidden');
    renderTemplateFields();
  } else {
    fieldsSection.classList.add('hidden');
  }
}

async function handleStartTemplateBuilding() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  const response = await chrome.runtime.sendMessage({
    type: 'START_TEMPLATE_BUILDING',
    tabId: tab.id,
    url: tab.url
  });

  templateState = response.state;
  updateTemplateUI();
}

async function handleStopTemplateBuilding() {
  await chrome.runtime.sendMessage({ type: 'STOP_TEMPLATE_BUILDING' });
  await loadTemplateState();
}

async function handleDetectItems() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  const response = await chrome.tabs.sendMessage(tab.id, {
    type: 'DETECT_CONTAINER_AND_ITEMS',
    fieldSelectors: templateState.fields
  });

  await chrome.runtime.sendMessage({
    type: 'SET_CONTAINER',
    selector: response.containerSelector,
    items: response.items
  });

  templateState.containerSelector = response.containerSelector;
  templateState.detectedItems = response.items;

  document.getElementById('detected-count').textContent = response.count || 0;

  let preview = `Container: ${response.containerSelector}\n\n`;
  preview += `Found ${response.count} items\n`;
  document.getElementById('detected-preview').textContent = preview;
}

function renderTemplateFields() {
  const fieldsList = document.getElementById('fields-list');
  const fieldCount = document.getElementById('field-count');

  fieldCount.textContent = templateState.fields.length;

  let html = '';
  templateState.fields.forEach((field, idx) => {
    html += `
      <div class="field-item">
        <div class="field-name">${field.name}</div>
        <div class="field-selector">${field.selector}</div>
      </div>
    `;
  });

  fieldsList.innerHTML = html;
}

function handlePreviewTemplate() {
  const templateName = document.getElementById('template-name').value || 'scrape-template';
  const template = buildTemplateJSON(templateName);

  const previewEl = document.getElementById('template-preview');
  previewEl.innerHTML = `<pre>${JSON.stringify(template, null, 2)}</pre>`;
  previewEl.classList.remove('hidden');
}

function handleExportTemplate() {
  const templateName = document.getElementById('template-name').value || 'scrape-template';
  const template = buildTemplateJSON(templateName);

  const blob = new Blob([JSON.stringify(template, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  chrome.downloads.download({
    url: url,
    filename: `${templateName}.json`,
    saveAs: true
  });

  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function buildTemplateJSON(templateName) {
  const paginationEnabled = document.getElementById('pagination-enabled').checked;
  const nextPageSelector = document.getElementById('next-page-selector').value;

  return {
    template_name: templateName,
    version: '1.0',
    created_at: new Date().toISOString(),
    container: {
      selector: templateState.containerSelector || 'div.item',
      type: 'repeating'
    },
    fields: templateState.fields.map(f => ({
      name: f.name,
      selector: f.selector,
      attribute: f.attribute || 'text',
      required: f.required !== false
    })),
    pagination: paginationEnabled ? {
      enabled: true,
      next_button: nextPageSelector || null,
      type: 'manual'
    } : { enabled: false }
  };
}
