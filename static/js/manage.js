/**
 * CivicAI - Complaint Management and Triage Script
 * Supports multi-field filtering, search, sorting, status updates, and deep link triage.
 */

let currentStatusFilter = 'All';
let searchDebounce = null;

document.addEventListener('DOMContentLoaded', () => {
  setupSidebarToggle();
  setupFilterListeners();
  readUrlParameters();
  fetchComplaints();
});

function setupSidebarToggle() {
  const toggleBtn = document.getElementById('complaintsSidebarToggle');
  const sidebar = document.getElementById('adminSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}

function readUrlParameters() {
  const urlParams = new URLSearchParams(window.location.search);
  const targetId = urlParams.get('id');
  const targetPriority = urlParams.get('priority');
  const targetStatus = urlParams.get('status');

  if (targetPriority) {
    const prioSelect = document.getElementById('filterPriority');
    if (prioSelect) prioSelect.value = targetPriority;
  }

  if (targetStatus) {
    currentStatusFilter = targetStatus;
    const statusBtns = document.querySelectorAll('.status-filter-btn');
    statusBtns.forEach(b => {
      if (b.dataset.status === targetStatus) {
        b.classList.add('active', 'btn-outline');
        b.classList.remove('btn-secondary');
      } else {
        b.classList.remove('active', 'btn-outline');
        b.classList.add('btn-secondary');
      }
    });
  }

  if (targetId) {
    setTimeout(() => {
      openModalByTrackingId(targetId);
    }, 400);
  }
}

function setupFilterListeners() {
  const searchInput = document.getElementById('filterSearch');
  const catSelect = document.getElementById('filterCategory');
  const prioSelect = document.getElementById('filterPriority');
  const sortSelect = document.getElementById('filterSort');

  searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(fetchComplaints, 300);
  });

  catSelect.addEventListener('change', fetchComplaints);
  prioSelect.addEventListener('change', fetchComplaints);
  sortSelect.addEventListener('change', fetchComplaints);

  // Status Filter Buttons
  const statusBtns = document.querySelectorAll('.status-filter-btn');
  statusBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      statusBtns.forEach(b => {
        b.classList.remove('active', 'btn-outline');
        b.classList.add('btn-secondary');
      });
      btn.classList.add('active', 'btn-outline');
      btn.classList.remove('btn-secondary');

      currentStatusFilter = btn.dataset.status;
      fetchComplaints();
    });
  });

  // Triage Form Submission
  const triageForm = document.getElementById('triageActionForm');
  triageForm.addEventListener('submit', handleTriageSubmit);
}

function fetchComplaints() {
  const search = document.getElementById('filterSearch').value.trim();
  const category = document.getElementById('filterCategory').value;
  const priority = document.getElementById('filterPriority').value;
  const sort = document.getElementById('filterSort').value;

  const params = new URLSearchParams({
    status: currentStatusFilter,
    category: category,
    priority: priority,
    search: search,
    sort: sort
  });

  fetch(`/api/admin/complaints?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        renderComplaintsTable(data.complaints);
      }
    })
    .catch(err => {
      console.error('Error fetching complaints:', err);
      showToast('Failed to load complaints.', 'error');
    });
}

function renderComplaintsTable(complaints) {
  const tbody = document.getElementById('complaintsTableBody');
  const emptyState = document.getElementById('tableEmptyState');
  tbody.innerHTML = '';

  if (!complaints || complaints.length === 0) {
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  complaints.forEach(c => {
    const tr = document.createElement('tr');
    if ((c.ai_priority_level || '').toLowerCase() === 'high' || (c.ai_priority_level || '').toLowerCase() === 'critical') {
      tr.classList.add('urgent-highlight');
    }

    const catIcon = getCategoryIcon(c.category);
    const statusBadge = getStatusBadge(c.status);
    const priorityBadge = getPriorityBadge(c.ai_priority_level, c.ai_priority_score);

    tr.innerHTML = `
      <td>
        <span style="font-family: monospace; font-weight: 700; color: var(--teal-primary);">${c.tracking_id}</span>
        <div style="font-size: 0.74rem; color: var(--text-dim);">${formatDate(c.created_at)}</div>
      </td>
      <td>
        <strong style="color: var(--text-main);">${c.citizen_name}</strong>
      </td>
      <td>
        <div style="display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 0.88rem;">
          <i class="fa-solid ${catIcon}" style="color: var(--teal-primary);"></i> ${c.category}
        </div>
        <div style="font-size: 0.78rem; color: var(--text-muted); text-overflow: ellipsis; white-space: nowrap; overflow: hidden; max-width: 220px;">
          ${c.location}
        </div>
      </td>
      <td style="max-width: 300px;">
        <div style="font-size: 0.84rem; color: var(--text-muted); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
          ${c.ai_summary || c.description}
        </div>
      </td>
      <td>${priorityBadge}</td>
      <td>${statusBadge}</td>
      <td style="text-align: right;">
        <button class="btn btn-secondary btn-sm" onclick="openTriageModalById(${c.id})">
          <i class="fa-solid fa-sliders"></i> Triage
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// Open Modal by ID
function openTriageModalById(complaintId) {
  fetch(`/api/admin/complaints/${complaintId}`)
    .then(res => res.json())
    .then(data => {
      if (data.success && data.complaint) {
        populateModal(data.complaint, data.activity_logs, data.duplicate_ref);
      }
    })
    .catch(err => {
      console.error(err);
      showToast('Could not load complaint details.', 'error');
    });
}

function openModalByTrackingId(trackingId) {
  fetch(`/api/complaints/track/${encodeURIComponent(trackingId)}`)
    .then(res => res.json())
    .then(data => {
      if (data.success && data.complaint) {
        populateModal(data.complaint, data.activity_logs, data.duplicate_ref);
      }
    })
    .catch(err => console.error(err));
}

function populateModal(c, logs, dupRef) {
  document.getElementById('triageComplaintId').value = c.id;
  document.getElementById('modalTracking').textContent = c.tracking_id;
  document.getElementById('modalCitizen').textContent = c.citizen_name;
  document.getElementById('modalDate').textContent = formatDate(c.created_at);
  document.getElementById('modalDesc').textContent = c.description;
  document.getElementById('modalLoc').textContent = c.location;
  document.getElementById('modalCat').textContent = c.category;

  const statusBadge = document.getElementById('modalStatusBadge');
  statusBadge.className = `badge badge-status-${c.status.toLowerCase().replace(/\s+/g, '-')}`;
  statusBadge.textContent = c.status;

  const priorityBadge = document.getElementById('modalPriorityBadge');
  priorityBadge.className = `badge badge-priority-${c.ai_priority_level.toLowerCase()}`;
  priorityBadge.textContent = `${c.ai_priority_level} Priority`;

  const aiExplEl = document.getElementById('modalAiExpl');
  if (c.ai_priority_explanation) {
    const lines = c.ai_priority_explanation.split('\n').filter(l => l.trim().length > 0);
    aiExplEl.innerHTML = `<div style="font-weight: 700; color: var(--text-main); margin-bottom: 4px;">Reason:</div><ul style="margin: 4px 0 0 18px; padding: 0; line-height: 1.5;">` + 
      lines.map(l => `<li>${l.replace(/^-\s*/, '')}</li>`).join('') + `</ul>`;
  } else {
    aiExplEl.textContent = 'Standard municipal priority assessment.';
  }

  // Photo
  const photoWrap = document.getElementById('modalPhotoWrap');
  if (c.image_filename) {
    photoWrap.style.display = 'block';
    const imgUrl = `/uploads/${encodeURIComponent(c.image_filename)}`;
    document.getElementById('modalPhoto').src = imgUrl;
    document.getElementById('modalPhotoLink').href = imgUrl;
  } else {
    photoWrap.style.display = 'none';
  }

  // Duplicate Banner
  const dupFlag = document.getElementById('modalDuplicateFlag');
  if (c.ai_duplicate_of && dupRef) {
    dupFlag.style.display = 'block';
    dupFlag.innerHTML = `<i class="fa-solid fa-clone"></i> <strong>Duplicate Warning:</strong> Matches existing ${dupRef.tracking_id}. ${c.ai_duplicate_notes || ''}`;
  } else {
    dupFlag.style.display = 'none';
  }

  // Populate Triage Inputs
  document.getElementById('triageStatusSelect').value = c.status;
  document.getElementById('triageDeptSelect').value = c.assigned_department || 'Department of Public Works & Transport';
  document.getElementById('triageOfficerInput').value = c.assigned_officer && c.assigned_officer !== 'Pending Assignment' ? c.assigned_officer : '';
  document.getElementById('triageNoteInput').value = '';

  // Citizen Track Link
  document.getElementById('modalCitizenTrackLink').href = `/track?id=${encodeURIComponent(c.tracking_id)}`;

  // Logs
  const logList = document.getElementById('modalLogList');
  logList.innerHTML = '';
  if (logs && logs.length > 0) {
    logs.forEach(l => {
      const row = document.createElement('div');
      row.style.cssText = 'padding: 8px 10px; background: rgba(255,255,255,0.03); border-radius: var(--radius-sm); border-left: 2px solid var(--teal-primary);';
      row.innerHTML = `
        <div style="display: flex; justify-content: space-between; font-weight: 600; color: var(--text-main);">
          <span>${l.action}</span>
          <span style="font-size: 0.72rem; color: var(--text-dim);">${formatDate(l.timestamp)}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">${l.details || ''}</div>
        <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 3px;">Actor: <strong style="color: var(--teal-primary);">${l.actor}</strong></div>
      `;
      logList.appendChild(row);
    });
  } else {
    logList.innerHTML = '<span style="color: var(--text-dim);">No prior audit logs recorded.</span>';
  }

  document.getElementById('triageModal').classList.add('show');
}

function closeTriageModal() {
  document.getElementById('triageModal').classList.remove('show');
}

// Close modal on backdrop click
document.getElementById('triageModal').addEventListener('click', (e) => {
  if (e.target.id === 'triageModal') closeTriageModal();
});

// Handle Triage Form Submission
function handleTriageSubmit(e) {
  e.preventDefault();

  const complaintId = document.getElementById('triageComplaintId').value;
  const newStatus = document.getElementById('triageStatusSelect').value;
  const dept = document.getElementById('triageDeptSelect').value;
  const officer = document.getElementById('triageOfficerInput').value.trim();
  const note = document.getElementById('triageNoteInput').value.trim();
  const saveBtn = document.getElementById('saveTriageBtn');

  const executeUpdate = () => {
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving Updates...';

    fetch(`/api/admin/complaints/${complaintId}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: newStatus,
        assigned_department: dept,
        assigned_officer: officer || 'Pending Assignment',
        note: note,
        actor: 'Municipal Control Admin'
      })
    })
    .then(res => res.json())
    .then(data => {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save & Apply Changes';

      if (data.success) {
        showToast('Complaint status updated successfully!', 'success');
        closeTriageModal();
        fetchComplaints();
      } else {
        showToast(data.error || 'Failed to update complaint.', 'error');
      }
    })
    .catch(err => {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save & Apply Changes';
      console.error(err);
      showToast('Network error while updating status.', 'error');
    });
  };

  if (newStatus === 'Resolved' && typeof window.showConfirmDialog === 'function') {
    window.showConfirmDialog({
      title: 'Resolve Grievance?',
      message: 'Are you sure you want to mark this grievance as Resolved? This will finalize the redressal and update citizen tracking.',
      confirmText: 'Resolve Issue',
      confirmColor: 'var(--status-resolved)',
      onConfirm: executeUpdate
    });
  } else {
    executeUpdate();
  }
}
