/**
 * CivicAI - Admin Analytics Dashboard & All-Location GIS Engine
 * Tracks and plots all valid complaint locations from SQLite database,
 * with clustering, multi-field filtering, live auto-sync, and location correction.
 */

let statusChartInstance = null;
let priorityChartInstance = null;
let categoryChartInstance = null;

// Leaflet Map & Layer References
let leafletMap = null;
let markersLayer = null;
let hotspotsLayer = null;
let currentMarkersData = [];
let currentHotspotsData = [];

// Dashboard complaints cache for filtering
let dashboardComplaintsCache = [];

// Correction Modal Map
let corrMapInstance = null;
let corrMarkerInstance = null;
let corrSelectedLat = null;
let corrSelectedLng = null;

// Auto-refresh timer
let mapAutoRefreshTimer = null;
let mapSearchDebounce = null;

document.addEventListener('DOMContentLoaded', () => {
  initGISMap();
  setupMapFilters();
  loadDashboardMetrics();
  setupDashboardSidebarToggle();
  setupDashboardTriageForm();
  setupDashboardTableFilters();
  setupThemeChangeListener();
  setupLocationCorrectionModal();

  // Periodic Live Map Updates (every 12 seconds)
  mapAutoRefreshTimer = setInterval(() => {
    loadMapData({ autoFit: false, isSilent: true });
    loadMissingCoordinates();
  }, 12000);
});

function setupDashboardSidebarToggle() {
  const toggleBtn = document.getElementById('adminSidebarToggle');
  const sidebar = document.getElementById('adminSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}

// ==========================================
// THEME REACTIVITY FOR CHARTS
// ==========================================
function getChartTheme() {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  return {
    isLight,
    textColor: isLight ? '#475569' : '#94a3b8',
    gridColor: isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.05)',
    borderColor: isLight ? '#ffffff' : '#0b132b',
    tooltipBg: isLight ? '#ffffff' : '#111d42',
    tooltipTitle: isLight ? '#0f172a' : '#f8fafc',
    tooltipBody: isLight ? '#475569' : '#94a3b8',
    tooltipBorder: isLight ? 'rgba(0, 184, 148, 0.4)' : 'rgba(0, 229, 188, 0.3)'
  };
}

function setupThemeChangeListener() {
  window.addEventListener('civicai_theme_changed', () => {
    const t = getChartTheme();

    if (statusChartInstance) {
      statusChartInstance.data.datasets[0].borderColor = t.borderColor;
      if (statusChartInstance.options.plugins.legend) {
        statusChartInstance.options.plugins.legend.labels.color = t.textColor;
      }
      statusChartInstance.options.plugins.tooltip.backgroundColor = t.tooltipBg;
      statusChartInstance.options.plugins.tooltip.titleColor = t.tooltipTitle;
      statusChartInstance.options.plugins.tooltip.bodyColor = t.tooltipBody;
      statusChartInstance.options.plugins.tooltip.borderColor = t.tooltipBorder;
      statusChartInstance.update();
    }

    if (priorityChartInstance) {
      priorityChartInstance.options.scales.x.ticks.color = t.textColor;
      priorityChartInstance.options.scales.y.ticks.color = t.textColor;
      priorityChartInstance.options.scales.y.grid.color = t.gridColor;
      priorityChartInstance.options.plugins.tooltip.backgroundColor = t.tooltipBg;
      priorityChartInstance.options.plugins.tooltip.titleColor = t.tooltipTitle;
      priorityChartInstance.options.plugins.tooltip.bodyColor = t.tooltipBody;
      priorityChartInstance.options.plugins.tooltip.borderColor = t.tooltipBorder;
      priorityChartInstance.update();
    }

    if (categoryChartInstance) {
      categoryChartInstance.options.scales.x.ticks.color = t.textColor;
      categoryChartInstance.options.scales.x.grid.color = t.gridColor;
      categoryChartInstance.options.scales.y.ticks.color = t.isLight ? '#0f172a' : '#f8fafc';
      categoryChartInstance.options.plugins.tooltip.backgroundColor = t.tooltipBg;
      categoryChartInstance.options.plugins.tooltip.titleColor = t.tooltipTitle;
      categoryChartInstance.options.plugins.tooltip.bodyColor = t.tooltipBody;
      categoryChartInstance.options.plugins.tooltip.borderColor = t.tooltipBorder;
      categoryChartInstance.update();
    }
  });
}

// ==========================================
// ALL-LOCATION LEAFLET.JS GIS MAP & CLUSTERING
// ==========================================

function initGISMap() {
  const mapContainer = document.getElementById('complaintMap');
  if (!mapContainer || leafletMap) return;

  // Initialize map without bounds lock (worldwide support)
  leafletMap = L.map('complaintMap', {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView([12.965, 77.625], 12);

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

  const cartoLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '&copy; CartoDB'
  });

  googleStreets.addTo(leafletMap);

  const baseLayers = {
    "🗺️ Google Streets": googleStreets,
    "🛰️ Google Satellite": googleHybrid,
    "⛰️ Google Terrain": googleTerrain,
    "🌐 OpenStreetMap": osmLayer,
    "🏙️ Carto Voyager": cartoLayer
  };

  L.control.layers(baseLayers, null, { position: 'topright' }).addTo(leafletMap);

  // Marker Clustering support if available, with graceful fallback
  if (typeof L.markerClusterGroup === 'function') {
    markersLayer = L.markerClusterGroup({
      showCoverageOnHover: false,
      maxClusterRadius: 45,
      spiderfyOnMaxZoom: true,
      disableClusteringAtZoom: 17
    });
  } else {
    markersLayer = L.layerGroup();
  }

  leafletMap.addLayer(markersLayer);
  hotspotsLayer = L.layerGroup().addTo(leafletMap);

  loadMapData({ autoFit: true });
  loadMissingCoordinates();
}

function setupMapFilters() {
  const catFilter = document.getElementById('mapCategoryFilter');
  const prioFilter = document.getElementById('mapPriorityFilter');
  const statusFilter = document.getElementById('mapStatusFilter');
  const sourceFilter = document.getElementById('mapSourceFilter');
  const searchInput = document.getElementById('mapSearchInput');
  const resetBtn = document.getElementById('mapResetFiltersBtn');
  const refreshBtn = document.getElementById('mapRefreshBtn');
  const centerBtn = document.getElementById('mapCenterBtn');

  const onFilterChange = () => loadMapData({ autoFit: true });

  if (catFilter) catFilter.addEventListener('change', onFilterChange);
  if (prioFilter) prioFilter.addEventListener('change', onFilterChange);
  if (statusFilter) statusFilter.addEventListener('change', onFilterChange);
  if (sourceFilter) sourceFilter.addEventListener('change', onFilterChange);

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(mapSearchDebounce);
      mapSearchDebounce = setTimeout(() => {
        loadMapData({ autoFit: true });
      }, 350);
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (catFilter) catFilter.value = 'All';
      if (prioFilter) prioFilter.value = 'All';
      if (statusFilter) statusFilter.value = 'All';
      if (sourceFilter) sourceFilter.value = 'All';
      if (searchInput) searchInput.value = '';
      loadMapData({ autoFit: true });
      showToast('Map filters reset to show all locations.', 'success');
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      refreshBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing...';
      loadMapData({ autoFit: false });
      loadMissingCoordinates();
      setTimeout(() => {
        refreshBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Refresh Map';
        showToast('Map locations refreshed from database.', 'success');
      }, 500);
    });
  }

  if (centerBtn) {
    centerBtn.addEventListener('click', resetMapView);
  }
}

function loadMapData(options = {}) {
  const { autoFit = false, isSilent = false } = options;

  const catFilter = document.getElementById('mapCategoryFilter');
  const prioFilter = document.getElementById('mapPriorityFilter');
  const statusFilter = document.getElementById('mapStatusFilter');
  const sourceFilter = document.getElementById('mapSourceFilter');
  const searchInput = document.getElementById('mapSearchInput');

  const category = catFilter ? catFilter.value : 'All';
  const priority = prioFilter ? prioFilter.value : 'All';
  const status = statusFilter ? statusFilter.value : 'All';
  const source = sourceFilter ? sourceFilter.value : 'All';
  const search = searchInput ? searchInput.value.trim() : '';

  const compParams = new URLSearchParams();
  if (category && category !== 'All') compParams.append('category', category);
  if (priority && priority !== 'All') compParams.append('priority', priority);
  if (status && status !== 'All') compParams.append('status', status);
  if (source && source !== 'All') compParams.append('source', source);
  if (search) compParams.append('search', search);

  const hotParams = new URLSearchParams();
  if (category && category !== 'All') hotParams.append('category', category);

  Promise.all([
    fetch(`/api/map/complaints?${compParams.toString()}`).then(r => r.json()),
    fetch(`/api/map/hotspots?${hotParams.toString()}`).then(r => r.json())
  ])
  .then(([compData, hotData]) => {
    if (compData.success) {
      currentMarkersData = compData.complaints || [];
      renderMapMarkers(currentMarkersData, autoFit);

      const counterBadge = document.getElementById('mapCounterBadge');
      if (counterBadge) {
        counterBadge.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${currentMarkersData.length} Locations Plotted`;
      }
    }
    if (hotData.success) {
      currentHotspotsData = hotData.hotspots || [];
      renderHotspotZones(currentHotspotsData);
      renderHotspotPanel(currentHotspotsData);
    }
  })
  .catch(err => {
    if (!isSilent) {
      console.error('Error fetching map data:', err);
      showToast('Could not load map locations from database.', 'error');
    }
  });
}

function renderMapMarkers(complaints, autoFit = false) {
  if (!markersLayer || !leafletMap) return;
  markersLayer.clearLayers();

  const validPoints = [];

  complaints.forEach(c => {
    if (c.latitude == null || c.longitude == null) return;

    const lat = parseFloat(c.latitude);
    const lng = parseFloat(c.longitude);
    if (isNaN(lat) || isNaN(lng)) return;

    validPoints.push([lat, lng]);

    const pLevel = (c.ai_priority_level || 'Medium').toLowerCase();
    const catIcon = getCategoryIcon(c.category);
    const statusBadge = getStatusBadge(c.status);
    const priorityBadge = getPriorityBadge(c.ai_priority_level, c.ai_priority_score);

    const isSynthetic = c.is_synthetic === 1 || (c.tracking_id && c.tracking_id.includes('SYN'));
    const sourceBadge = isSynthetic
      ? `<span class="badge badge-secondary" style="font-size: 0.68rem; padding: 2px 7px;"><i class="fa-solid fa-flask"></i> Demonstration Data</span>`
      : `<span class="badge badge-primary" style="font-size: 0.68rem; padding: 2px 7px;"><i class="fa-solid fa-user-check"></i> Citizen Report</span>`;

    const customIcon = L.divIcon({
      className: 'custom-map-marker',
      html: `<div class="marker-pin ${pLevel}" title="${c.tracking_id} - ${c.category}"><i class="fa-solid ${catIcon}"></i></div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    const marker = L.marker([lat, lng], { icon: customIcon });

    const popupContent = `
      <div style="font-family: var(--font-family); min-width: 270px; max-width: 320px; padding: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
          <span style="font-family: monospace; font-weight: 800; color: var(--teal-primary); font-size: 0.9rem;">
            ${escapeHTML(c.tracking_id)}
          </span>
          ${statusBadge}
        </div>

        <div style="margin-bottom: 8px;">
          ${sourceBadge}
        </div>

        <div style="display: grid; grid-template-columns: auto 1fr; gap: 4px 8px; font-size: 0.8rem; margin-bottom: 8px; background: rgba(255,255,255,0.03); padding: 8px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
          <strong style="color: var(--text-dim);">Category:</strong>
          <span style="color: var(--text-main); font-weight: 600;"><i class="fa-solid ${catIcon}" style="color: var(--teal-primary);"></i> ${escapeHTML(c.category)}</span>

          <strong style="color: var(--text-dim);">Address:</strong>
          <span style="color: var(--text-main);">${escapeHTML(c.location)}</span>

          <strong style="color: var(--text-dim);">Coordinates:</strong>
          <code style="color: var(--teal-primary); font-size: 0.76rem;">${lat.toFixed(6)}, ${lng.toFixed(6)}</code>

          <strong style="color: var(--text-dim);">Priority:</strong>
          <span>${priorityBadge}</span>

          <strong style="color: var(--text-dim);">Date:</strong>
          <span style="color: var(--text-muted);">${formatDate(c.created_at)}</span>
        </div>

        <div style="font-size: 0.78rem; color: var(--text-main); margin-bottom: 10px; line-height: 1.4; max-height: 60px; overflow-y: auto;">
          ${escapeHTML(c.ai_summary || c.description)}
        </div>

        <div style="display: flex; gap: 8px; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
          <button class="btn btn-primary btn-sm" onclick="openDashboardTriageModal(${c.id})" style="flex: 1; justify-content: center; font-size: 0.74rem;">
            <i class="fa-solid fa-sliders"></i> Triage Complaint
          </button>
          <a href="/track?id=${encodeURIComponent(c.tracking_id)}" target="_blank" class="btn btn-secondary btn-sm" style="font-size: 0.74rem;" title="Open Citizen Tracker">
            <i class="fa-solid fa-crosshairs"></i> Track
          </a>
        </div>
      </div>
    `;

    marker.bindPopup(popupContent);
    markersLayer.addLayer(marker);
  });

  // Automatically adjust bounds to fit all plotted complaint locations
  if (autoFit && validPoints.length > 0) {
    if (validPoints.length === 1) {
      leafletMap.setView(validPoints[0], 15, { animate: true });
    } else {
      const bounds = L.latLngBounds(validPoints);
      leafletMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
    }
  }
}

function renderHotspotZones(hotspots) {
  if (!hotspotsLayer || !leafletMap) return;
  hotspotsLayer.clearLayers();

  hotspots.forEach(h => {
    const sev = (h.severity || 'Medium').toLowerCase();
    let fillColor = 'rgba(234, 179, 8, 0.22)';
    let strokeColor = '#eab308';

    if (sev === 'high' || sev === 'critical') {
      fillColor = 'rgba(239, 68, 68, 0.25)';
      strokeColor = '#ef4444';
    }

    const circle = L.circle([h.center_lat, h.center_lng], {
      radius: h.radius_meters || 850,
      color: strokeColor,
      weight: 2,
      dashArray: '5, 5',
      fillColor: fillColor,
      fillOpacity: 0.35
    });

    const popupHtml = `
      <div style="font-family: var(--font-family); min-width: 240px; padding: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
          <strong style="color: ${strokeColor}; font-size: 0.95rem;"><i class="fa-solid fa-fire"></i> ${escapeHTML(h.name)}</strong>
          <span class="badge badge-priority-${sev}">${h.severity}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-main); margin-bottom: 6px;">
          <strong>${h.complaint_count} Complaints Clustered</strong> (${escapeHTML(h.dominant_category)})
        </div>
        <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0; line-height: 1.4;">${escapeHTML(h.summary)}</p>
      </div>
    `;

    circle.bindPopup(popupHtml);
    hotspotsLayer.addLayer(circle);
  });
}

function renderHotspotPanel(hotspots) {
  const container = document.getElementById('hotspotCardsContainer');
  const counter = document.getElementById('hotspotCounterBadge');
  if (!container) return;

  container.innerHTML = '';
  if (counter) counter.textContent = `${hotspots.length} Clusters`;

  if (!hotspots || hotspots.length === 0) {
    container.innerHTML = `
      <div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 0.82rem;">
        <i class="fa-solid fa-circle-check" style="color: var(--status-resolved); font-size: 1.5rem; margin-bottom: 6px; display: block;"></i>
        No active geographical complaint hotspots detected.
      </div>
    `;
    return;
  }

  hotspots.forEach(h => {
    const card = document.createElement('div');
    card.className = 'hotspot-card';
    card.style.cssText = `
      padding: 12px 14px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      transition: var(--transition);
      cursor: pointer;
    `;

    const catIcon = getCategoryIcon(h.dominant_category);

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
        <strong style="font-size: 0.88rem; color: var(--text-main);">${escapeHTML(h.name)}</strong>
        <span class="badge badge-priority-${(h.severity || 'medium').toLowerCase()}" style="font-size: 0.68rem; padding: 2px 7px;">
          ${h.severity} Alert
        </span>
      </div>
      <div style="font-size: 0.8rem; color: var(--teal-primary); font-weight: 600; margin-bottom: 4px;">
        <i class="fa-solid ${catIcon}"></i> ${escapeHTML(h.dominant_category)} (${h.complaint_count} reports)
      </div>
      <div style="font-size: 0.74rem; color: var(--text-muted); margin-bottom: 8px; line-height: 1.4;">
        ${escapeHTML(h.summary)}
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-subtle); padding-top: 6px;">
        <span style="font-size: 0.7rem; color: var(--text-dim);">Radius: ~${h.radius_meters}m</span>
        <button class="btn btn-outline btn-sm" style="font-size: 0.72rem; padding: 3px 8px;" onclick="flyToHotspot(${h.center_lat}, ${h.center_lng}, ${h.radius_meters})">
          <i class="fa-solid fa-location-crosshairs"></i> Focus
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

function flyToHotspot(lat, lng, radius) {
  if (!leafletMap) return;
  leafletMap.flyTo([lat, lng], 15, {
    animate: true,
    duration: 1.2
  });
}

function resetMapView() {
  if (!leafletMap) return;
  if (currentMarkersData.length > 0) {
    const valid = currentMarkersData
      .filter(c => c.latitude != null && c.longitude != null)
      .map(c => [parseFloat(c.latitude), parseFloat(c.longitude)]);

    if (valid.length === 1) {
      leafletMap.setView(valid[0], 15, { animate: true });
    } else if (valid.length > 1) {
      const bounds = L.latLngBounds(valid);
      leafletMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
    }
  } else {
    leafletMap.setView([12.965, 77.625], 12);
  }
}

// ==========================================
// COMPLAINTS MISSING COORDINATES HANDLER
// ==========================================
function loadMissingCoordinates() {
  fetch('/api/map/missing-coordinates')
    .then(res => res.json())
    .then(data => {
      const card = document.getElementById('missingCoordinatesCard');
      const countEl = document.getElementById('missingCoordsCount');
      const listEl = document.getElementById('missingCoordsList');
      if (!card || !listEl) return;

      if (data.success && data.complaints && data.complaints.length > 0) {
        card.style.display = 'block';
        if (countEl) countEl.textContent = data.complaints.length;

        listEl.innerHTML = data.complaints.map(c => `
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); font-size: 0.82rem; gap: 10px;">
            <div>
              <span style="font-family: monospace; font-weight: 700; color: var(--teal-primary);">${c.tracking_id}</span>
              &bull; <strong style="color: var(--text-main);">${escapeHTML(c.citizen_name)}</strong>
              &bull; <span style="color: var(--text-muted);">${escapeHTML(c.location || 'No address text')}</span>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="openLocationCorrectionModal(${c.id}, '${escapeHTML(c.tracking_id)}', '${escapeHTML(c.location || '')}')">
              <i class="fa-solid fa-map-pin"></i> Set Location
            </button>
          </div>
        `).join('');
      } else {
        card.style.display = 'none';
      }
    })
    .catch(() => {});
}

function setupLocationCorrectionModal() {
  const saveBtn = document.getElementById('corrSaveBtn');
  const geocodeBtn = document.getElementById('corrGeocodeBtn');

  if (geocodeBtn) {
    geocodeBtn.addEventListener('click', () => {
      const query = document.getElementById('corrAddressInput').value.trim();
      if (!query) return;

      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`)
        .then(r => r.json())
        .then(res => {
          if (res && res.length > 0) {
            const lat = parseFloat(res[0].lat);
            const lng = parseFloat(res[0].lon);
            setCorrModalPoint(lat, lng);
            if (corrMapInstance) corrMapInstance.setView([lat, lng], 15);
          } else {
            showToast('Could not geocode automatically. Please click directly on the map.', 'error');
          }
        });
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      const compId = document.getElementById('corrComplaintId').value;
      const address = document.getElementById('corrAddressInput').value.trim();

      if (!corrSelectedLat || !corrSelectedLng) {
        showToast('Please click on the map to set a location pin.', 'error');
        return;
      }

      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

      fetch(`/api/complaints/${compId}/update-location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: corrSelectedLat,
          longitude: corrSelectedLng,
          location: address
        })
      })
      .then(res => res.json())
      .then(data => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Save Coordinates & Show on Map';

        if (data.success) {
          showToast(data.message || 'Location updated!', 'success');
          closeLocationCorrectionModal();
          loadMapData({ autoFit: true });
          loadMissingCoordinates();
          loadDashboardMetrics();
        } else {
          showToast(data.error || 'Failed to update location.', 'error');
        }
      })
      .catch(() => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Save Coordinates & Show on Map';
        showToast('Network error updating coordinates.', 'error');
      });
    });
  }
}

function openLocationCorrectionModal(id, trackingId, address) {
  document.getElementById('corrComplaintId').value = id;
  document.getElementById('corrModalTrackingId').textContent = trackingId;
  document.getElementById('corrModalAddressText').textContent = address || 'None';
  document.getElementById('corrAddressInput').value = address || '';
  document.getElementById('corrCoordStatus').textContent = 'Click map to place pin';
  document.getElementById('corrCoordStatus').style.color = 'var(--priority-critical)';

  corrSelectedLat = null;
  corrSelectedLng = null;

  document.getElementById('locationCorrectionModal').classList.add('show');

  setTimeout(() => {
    if (!corrMapInstance) {
      corrMapInstance = L.map('corrPickerMap').setView([12.9716, 77.5946], 12);
      L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
      }).addTo(corrMapInstance);

      corrMapInstance.on('click', (e) => {
        setCorrModalPoint(e.latlng.lat, e.latlng.lng);
      });
    } else {
      corrMapInstance.invalidateSize();
    }
  }, 200);
}

function setCorrModalPoint(lat, lng) {
  corrSelectedLat = lat;
  corrSelectedLng = lng;

  const statusEl = document.getElementById('corrCoordStatus');
  if (statusEl) {
    statusEl.textContent = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    statusEl.style.color = 'var(--teal-primary)';
  }

  const pinIcon = L.divIcon({
    className: 'custom-map-marker',
    html: `<div class="marker-pin high"><i class="fa-solid fa-location-dot"></i></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });

  if (corrMarkerInstance) {
    corrMarkerInstance.setLatLng([lat, lng]);
  } else if (corrMapInstance) {
    corrMarkerInstance = L.marker([lat, lng], { icon: pinIcon, draggable: true }).addTo(corrMapInstance);
    corrMarkerInstance.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      setCorrModalPoint(pos.lat, pos.lng);
    });
  }
}

function closeLocationCorrectionModal() {
  document.getElementById('locationCorrectionModal').classList.remove('show');
}

// ==========================================
// DASHBOARD METRICS & CHARTS
// ==========================================

function loadDashboardMetrics() {
  fetch('/api/admin/metrics')
    .then(res => res.json())
    .then(data => {
      document.getElementById('kpiTotal').textContent = data.total;
      document.getElementById('kpiPending').textContent = data.pending;
      document.getElementById('kpiResolved').textContent = data.resolved;
      document.getElementById('kpiUrgent').textContent = data.urgent;

      renderStatusChart(data.status_distribution);
      renderPriorityChart(data.priority_distribution);
      renderCategoryChart(data.category_distribution);
      renderActivityFeed(data.recent_activity);

      if (data.recent_complaints) {
        dashboardComplaintsCache = data.recent_complaints;
        filterAndRenderDashboardTable();
      }
    })
    .catch(err => {
      console.error('Error fetching admin metrics:', err);
    });
}

function renderStatusChart(statusDist) {
  const ctx = document.getElementById('statusChart').getContext('2d');
  if (statusChartInstance) statusChartInstance.destroy();

  const t = getChartTheme();
  const labels = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved'];
  const values = labels.map(label => statusDist[label] || 0);

  statusChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: [
          '#38bdf8', // Submitted
          '#f59e0b', // Under Review
          '#a855f7', // Assigned
          '#00e5bc', // In Progress
          '#10b981'  // Resolved
        ],
        borderWidth: 2,
        borderColor: t.borderColor
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: t.textColor,
            font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 },
            boxWidth: 12,
            padding: 14
          }
        },
        tooltip: {
          backgroundColor: t.tooltipBg,
          borderColor: t.tooltipBorder,
          borderWidth: 1,
          titleColor: t.tooltipTitle,
          bodyColor: t.tooltipBody,
          padding: 10
        }
      },
      cutout: '68%'
    }
  });
}

function renderPriorityChart(prioDist) {
  const ctx = document.getElementById('priorityChart').getContext('2d');
  if (priorityChartInstance) priorityChartInstance.destroy();

  const t = getChartTheme();
  const labels = ['High', 'Medium', 'Low'];
  const values = labels.map(label => prioDist[label] || 0);

  priorityChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Grievances by Priority',
        data: values,
        backgroundColor: [
          'rgba(239, 68, 68, 0.88)',   // High
          'rgba(234, 179, 8, 0.88)',   // Medium
          'rgba(16, 185, 129, 0.88)'   // Low
        ],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: t.tooltipBg,
          borderColor: t.tooltipBorder,
          borderWidth: 1,
          titleColor: t.tooltipTitle,
          bodyColor: t.tooltipBody
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: t.textColor, font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 } }
        },
        y: {
          beginAtZero: true,
          grid: { color: t.gridColor },
          ticks: { color: t.textColor, stepSize: 1, font: { family: 'Plus Jakarta Sans' } }
        }
      }
    }
  });
}

function renderCategoryChart(catDist) {
  const ctx = document.getElementById('categoryChart').getContext('2d');
  if (categoryChartInstance) categoryChartInstance.destroy();

  const t = getChartTheme();
  const labels = catDist.map(c => c.category);
  const values = catDist.map(c => c.count);

  categoryChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Complaints',
        data: values,
        backgroundColor: '#00e5bc',
        borderRadius: 8,
        hoverBackgroundColor: '#02fad0'
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: t.tooltipBg,
          borderColor: t.tooltipBorder,
          borderWidth: 1,
          titleColor: t.tooltipTitle,
          bodyColor: t.tooltipBody
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: t.gridColor },
          ticks: { color: t.textColor, stepSize: 1, font: { family: 'Plus Jakarta Sans' } }
        },
        y: {
          grid: { display: false },
          ticks: { color: t.isLight ? '#0f172a' : '#f8fafc', font: { family: 'Plus Jakarta Sans', size: 11, weight: 600 } }
        }
      }
    }
  });
}

function renderActivityFeed(activities) {
  const container = document.getElementById('liveActivityFeed');
  if (!container) return;
  container.innerHTML = '';

  if (!activities || activities.length === 0) {
    container.innerHTML = '<p style="color: var(--text-dim); font-size: 0.85rem; padding: 12px;">No recent activities logged.</p>';
    return;
  }

  activities.forEach(item => {
    const row = document.createElement('div');
    row.style.cssText = `
      padding: 10px 12px;
      background: var(--bg-surface-elevated);
      border-radius: var(--radius-sm);
      border-left: 3px solid var(--teal-primary);
      display: flex;
      flex-direction: column;
      gap: 3px;
      transition: var(--transition);
    `;

    row.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: baseline; font-size: 0.84rem;">
        <strong style="color: var(--text-main);">${escapeHTML(item.action)}</strong>
        <span style="font-size: 0.72rem; color: var(--text-dim);">${formatDate(item.timestamp)}</span>
      </div>
      <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4;">${escapeHTML(item.details || '')}</div>
      <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: var(--text-dim); margin-top: 2px;">
        <span><i class="fa-solid fa-hashtag"></i> <a href="/admin/complaints?id=${item.tracking_id}" style="color: var(--teal-primary); text-decoration: none; font-weight: 600;">${item.tracking_id}</a></span>
        <span>By: <strong style="color: var(--text-muted);">${escapeHTML(item.actor)}</strong></span>
      </div>
    `;

    container.appendChild(row);
  });
}

// ==========================================
// INTERACTIVE TABLE SEARCH & FILTERS
// ==========================================
function setupDashboardTableFilters() {
  const searchInput = document.getElementById('dashTableSearch');
  const prioSelect = document.getElementById('dashTablePriorityFilter');
  const statusSelect = document.getElementById('dashTableStatusFilter');
  const resetBtn = document.getElementById('dashTableResetBtn');

  if (searchInput) searchInput.addEventListener('input', filterAndRenderDashboardTable);
  if (prioSelect) prioSelect.addEventListener('change', filterAndRenderDashboardTable);
  if (statusSelect) statusSelect.addEventListener('change', filterAndRenderDashboardTable);
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (prioSelect) prioSelect.value = 'All';
      if (statusSelect) statusSelect.value = 'All';
      filterAndRenderDashboardTable();
    });
  }
}

function filterAndRenderDashboardTable() {
  const tbody = document.getElementById('dashboardTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const searchInput = document.getElementById('dashTableSearch');
  const prioSelect = document.getElementById('dashTablePriorityFilter');
  const statusSelect = document.getElementById('dashTableStatusFilter');

  const search = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const prio = prioSelect ? prioSelect.value : 'All';
  const status = statusSelect ? statusSelect.value : 'All';

  const filtered = dashboardComplaintsCache.filter(c => {
    if (prio !== 'All' && (c.ai_priority_level || '').toLowerCase() !== prio.toLowerCase()) return false;
    if (status !== 'All' && (c.status || '').toLowerCase() !== status.toLowerCase()) return false;
    if (search) {
      const matchTrack = (c.tracking_id || '').toLowerCase().includes(search);
      const matchName = (c.citizen_name || '').toLowerCase().includes(search);
      const matchLoc = (c.location || '').toLowerCase().includes(search);
      const matchCat = (c.category || '').toLowerCase().includes(search);
      if (!matchTrack && !matchName && !matchLoc && !matchCat) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td colspan="7" style="text-align: center; padding: 36px 16px; color: var(--text-muted);">
        <i class="fa-solid fa-filter-circle-xmark" style="font-size: 1.8rem; color: var(--text-dim); margin-bottom: 8px; display: block;"></i>
        No complaints match your current search or filter criteria.
      </td>
    `;
    tbody.appendChild(tr);
    return;
  }

  filtered.forEach(c => {
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
      <td><strong style="color: var(--text-main);">${escapeHTML(c.citizen_name)}</strong></td>
      <td>
        <span style="display: flex; align-items: center; gap: 6px; font-weight: 600;">
          <i class="fa-solid ${catIcon}" style="color: var(--teal-primary);"></i> ${escapeHTML(c.category)}
        </span>
      </td>
      <td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-muted);">
        ${escapeHTML(c.location)}
      </td>
      <td>${priorityBadge}</td>
      <td>${statusBadge}</td>
      <td style="text-align: right;">
        <button class="btn btn-secondary btn-sm" onclick="openDashboardTriageModal(${c.id})">
          <i class="fa-solid fa-sliders"></i> Triage
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openDashboardTriageModal(complaintId) {
  fetch(`/api/admin/complaints/${complaintId}`)
    .then(res => res.json())
    .then(data => {
      if (data.success && data.complaint) {
        const c = data.complaint;
        document.getElementById('dashTriageId').value = c.id;
        document.getElementById('dashModalTracking').textContent = c.tracking_id;
        document.getElementById('dashModalCitizen').textContent = c.citizen_name;
        document.getElementById('dashModalDesc').textContent = c.description;

        const statusBadge = document.getElementById('dashModalStatusBadge');
        statusBadge.className = `badge badge-status-${c.status.toLowerCase().replace(/\s+/g, '-')}`;
        statusBadge.textContent = c.status;

        const prioBadge = document.getElementById('dashModalPriorityBadge');
        prioBadge.className = `badge badge-priority-${c.ai_priority_level.toLowerCase()}`;
        prioBadge.textContent = `${c.ai_priority_level} Priority`;

        const explEl = document.getElementById('dashModalAiExpl');
        if (c.ai_priority_explanation) {
          const lines = c.ai_priority_explanation.split('\n').filter(l => l.trim().length > 0);
          explEl.innerHTML = `<div style="font-weight: 700; color: var(--text-main); margin-bottom: 4px;">Reason:</div><ul style="margin: 4px 0 0 18px; padding: 0; line-height: 1.5;">` + 
            lines.map(l => `<li>${escapeHTML(l.replace(/^-\s*/, ''))}</li>`).join('') + `</ul>`;
        } else {
          explEl.textContent = 'Standard triage applied.';
        }

        document.getElementById('dashStatusSelect').value = c.status;
        document.getElementById('dashDeptSelect').value = c.assigned_department || 'Department of Roads & Infrastructure';
        document.getElementById('dashOfficerInput').value = c.assigned_officer && c.assigned_officer !== 'Pending Assignment' ? c.assigned_officer : '';
        document.getElementById('dashNoteInput').value = '';
        document.getElementById('dashModalCitizenTrackLink').href = `/track?id=${encodeURIComponent(c.tracking_id)}`;

        document.getElementById('dashboardTriageModal').classList.add('show');
      }
    })
    .catch(err => console.error(err));
}

function closeDashboardTriageModal() {
  document.getElementById('dashboardTriageModal').classList.remove('show');
}

function setupDashboardTriageForm() {
  const form = document.getElementById('dashTriageForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const id = document.getElementById('dashTriageId').value;
    const newStatus = document.getElementById('dashStatusSelect').value;
    const dept = document.getElementById('dashDeptSelect').value;
    const officer = document.getElementById('dashOfficerInput').value.trim();
    const note = document.getElementById('dashNoteInput').value.trim();
    const saveBtn = document.getElementById('dashSaveBtn');

    const executeUpdate = () => {
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

      fetch(`/api/admin/complaints/${id}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          assigned_department: dept,
          assigned_officer: officer || 'Pending Assignment',
          note: note,
          actor: 'Dashboard Admin'
        })
      })
      .then(res => res.json())
      .then(data => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Apply Triage';

        if (data.success) {
          showToast('Complaint status updated successfully!', 'success');
          closeDashboardTriageModal();
          loadDashboardMetrics();
          loadMapData({ autoFit: false });
        } else {
          showToast(data.error || 'Failed to update.', 'error');
        }
      })
      .catch(err => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Apply Triage';
        showToast('Error saving updates.', 'error');
      });
    };

    if (newStatus === 'Resolved' && typeof window.showConfirmDialog === 'function') {
      window.showConfirmDialog({
        title: 'Resolve Grievance?',
        message: 'Are you sure you want to resolve this complaint? This marks the issue resolved in the database and updates citizen tracking.',
        confirmText: 'Resolve Grievance',
        confirmColor: 'var(--status-resolved)',
        onConfirm: executeUpdate
      });
    } else {
      executeUpdate();
    }
  });
}
