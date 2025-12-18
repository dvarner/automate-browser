// Content Script - Captures user interactions on the page
// Injected into active tab when recording starts

let isRecording = false;
let recordingIndicator = null;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'START_RECORDING') {
    startRecording();
    sendResponse({ success: true });
  } else if (message.type === 'STOP_RECORDING') {
    stopRecording();
    sendResponse({ success: true });
  }
  return true;
});

// Start recording
function startRecording() {
  if (isRecording) return;

  isRecording = true;
  showRecordingIndicator();
  attachEventListeners();
}

// Stop recording
function stopRecording() {
  if (!isRecording) return;

  isRecording = false;
  hideRecordingIndicator();
  removeEventListeners();
}

// Show visual indicator that recording is active
function showRecordingIndicator() {
  if (recordingIndicator) return;

  recordingIndicator = document.createElement('div');
  recordingIndicator.id = 'workflow-recorder-indicator';
  recordingIndicator.innerHTML = `
    <div style="display: flex; align-items: center; gap: 8px;">
      <span style="width: 8px; height: 8px; background: white; border-radius: 50%; animation: pulse 2s infinite;"></span>
      <span>Recording</span>
    </div>
  `;
  recordingIndicator.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 20px;
    background: rgba(244, 67, 54, 0.95);
    color: white;
    padding: 10px 16px;
    border-radius: 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
    font-weight: 600;
    z-index: 2147483647;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    cursor: move;
    user-select: none;
    backdrop-filter: blur(10px);
  `;

  // Add pulsing animation
  const style = document.createElement('style');
  style.id = 'workflow-recorder-style';
  style.textContent = `
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  `;

  // Only add style if not already present
  if (!document.getElementById('workflow-recorder-style')) {
    document.head.appendChild(style);
  }

  // Make it draggable
  makeDraggable(recordingIndicator);

  document.body.appendChild(recordingIndicator);

  console.log('[Recorder] Recording indicator shown');
}

// Make indicator draggable
function makeDraggable(element) {
  let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

  element.onmousedown = dragMouseDown;

  function dragMouseDown(e) {
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e.preventDefault();
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    element.style.top = (element.offsetTop - pos2) + "px";
    element.style.left = (element.offsetLeft - pos1) + "px";
    element.style.bottom = "auto";
    element.style.right = "auto";
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

// Hide recording indicator
function hideRecordingIndicator() {
  if (recordingIndicator) {
    recordingIndicator.remove();
    recordingIndicator = null;
  }
}

// Event handlers
const clickHandler = (e) => {
  if (!isRecording) return;
  if (e.target.id === 'workflow-recorder-indicator') return; // Ignore clicks on indicator

  const selector = generateSelector(e.target);
  const action = {
    action: 'click',
    selector: selector,
    text: e.target.innerText?.substring(0, 50) || '',
    timestamp: Date.now()
  };

  sendActionToBackground(action);

  // Visual feedback
  highlightElement(e.target);
};

const inputHandler = (e) => {
  if (!isRecording) return;

  const selector = generateSelector(e.target);
  const isPassword = e.target.type === 'password';

  const action = {
    action: 'fill',
    selector: selector,
    value: isPassword ? '********' : e.target.value,
    sensitive: isPassword,
    timestamp: Date.now()
  };

  sendActionToBackground(action);
};

const changeHandler = (e) => {
  if (!isRecording) return;

  // For selects and checkboxes
  if (e.target.tagName === 'SELECT' || e.target.type === 'checkbox' || e.target.type === 'radio') {
    const selector = generateSelector(e.target);
    const action = {
      action: 'fill',
      selector: selector,
      value: e.target.value || e.target.checked,
      timestamp: Date.now()
    };

    sendActionToBackground(action);
  }
};

// Attach event listeners
function attachEventListeners() {
  document.addEventListener('click', clickHandler, true);
  document.addEventListener('input', inputHandler, true);
  document.addEventListener('change', changeHandler, true);
}

// Remove event listeners
function removeEventListeners() {
  document.removeEventListener('click', clickHandler, true);
  document.removeEventListener('input', inputHandler, true);
  document.removeEventListener('change', changeHandler, true);
}

// Generate unique selector for an element
function generateSelector(element) {
  // Priority: ID > name attribute > data-testid > class > tag + nth-child

  // Try ID first (most specific)
  if (element.id) {
    return `#${element.id}`;
  }

  // Try name attribute (common for forms)
  if (element.name) {
    return `${element.tagName.toLowerCase()}[name="${element.name}"]`;
  }

  // Try data-testid or data-test
  if (element.dataset.testid) {
    return `[data-testid="${element.dataset.testid}"]`;
  }
  if (element.dataset.test) {
    return `[data-test="${element.dataset.test}"]`;
  }

  // Try unique class combination
  if (element.className && typeof element.className === 'string') {
    const classes = element.className.trim().split(/\s+/).filter(c => c.length > 0);
    if (classes.length > 0) {
      const selector = `${element.tagName.toLowerCase()}.${classes.join('.')}`;
      // Check if unique
      if (document.querySelectorAll(selector).length === 1) {
        return selector;
      }
    }
  }

  // Try tag + type for inputs
  if (element.type) {
    const selector = `${element.tagName.toLowerCase()}[type="${element.type}"]`;
    if (document.querySelectorAll(selector).length === 1) {
      return selector;
    }
  }

  // Fallback: tag + nth-child
  let path = [];
  let current = element;

  while (current && current !== document.body) {
    let selector = current.tagName.toLowerCase();

    if (current.parentElement) {
      const siblings = Array.from(current.parentElement.children);
      const index = siblings.indexOf(current) + 1;
      selector += `:nth-child(${index})`;
    }

    path.unshift(selector);
    current = current.parentElement;
  }

  return path.join(' > ');
}

// Send action to background script
function sendActionToBackground(action) {
  console.log('[Recorder] Sending action to background:', action);
  chrome.runtime.sendMessage({
    type: 'ACTION_CAPTURED',
    action: action
  }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('[Recorder] Error sending action:', chrome.runtime.lastError);
    } else {
      console.log('[Recorder] Action sent successfully:', response);
    }
  });
}

// Highlight element briefly when clicked
function highlightElement(element) {
  const originalOutline = element.style.outline;
  element.style.outline = '2px solid #00ff00';

  setTimeout(() => {
    element.style.outline = originalOutline;
  }, 500);
}
