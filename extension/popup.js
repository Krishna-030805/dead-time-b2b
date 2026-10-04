document.addEventListener('DOMContentLoaded', () => {
  const statusBadge = document.getElementById('backend-status');
  const btnDashboard = document.getElementById('btn-dashboard');
  const orgIdInput = document.getElementById('org-id-input');
  const userIdInput = document.getElementById('user-id-input');
  const btnSaveUser = document.getElementById('btn-save-user');
  const saveMsg = document.getElementById('save-msg');

  // Load current org_id and user_id
  chrome.storage.local.get(['org_id', 'user_id'], (res) => {
    if (res.org_id) {
      orgIdInput.value = res.org_id;
    } else {
      orgIdInput.value = 'org_default';
    }

    if (res.user_id) {
      userIdInput.value = res.user_id;
    } else {
      const autoId = "device_" + Math.random().toString(36).substring(2, 8);
      chrome.storage.local.set({ user_id: autoId });
      userIdInput.value = autoId;
    }
  });

  // Save new org_id and user_id
  btnSaveUser.addEventListener('click', () => {
    const orgVal = orgIdInput.value.trim() || 'org_default';
    const userVal = userIdInput.value.trim();
    if (!userVal) return;

    chrome.storage.local.set({ org_id: orgVal, user_id: userVal }, () => {
      saveMsg.textContent = `Saved! Tagged: ${orgVal} / ${userVal}`;
      setTimeout(() => {
        saveMsg.textContent = '';
      }, 3000);
    });
  });

  // Telemetry Pause/Resume Toggle
  const btnToggle = document.getElementById('btn-toggle-telemetry');
  const telemetryBadge = document.getElementById('telemetry-status');

  function updateTelemetryUI(isPaused) {
    if (isPaused) {
      telemetryBadge.textContent = 'Paused';
      telemetryBadge.className = 'status-badge offline';
      btnToggle.textContent = '▶️ Resume Telemetry';
      btnToggle.style.background = '#065f46';
      btnToggle.style.borderColor = '#10b981';
    } else {
      telemetryBadge.textContent = 'Active';
      telemetryBadge.className = 'status-badge online';
      btnToggle.textContent = '⏸️ Pause Telemetry (Private Mode)';
      btnToggle.style.background = '#312e81';
      btnToggle.style.borderColor = '#4f46e5';
    }
  }

  chrome.storage.local.get(['telemetry_paused'], (res) => {
    updateTelemetryUI(Boolean(res.telemetry_paused));
  });

  btnToggle.addEventListener('click', () => {
    chrome.storage.local.get(['telemetry_paused'], (res) => {
      const nextState = !res.telemetry_paused;
      chrome.storage.local.set({ telemetry_paused: nextState }, () => {
        updateTelemetryUI(nextState);
      });
    });
  });

  // Check backend health
  fetch('https://dead-time-backend.onrender.com/health')
    .then(r => r.json())
    .then(data => {
      if(data.status === 'healthy') {
        statusBadge.textContent = 'Online';
        statusBadge.className = 'status-badge online';
      } else {
        throw new Error('Unhealthy');
      }
    })
    .catch(() => {
      statusBadge.textContent = 'Offline';
      statusBadge.className = 'status-badge offline';
    });

  // Open Next.js Dashboard
  btnDashboard.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://dead-time-b2b.vercel.app/' });
  });
});
