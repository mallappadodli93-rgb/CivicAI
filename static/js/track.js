/**
 * CivicAI - Complaint Lifecycle Tracking Script
 * Includes real-time status tracker, AI telemetry audit,
 * and high-clarity Google Maps geolocation tracking.
 */

let trackMapInstance = null;
let trackMarkerLayer = null;

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('trackSearchInput');
  const searchBtn = document.getElementById('trackSearchBtn');
  const loadingEl = document.getElementById('trackLoading');
  const notFoundEl = document.getElementById('trackNotFound');
  const resultContainer = document.getElementById('trackResultContainer');

  // Search trigger
  function doSearch() {
    const id = searchInput.value.trim();
    if (!id) {
      showToast('Please enter a Tracking ID to search.', 'error');
      return;
    }
    fetchTrackingData(id);
  }

  searchBtn.addEventListener('click', doSearch);
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doSearch();
  });

  // Auto-search if prefilled from URL
  if (searchInput.value.trim()) {
    fetchTrackingData(searchInput.value.trim());
  }

  function fetchTrackingData(trackingId) {
    loadingEl.style.display = 'block';
    notFoundEl.style.display = 'none';
    resultContainer.style.display = 'none';

    fetch(`/api/complaints/track/${encodeURIComponent(trackingId)}`)
      .then(res => res.json())
      .then(data => {
        loadingEl.style.display = 'none';

        if (!data.success || !data.complaint) {
          notFoundEl.style.display = 'block';
          return;
        }

        renderTrackingView(data.complaint, data.activity_logs, data.duplicate_ref);
      })
      .catch(err => {
        loadingEl.style.display = 'none';
        notFoundEl.style.display = 'block';
        console.error('Track fetch error:', err);
      });
  }

  function renderTrackingView(c, logs, dupRef) {
    resultContainer.style.display = 'block';

    // 1. Header & Badges
    document.getElementById('resTrackingId').textContent = c.tracking_id;
    document.getElementById('resCitizenName').textContent = c.citizen_name;
    document.getElementById('resDate').textContent = formatDate(c.created_at);
    document.getElementById('resDepartment').textContent = c.assigned_department || 'General Administration';
    document.getElementById('resOfficer').textContent = c.assigned_officer ? `Assigned to: ${c.assigned_officer}` : 'Officer Pending';

    const statusBadge = document.getElementById('resStatusBadge');
    statusBadge.className = `badge badge-status-${c.status.toLowerCase().replace(/\s+/g, '-')}`;
    statusBadge.textContent = c.status;

    const priorityBadge = document.getElementById('resPriorityBadge');
    priorityBadge.className = `badge badge-priority-${c.ai_priority_level.toLowerCase()}`;
    priorityBadge.textContent = `${c.ai_priority_level} Priority`;

    // 2. Lifecycle Stepper Update
    updateStepper(c.status);

    // 3. Issue Content
    document.getElementById('resDescription').textContent = c.description;
    document.getElementById('resLocation').textContent = c.location;
    document.getElementById('resCategory').textContent = c.category;

    // Photo Preview
    const photoContainer = document.getElementById('resPhotoContainer');
    if (c.image_filename) {
      photoContainer.style.display = 'block';
      const imgUrl = `/uploads/${encodeURIComponent(c.image_filename)}`;
      document.getElementById('resPhotoImg').src = imgUrl;
      document.getElementById('resPhotoLink').href = imgUrl;
    } else {
      photoContainer.style.display = 'none';
    }

    // 4. AI Diagnostic Telemetry
    document.getElementById('resAiSummary').textContent = `"${c.ai_summary || c.description.substring(0, 150)}"`;
    
    const prioExplEl = document.getElementById('resAiPriorityExpl');
    if (c.ai_priority_explanation) {
      const lines = c.ai_priority_explanation.split('\n').filter(l => l.trim().length > 0);
      prioExplEl.innerHTML = `<div style="font-weight: 700; color: var(--text-main); margin-bottom: 4px;">Reason:</div><ul style="margin: 4px 0 0 16px; padding: 0; line-height: 1.5;">` +
        lines.map(l => `<li>${l.replace(/^-\s*/, '')}</li>`).join('') + `</ul>`;
    } else {
      prioExplEl.textContent = 'Standard municipal maintenance protocol.';
    }

    document.getElementById('resAiPriorityScoreText').textContent = `${c.ai_priority_level} Priority`;
    
    const prioBar = document.getElementById('resAiPriorityBar');
    prioBar.style.width = c.ai_priority_level === 'High' ? '90%' : c.ai_priority_level === 'Medium' ? '55%' : '25%';
    let pColor = 'var(--status-resolved)';
    if (c.ai_priority_level === 'High') pColor = 'var(--priority-critical)';
    else if (c.ai_priority_level === 'Medium') pColor = 'var(--priority-high)';
    else pColor = 'var(--status-resolved)';
    prioBar.style.background = pColor;

    // Duplicate detection display
    const dupBox = document.getElementById('resDuplicateStatus');
    if (c.ai_duplicate_of && dupRef) {
      dupBox.innerHTML = `
        <span style="color: var(--status-under-review); font-weight: 700;">
          <i class="fa-solid fa-triangle-exclamation"></i> Flagged as duplicate of ${dupRef.tracking_id}
        </span>
        <div style="margin-top: 4px; font-size: 0.8rem;">${c.ai_duplicate_notes || 'Matched location and incident context.'}</div>
      `;
    } else {
      dupBox.innerHTML = `
        <span style="color: var(--teal-primary); font-weight: 600;">
          <i class="fa-solid fa-shield-check"></i> Unique Citizen Report
        </span>
        <div style="margin-top: 4px; font-size: 0.8rem;">No prior duplicate incidents detected in this vicinity.</div>
      `;
    }

    // Category verification
    const catDetails = document.getElementById('resAiCategoryDetails');
    const conf = Math.round((c.ai_category_confidence || 0.8) * 100);
    catDetails.innerHTML = `
      Verified as <strong style="color: var(--text-main);">${c.ai_category || c.category}</strong> (${conf}% confidence score).
    `;

    // 5. Audit Log Timeline
    renderTimeline(logs);

    // 6. Resolved Completion Banner
    const resolvedBanner = document.getElementById('resResolvedBanner');
    if (resolvedBanner) {
      if (c.status === 'Resolved') {
        resolvedBanner.style.display = 'flex';
        const resLog = logs ? [...logs].reverse().find(l => l.action.includes('Resolved') || (l.details && l.details.includes('Resolved'))) : null;
        const resText = resLog && resLog.details ? resLog.details : 'Grievance remediated and officially certified by the municipal division.';
        document.getElementById('resResolvedDetails').textContent = resText;
      } else {
        resolvedBanner.style.display = 'none';
      }
    }

    // 7. Google Maps Geolocation & Field Tracking
    renderTrackingMap(c);
  }

  function updateStepper(currentStatus) {
    const steps = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved'];
    const currentIndex = steps.indexOf(currentStatus);

    const stepElements = document.querySelectorAll('#lifecycleStepper .step');
    stepElements.forEach((el, index) => {
      el.classList.remove('completed', 'active', 'resolved');
      if (index < currentIndex) {
        el.classList.add('completed');
      } else if (index === currentIndex) {
        el.classList.add('active');
        if (currentStatus === 'Resolved') {
          el.classList.add('completed', 'resolved');
        }
      }
    });
  }

  function renderTimeline(logs) {
    const list = document.getElementById('resTimelineList');
    list.innerHTML = '';

    if (!logs || logs.length === 0) {
      list.innerHTML = '<p style="color: var(--text-dim); font-size: 0.86rem;">No audit logs recorded yet.</p>';
      return;
    }

    logs.forEach((log, index) => {
      const isLatest = index === logs.length - 1;
      const item = document.createElement('div');
      item.className = `timeline-item ${isLatest ? 'current' : 'completed'}`;

      let icon = 'fa-check';
      const act = (log.action || '').toLowerCase();
      const det = (log.details || '').toLowerCase();

      if (act.includes('submit')) icon = 'fa-file-lines';
      else if (act.includes('ai') || act.includes('triage')) icon = 'fa-brain';
      else if (act.includes('under review') || det.includes('under review')) icon = 'fa-magnifying-glass';
      else if (act.includes('assigned') || act.includes('department') || act.includes('officer') || det.includes('assigned')) icon = 'fa-user-gear';
      else if (act.includes('in progress') || det.includes('in progress') || det.includes('dispatched')) icon = 'fa-screwdriver-wrench';
      else if (act.includes('resolved') || det.includes('resolved') || det.includes('remediated')) icon = 'fa-circle-check';
      else if (act.includes('note') || det.includes('note')) icon = 'fa-comment-dots';

      item.innerHTML = `
        <div class="timeline-marker"><i class="fa-solid ${icon}"></i></div>
        <div class="timeline-header">
          <div class="timeline-title">${log.action}</div>
          <div class="timeline-date">${formatDate(log.timestamp)}</div>
        </div>
        <div class="timeline-desc">${log.details || ''}</div>
        <div style="font-size: 0.76rem; color: var(--text-dim); margin-top: 4px;">Actor: <strong style="color: var(--teal-primary);">${log.actor || 'System'}</strong></div>
      `;
      list.appendChild(item);
    });
  }

  // ========================================================
  // GOOGLE MAPS GEOLOCATION TRACKING ENGINE
  // ========================================================
  function renderTrackingMap(c) {
    const mapEl = document.getElementById('trackMap');
    if (!mapEl) return;

    // Parse coordinates or fallback to metropolitan center
    let lat = parseFloat(c.latitude);
    let lng = parseFloat(c.longitude);
    if (isNaN(lat) || isNaN(lng)) {
      lat = 12.9716;
      lng = 77.5946;
    }

    // Update coordinates badge
    const coordBadge = document.getElementById('trackCoordText');
    if (coordBadge) {
      coordBadge.textContent = `${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E`;
    }

    // Update direct Google Maps link button
    const googleBtn = document.getElementById('trackGoogleMapsBtn');
    if (googleBtn) {
      googleBtn.href = `https://www.google.com/maps?q=${lat},${lng}&ll=${lat},${lng}&z=16`;
    }

    // Initialize Leaflet map with Google Maps tiles if not already created
    if (!trackMapInstance) {
      trackMapInstance = L.map('trackMap', {
        zoomControl: true,
        scrollWheelZoom: true
      }).setView([lat, lng], 16);

      // High-Clarity Google Maps Tile Layers
      const googleStreets = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '&copy; Google Maps'
      });

      const googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '&copy; Google Maps'
      });

      const googleTerrain = L.tileLayer('https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '&copy; Google Maps'
      });

      const osmLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      });

      // Default base layer: Google Streets for clean vector clarity
      googleStreets.addTo(trackMapInstance);

      const baseLayers = {
        "🗺️ Google Streets": googleStreets,
        "🛰️ Google Satellite": googleHybrid,
        "⛰️ Google Terrain": googleTerrain,
        "🌐 OpenStreetMap": osmLayer
      };

      L.control.layers(baseLayers, null, { position: 'topright' }).addTo(trackMapInstance);
      trackMarkerLayer = L.layerGroup().addTo(trackMapInstance);
    } else {
      trackMarkerLayer.clearLayers();
      trackMapInstance.setView([lat, lng], 16);
    }

    const pLevel = (c.ai_priority_level || 'Medium').toLowerCase();
    const catIcon = getCategoryIcon(c.category);

    // Dynamic marker pin with animated pulsing radar
    const customIcon = L.divIcon({
      className: 'track-custom-pin',
      html: `
        <div style="position: relative; width: 34px; height: 34px;">
          <div class="pulse-ring ${pLevel}"></div>
          <div class="marker-pin ${pLevel}" style="width: 34px; height: 34px; font-size: 0.95rem; border-width: 2.5px; border-color: #ffffff; box-shadow: 0 0 16px rgba(0,0,0,0.7);">
            <i class="fa-solid ${catIcon}"></i>
          </div>
        </div>
      `,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
      popupAnchor: [0, -20]
    });

    const marker = L.marker([lat, lng], { icon: customIcon }).addTo(trackMarkerLayer);

    // Municipal rapid response perimeter buffer (250m)
    let ringColor = '#ef4444';
    if (pLevel === 'medium') ringColor = '#f59e0b';
    else if (pLevel === 'low') ringColor = '#10b981';

    L.circle([lat, lng], {
      radius: 250,
      color: ringColor,
      fillColor: ringColor,
      fillOpacity: 0.12,
      weight: 1.5,
      dashArray: '5, 5'
    }).addTo(trackMarkerLayer);

    // Interactive detailed popup
    const popupHtml = `
      <div style="min-width: 210px;">
        <div class="map-popup-header">
          <div class="map-popup-title">${c.tracking_id}</div>
          <span class="badge badge-priority-${pLevel}">${c.ai_priority_level}</span>
        </div>
        <div style="font-size: 0.86rem; font-weight: 700; color: var(--teal-primary); margin: 6px 0 2px;">
          <i class="fa-solid ${catIcon}"></i> ${c.category}
        </div>
        <div class="map-popup-desc" style="font-size: 0.82rem; margin: 4px 0 8px; line-height: 1.4;">
          ${c.ai_summary ? `"${c.ai_summary}"` : c.description.substring(0, 100)}
        </div>
        <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 8px;">
          <i class="fa-solid fa-location-dot" style="color: var(--teal-primary);"></i> ${c.location}
        </div>
        <div style="font-size: 0.75rem; color: var(--text-dim); font-family: monospace; margin-bottom: 8px;">
          GPS: ${lat.toFixed(4)}, ${lng.toFixed(4)}
        </div>
        <a href="https://www.google.com/maps?q=${lat},${lng}&ll=${lat},${lng}&z=16" target="_blank" class="btn btn-primary btn-sm" style="display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; font-size: 0.78rem; padding: 6px 10px; text-decoration: none; border-radius: 6px;">
          <i class="fa-brands fa-google"></i> Open in Google Maps
        </a>
      </div>
    `;

    marker.bindPopup(popupHtml).openPopup();

    // Recalculate container dimensions after visibility toggle
    setTimeout(() => {
      if (trackMapInstance) {
        trackMapInstance.invalidateSize();
        trackMapInstance.setView([lat, lng], 16);
      }
    }, 200);
  }
});

