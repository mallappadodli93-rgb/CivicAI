/**
 * CivicAI - Complaint Submission, Location Picker & Live AI Radar Script
 * Enforces mandatory geolocation capture via interactive map picker or current GPS.
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('complaintForm');
  const descInput = document.getElementById('descriptionInput');
  const locInput = document.getElementById('locationInput');
  const catSelect = document.getElementById('categorySelect');
  const charCount = document.getElementById('charCount');

  // Coordinate Inputs & Status
  const latInput = document.getElementById('latitudeInput');
  const lngInput = document.getElementById('longitudeInput');
  const coordBadge = document.getElementById('coordBadge');
  const useGpsBtn = document.getElementById('useGpsBtn');
  const searchAddressBtn = document.getElementById('searchAddressBtn');

  // AI Live Panel Elements
  const aiEmptyState = document.getElementById('aiEmptyState');
  const aiLiveState = document.getElementById('aiLiveState');
  const aiCategoryName = document.getElementById('aiCategoryName');
  const aiConfidenceScore = document.getElementById('aiConfidenceScore');
  const aiConfidenceBar = document.getElementById('aiConfidenceBar');
  const aiCategoryReason = document.getElementById('aiCategoryReason');
  const aiDepartment = document.getElementById('aiDepartment');
  const aiPriorityBadge = document.getElementById('aiPriorityBadge');
  const aiPriorityScore = document.getElementById('aiPriorityScore');
  const aiPriorityBar = document.getElementById('aiPriorityBar');
  const aiPriorityReason = document.getElementById('aiPriorityReason');
  const aiSummaryText = document.getElementById('aiSummaryText');
  const duplicateAlertBox = document.getElementById('duplicateAlertBox');
  const duplicateAlertText = document.getElementById('duplicateAlertText');

  // File Upload Elements
  const fileDropzone = document.getElementById('fileDropzone');
  const imageInput = document.getElementById('imageInput');
  const filePreview = document.getElementById('filePreview');
  const previewImg = document.getElementById('previewImg');
  const previewName = document.getElementById('previewName');
  const previewSize = document.getElementById('previewSize');
  const removeFileBtn = document.getElementById('removeFileBtn');

  // Modal Elements
  const successModal = document.getElementById('successModal');
  const modalTrackingId = document.getElementById('modalTrackingId');
  const copyTrackBtn = document.getElementById('copyTrackBtn');
  const modalPriority = document.getElementById('modalPriority');
  const modalDepartment = document.getElementById('modalDepartment');
  const modalSummary = document.getElementById('modalSummary');
  const trackLinkBtn = document.getElementById('trackLinkBtn');
  const submitBtn = document.getElementById('submitBtn');

  let debounceTimer = null;
  let pickerMap = null;
  let pickerMarker = null;

  // ==========================================
  // 1. INTERACTIVE LOCATION PICKER MAP
  // ==========================================
  function initPickerMap() {
    const mapContainer = document.getElementById('submitPickerMap');
    if (!mapContainer || pickerMap) return;

    // Default center (Bangalore metropolitan area) with unrestricted panning worldwide
    const defaultLat = 12.9716;
    const defaultLng = 77.5946;

    pickerMap = L.map('submitPickerMap', {
      zoomControl: true,
      scrollWheelZoom: true
    }).setView([defaultLat, defaultLng], 12);

    L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
      maxZoom: 20,
      subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
      attribution: '&copy; Google Maps'
    }).addTo(pickerMap);

    // Map click handler to set location
    pickerMap.on('click', (e) => {
      setPickedCoordinates(e.latlng.lat, e.latlng.lng, true);
    });

    // Check if coordinates were pre-filled (e.g. from query params or browser)
    if (latInput.value && lngInput.value) {
      const pLat = parseFloat(latInput.value);
      const pLng = parseFloat(lngInput.value);
      if (!isNaN(pLat) && !isNaN(pLng)) {
        setPickedCoordinates(pLat, pLng, false);
        pickerMap.setView([pLat, pLng], 15);
      }
    }
  }

  function setPickedCoordinates(lat, lng, shouldReverseGeocode = false) {
    if (lat == null || lng == null || isNaN(lat) || isNaN(lng)) return;

    lat = parseFloat(lat);
    lng = parseFloat(lng);

    latInput.value = lat.toFixed(6);
    lngInput.value = lng.toFixed(6);

    if (coordBadge) {
      coordBadge.style.color = 'var(--teal-primary)';
      coordBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Selected: ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    }

    const pinIcon = L.divIcon({
      className: 'custom-map-marker',
      html: `<div class="marker-pin high" style="box-shadow: 0 0 16px rgba(0, 229, 188, 0.9);"><i class="fa-solid fa-location-dot"></i></div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });

    if (pickerMarker) {
      pickerMarker.setLatLng([lat, lng]);
    } else if (pickerMap) {
      pickerMarker = L.marker([lat, lng], { icon: pinIcon, draggable: true }).addTo(pickerMap);
      pickerMarker.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        setPickedCoordinates(pos.lat, pos.lng, true);
      });
    }

    if (shouldReverseGeocode && (!locInput.value || locInput.value.trim().length === 0 || locInput.value.includes('('))) {
      reverseGeocodeCoordinates(lat, lng);
    }

    triggerAiAnalysis();
  }

  function reverseGeocodeCoordinates(lat, lng) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
      .then(res => res.json())
      .then(data => {
        if (data && data.display_name) {
          locInput.value = data.display_name.split(',').slice(0, 4).join(',').trim();
        } else if (!locInput.value) {
          locInput.value = `Location at (${lat.toFixed(5)}, ${lng.toFixed(5)})`;
        }
      })
      .catch(() => {
        if (!locInput.value) {
          locInput.value = `Selected Point (${lat.toFixed(5)}, ${lng.toFixed(5)})`;
        }
      });
  }

  // Use My Current GPS Location
  if (useGpsBtn) {
    useGpsBtn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        showToast('Geolocation is not supported by your browser.', 'error');
        return;
      }

      useGpsBtn.disabled = true;
      useGpsBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Detecting GPS...';

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          useGpsBtn.disabled = false;
          useGpsBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" style="color: var(--teal-primary);"></i> Use My Current GPS Location';

          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;

          setPickedCoordinates(lat, lng, true);

          if (pickerMap) {
            pickerMap.setView([lat, lng], 16, { animate: true });
          }

          showToast(`GPS Position detected: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, 'success');
        },
        (err) => {
          useGpsBtn.disabled = false;
          useGpsBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" style="color: var(--teal-primary);"></i> Use My Current GPS Location';
          showToast('GPS permission denied or unavailable. Please click on the map to place your pin.', 'error');
        },
        { enableHighAccuracy: true, timeout: 9000, maximumAge: 0 }
      );
    });
  }

  // Search Address on Map
  if (searchAddressBtn) {
    searchAddressBtn.addEventListener('click', () => {
      const query = locInput.value.trim();
      if (!query) {
        showToast('Please type an address or landmark first.', 'error');
        locInput.focus();
        return;
      }

      searchAddressBtn.disabled = true;
      searchAddressBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Searching...';

      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`)
        .then(res => res.json())
        .then(results => {
          searchAddressBtn.disabled = false;
          searchAddressBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass-location"></i> Find Address';

          if (results && results.length > 0) {
            const lat = parseFloat(results[0].lat);
            const lng = parseFloat(results[0].lon);
            setPickedCoordinates(lat, lng, false);
            if (pickerMap) {
              pickerMap.setView([lat, lng], 15, { animate: true });
            }
            showToast('Address located on map!', 'success');
          } else {
            showToast('Address could not be geocoded automatically. Please click directly on the map to place your pin.', 'error');
          }
        })
        .catch(() => {
          searchAddressBtn.disabled = false;
          searchAddressBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass-location"></i> Find Address';
          showToast('Address lookup unavailable. Click on map to set pin.', 'error');
        });
    });
  }

  // Initialize Map
  initPickerMap();

  // ==========================================
  // 2. CHARACTER COUNT & AI RADAR
  // ==========================================
  function triggerAiAnalysis() {
    const text = descInput.value.trim();
    const location = locInput.value.trim();
    const category = catSelect.value;

    charCount.textContent = `${text.length} characters`;

    if (text.length < 10) {
      aiEmptyState.style.display = 'block';
      aiLiveState.style.display = 'none';
      return;
    }

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      fetch('/api/ai/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: text, location: location, category: category })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success' && data.analysis) {
          renderAiPreview(data.analysis);
        }
      })
      .catch(err => {
        console.warn('AI live preview error:', err);
      });
    }, 350);
  }

  descInput.addEventListener('input', triggerAiAnalysis);
  locInput.addEventListener('input', triggerAiAnalysis);
  catSelect.addEventListener('change', triggerAiAnalysis);

  function renderAiPreview(analysis) {
    aiEmptyState.style.display = 'none';
    aiLiveState.style.display = 'block';

    aiCategoryName.textContent = analysis.ai_category;
    const confidencePct = Math.round((analysis.ai_category_confidence || 0.5) * 100);
    aiConfidenceScore.textContent = `${confidencePct}% confidence`;
    aiConfidenceBar.style.width = `${confidencePct}%`;
    aiCategoryReason.textContent = analysis.category_explanation;
    aiDepartment.textContent = analysis.suggested_department;

    const pLevel = analysis.ai_priority_level;
    const pScore = analysis.ai_priority_score;
    aiPriorityScore.textContent = `${pScore} / 100`;
    aiPriorityBar.style.width = `${pScore}%`;

    let pColor = 'var(--status-resolved)';
    if (pLevel === 'High') pColor = 'var(--priority-critical)';
    else if (pLevel === 'Medium') pColor = 'var(--priority-high)';
    else pColor = 'var(--status-resolved)';

    aiPriorityBar.style.background = pColor;
    aiPriorityBadge.className = `badge badge-priority-${pLevel.toLowerCase()}`;
    aiPriorityBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${pLevel} Priority`;
    
    if (analysis.ai_priority_explanation) {
      const lines = analysis.ai_priority_explanation.split('\n').filter(l => l.trim().length > 0);
      aiPriorityReason.innerHTML = `<div style="font-weight: 700; color: var(--text-main); margin-bottom: 4px;">Reason:</div><ul style="margin: 0 0 0 16px; padding: 0; line-height: 1.4;">` +
        lines.map(l => `<li>${l.replace(/^-\s*/, '')}</li>`).join('') + `</ul>`;
    } else {
      aiPriorityReason.textContent = 'Standard municipal maintenance protocol.';
    }

    aiSummaryText.textContent = `"${analysis.ai_summary}"`;

    if (analysis.is_duplicate) {
      duplicateAlertBox.style.display = 'flex';
      duplicateAlertText.textContent = analysis.ai_duplicate_notes;
    } else {
      duplicateAlertBox.style.display = 'none';
    }
  }

  // ==========================================
  // 3. IMAGE UPLOAD HANDLING
  // ==========================================
  imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 16 * 1024 * 1024) {
        showToast('Image size exceeds 16 MB limit.', 'error');
        imageInput.value = '';
        return;
      }
      const reader = new FileReader();
      reader.onload = (event) => {
        previewImg.src = event.target.result;
        previewName.textContent = file.name;
        previewSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
        filePreview.style.display = 'flex';
        fileDropzone.style.display = 'none';
      };
      reader.readAsDataURL(file);
    }
  });

  removeFileBtn.addEventListener('click', () => {
    imageInput.value = '';
    previewImg.src = '';
    filePreview.style.display = 'none';
    fileDropzone.style.display = 'block';
  });

  // ==========================================
  // 4. FORM SUBMISSION WITH COMPULSORY LOCATION
  // ==========================================
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const citizenName = document.getElementById('citizenName').value.trim();
    const location = locInput.value.trim();
    const description = descInput.value.trim();
    const lat = latInput.value.trim();
    const lng = lngInput.value.trim();

    if (!citizenName || !location || !description) {
      showToast('Please fill in citizen name, location address, and description.', 'error');
      return;
    }

    // Compulsory location verification
    if (!lat || !lng || isNaN(parseFloat(lat)) || isNaN(parseFloat(lng))) {
      showToast('Location selection is required! Please click on the map to drop a pin or click "Use My Current GPS Location".', 'error');
      const mapEl = document.getElementById('submitPickerMap');
      if (mapEl) {
        mapEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        mapEl.style.outline = '2px solid var(--priority-critical)';
        setTimeout(() => { mapEl.style.outline = 'none'; }, 3000);
      }
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing & Submitting Grievance...';

    const formData = new FormData(form);

    fetch('/api/complaints/submit', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Complaint';

      if (data.success) {
        modalTrackingId.textContent = data.tracking_id;
        modalPriority.className = `badge badge-priority-${data.analysis.ai_priority_level.toLowerCase()}`;
        modalPriority.textContent = `${data.analysis.ai_priority_level} Priority`;
        modalDepartment.textContent = data.analysis.suggested_department;
        modalSummary.textContent = data.analysis.ai_summary;
        trackLinkBtn.href = `/track?id=${encodeURIComponent(data.tracking_id)}`;

        successModal.classList.add('show');
        showToast('Complaint submitted and pinned successfully!', 'success');
      } else {
        showToast(data.error || 'Failed to submit complaint.', 'error');
      }
    })
    .catch(err => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Complaint';
      showToast('An unexpected network error occurred.', 'error');
      console.error(err);
    });
  });

  // Copy Tracking ID to Clipboard
  copyTrackBtn.addEventListener('click', () => {
    const text = modalTrackingId.textContent.trim();
    navigator.clipboard.writeText(text).then(() => {
      showToast('Tracking ID copied to clipboard!', 'success');
    });
  });
});
