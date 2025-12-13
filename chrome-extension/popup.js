// Tab Session Exporter - Main Logic

let currentTabsData = null;
let currentGroupsData = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
  await loadTabsInfo();
  setupEventListeners();
  generateDefaultSessionName();
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
