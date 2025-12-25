// Content Script - Captures user interactions on the page
// Injected into active tab when recording starts

let isRecording = false;
let recordingIndicator = null;

// Template Building State
let isTemplateBuilding = false;
let selectedElement = null;
let contextMenu = null;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'START_RECORDING') {
    startRecording();
    sendResponse({ success: true });
  } else if (message.type === 'STOP_RECORDING') {
    stopRecording();
    sendResponse({ success: true });
  } else if (message.type === 'START_TEMPLATE_BUILDING') {
    startTemplateBuilding();
    sendResponse({ success: true });
  } else if (message.type === 'STOP_TEMPLATE_BUILDING') {
    stopTemplateBuilding();
    sendResponse({ success: true });
  } else if (message.type === 'DETECT_CONTAINER_AND_ITEMS') {
    const result = detectContainerAndItems(message.fieldSelectors);
    sendResponse({ success: true, ...result });
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

// ============================================================================
// TEMPLATE BUILDING MODE
// ============================================================================

function startTemplateBuilding() {
  isTemplateBuilding = true;
  showTemplateIndicator();
  document.addEventListener('contextmenu', templateRightClickHandler, true);
}

function stopTemplateBuilding() {
  isTemplateBuilding = false;
  hideTemplateIndicator();
  document.removeEventListener('contextmenu', templateRightClickHandler, true);
  removeContextMenu();
}

function showTemplateIndicator() {
  const indicator = document.createElement('div');
  indicator.id = 'template-builder-indicator';
  indicator.innerHTML = '🎯 Template Building Mode';
  indicator.style.cssText = `
    position: fixed; top: 20px; right: 20px;
    background: rgba(255, 152, 0, 0.95); color: white;
    padding: 10px 16px; border-radius: 8px;
    font-size: 13px; font-weight: 600;
    z-index: 2147483647;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  `;
  document.body.appendChild(indicator);
}

function hideTemplateIndicator() {
  document.getElementById('template-builder-indicator')?.remove();
}

const templateRightClickHandler = (e) => {
  if (!isTemplateBuilding) return;
  e.preventDefault();
  e.stopPropagation();
  selectedElement = e.target;
  showContextMenu(e.clientX, e.clientY);
};

function showContextMenu(x, y) {
  removeContextMenu();

  contextMenu = document.createElement('div');
  contextMenu.style.cssText = `
    position: fixed; left: ${x}px; top: ${y}px;
    background: white; border: 1px solid #e0e0e0;
    border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 2147483648; min-width: 200px;
  `;

  const options = [
    { label: '📝 Extract as Title', field: 'title', attribute: 'text' },
    { label: '💰 Extract as Price', field: 'price', attribute: 'text' },
    { label: '📄 Extract as Description', field: 'description', attribute: 'text' },
    { label: '🖼️ Extract as Image', field: 'image', attribute: 'src' },
    { label: '🔗 Extract as Link', field: 'link', attribute: 'href' },
    { label: '✏️ Custom Field...', field: 'custom', attribute: 'text' }
  ];

  options.forEach(opt => {
    const item = document.createElement('div');
    item.textContent = opt.label;
    item.style.cssText = 'padding: 10px 15px; cursor: pointer;';
    item.onmouseover = () => item.style.background = '#f5f5f5';
    item.onmouseout = () => item.style.background = 'white';
    item.onclick = () => {
      if (opt.field === 'custom') {
        const fieldName = prompt('Enter custom field name:');
        if (fieldName) extractField(fieldName, opt.attribute);
      } else {
        extractField(opt.field, opt.attribute);
      }
      removeContextMenu();
    };
    contextMenu.appendChild(item);
  });

  document.body.appendChild(contextMenu);
  setTimeout(() => {
    document.addEventListener('click', removeContextMenu, { once: true });
  }, 100);
}

function removeContextMenu() {
  contextMenu?.remove();
  contextMenu = null;
}

function extractField(fieldName, attribute = 'text') {
  if (!selectedElement) return;

  const selector = generateSelector(selectedElement);
  const field = {
    name: fieldName,
    selector: selector,
    attribute: attribute,
    required: true
  };

  chrome.runtime.sendMessage({
    type: 'ADD_TEMPLATE_FIELD',
    field: field
  });

  // Visual feedback
  const original = selectedElement.style.outline;
  selectedElement.style.outline = '3px solid #ff9800';
  setTimeout(() => { selectedElement.style.outline = original; }, 1000);

  selectedElement = null;
}

// ============================================================================
// CONTAINER DETECTION ALGORITHM
// ============================================================================

function detectContainerAndItems(fieldSelectors) {
  if (!fieldSelectors || fieldSelectors.length === 0) {
    return { containerSelector: null, items: [] };
  }

  // Get elements for first field
  const firstField = fieldSelectors[0];
  const firstElements = Array.from(document.querySelectorAll(firstField.selector));

  if (firstElements.length === 0) {
    return { containerSelector: null, items: [] };
  }

  // Find common parent container
  const containerSelector = findCommonParentContainer(firstElements);
  if (!containerSelector) {
    return { containerSelector: null, items: [] };
  }

  // Find all container instances
  const containers = Array.from(document.querySelectorAll(containerSelector));

  // Extract data from each container
  const items = [];
  containers.forEach((container, idx) => {
    const itemData = { _index: idx };
    let allFieldsFound = true;

    fieldSelectors.forEach(field => {
      const relativeSelector = makeRelativeSelector(field.selector, containerSelector);
      const elem = container.querySelector(relativeSelector);

      if (elem) {
        if (field.attribute === 'text') {
          itemData[field.name] = elem.innerText.trim().substring(0, 50);
        } else {
          itemData[field.name] = elem.getAttribute(field.attribute)?.substring(0, 50) || null;
        }
      } else if (field.required) {
        allFieldsFound = false;
      }
    });

    if (allFieldsFound) {
      items.push(itemData);
    }
  });

  return {
    containerSelector: containerSelector,
    items: items,
    count: items.length
  };
}

function findCommonParentContainer(elements) {
  // For single element, go up 2-3 levels to find repeating parent
  if (elements.length < 2) {
    let parent = elements[0].parentElement;
    for (let level = 0; level < 3; level++) {
      if (!parent) break;

      const selector = generateContainerSelector(parent);
      const matches = document.querySelectorAll(selector);

      // Check if this selector finds multiple instances (2-50)
      if (matches.length >= 2 && matches.length <= 50) {
        return selector;
      }

      parent = parent.parentElement;
    }
    return null;
  }

  // Find common ancestor for multiple elements
  let candidate = elements[0].parentElement;
  for (let level = 0; level < 3 && candidate; level++) {
    let isCommonParent = elements.every(elem => candidate.contains(elem));

    if (isCommonParent) {
      const selector = generateContainerSelector(candidate);
      const matches = document.querySelectorAll(selector);
      if (matches.length >= 2) {
        return selector;
      }
    }

    candidate = candidate.parentElement;
  }

  return null;
}

function generateContainerSelector(element) {
  // Priority: class-based > tag + class
  if (element.className && typeof element.className === 'string') {
    const classes = element.className.trim().split(/\s+/).filter(c => c);
    if (classes.length > 0) {
      // Try single class
      for (let cls of classes) {
        const selector = `.${cls}`;
        const matches = document.querySelectorAll(selector);
        if (matches.length >= 2 && matches.length <= 50) {
          return selector;
        }
      }
      // Try tag + class
      return `${element.tagName.toLowerCase()}.${classes[0]}`;
    }
  }

  // Fallback: tag name
  return element.tagName.toLowerCase();
}

function makeRelativeSelector(absoluteSelector, containerSelector) {
  // Convert absolute selector to relative (within container)
  if (absoluteSelector.includes(containerSelector)) {
    return absoluteSelector.replace(containerSelector, '').trim().replace(/^>\s*/, '');
  }

  // Extract last meaningful part
  const parts = absoluteSelector.split('>').map(p => p.trim());
  return parts[parts.length - 1] || absoluteSelector;
}
