/**
 * CivicAI - Global Frontend Utility Script
 * Handles Theme Toggling (Dark/Light), Kannada/English i18n, Real-Time Notifications,
 * Confirmation Dialogs, Mobile Navigation Drawer, Back-To-Top, and UI Helpers.
 */

// ==========================================
// 1. BILINGUAL DICTIONARY (English & ಕನ್ನಡ)
// ==========================================
const I18N_TRANSLATIONS = {
  en: {
    badge_ai_active: "AI Active",
    nav_home: "Home",
    nav_report: "Report a Problem",
    nav_track: "Track Status",
    nav_dashboard: "Admin Dashboard",
    nav_manage: "Manage",
    nav_settings: "Settings",
    btn_report_problem: "Report a Problem",
    admin_portals: "Admin Portals",

    // Notifications
    notif_title: "Civic Notifications",
    notif_mark_read: "Mark read",
    notif_view_all: "View all municipal complaints",

    // Home Page Hero
    hero_badge: "AI-Powered Grievance Redressal",
    hero_title_1: "Smart Citizen Grievance",
    hero_title_2: "Resolution Platform",
    hero_subtitle: "Empowering citizens and municipal administrators with transparent NLP categorization, instant duplicate detection, and geographic hotspot intelligence.",
    hero_btn_report: "File a Complaint",
    hero_btn_track: "Track Grievance",
    hero_btn_admin: "Admin Console",

    // Stats
    stat_total: "Total Grievances",
    stat_urgent: "High Risk Alerts",
    stat_in_progress: "In Progress",
    stat_resolved: "Resolved Cases",

    // Categories
    cat_road: "Road Damage",
    cat_waterlog: "Waterlogging",
    cat_garbage: "Garbage & Waste",
    cat_light: "Street Lighting",
    cat_drain: "Stormwater Drainage",
    cat_other: "Civic Utilities",

    // Priorities & Statuses
    priority_high: "High",
    priority_medium: "Medium",
    priority_low: "Low",
    status_submitted: "Submitted",
    status_under_review: "Under Review",
    status_assigned: "Assigned",
    status_in_progress: "In Progress",
    status_resolved: "Resolved",

    // Settings Page
    settings_title: "User Profile & Platform Settings",
    settings_subtitle: "Manage your administrative profile, display theme, language preferences, and municipal triage notification rules.",
    settings_tab_profile: "Officer Profile",
    settings_tab_appearance: "Appearance & Themes",
    settings_tab_language: "Language & Regional",
    settings_tab_notifications: "Triage Notifications",
    settings_tab_diagnostics: "Engine Telemetry",
    profile_heading: "Officer Profile",
    label_full_name: "Full Name *",
    label_role: "Designation / Role *",
    label_department: "Primary Department *",
    btn_save_changes: "Save Profile",
    btn_reset: "Reset",
    theme_heading: "Appearance & Themes",
    theme_subheading: "Select your preferred color scheme. CivicAI stores your choice across browser sessions.",
    theme_sync_note: "Theme automatically synchronizes your charts, Leaflet GIS map tiles, and tables instantly.",
    theme_switch_btn: "Toggle Now",
    lang_heading: "Language & Regional Preferences",
    lang_subheading: "CivicAI provides full bilingual support in English and ಕನ್ನಡ (Kannada) for citizens and municipal staff.",
    notif_heading: "Triage Notification Preferences",
    notif_subheading: "Configure municipal alert triggers when urgent citizen complaints or geographic hotspots are detected.",
    btn_save_preferences: "Save Alert Rules",
    diag_heading: "AI Engine Telemetry & System Diagnostics",

    // Footer
    footer_desc: "Next-generation citizen grievance redressal powered by transparent NLP prioritization, automated triage, and lifecycle tracking.",
    footer_navigation: "Platform Navigation",
    footer_ai_standards: "Municipal AI Standards",
    footer_standards_desc: "CivicAI uses verified multi-factor risk assessment, duplicate deduplication, and explainable NLP algorithms. Zero simulated metrics.",
    footer_copyright: "© 2026 CivicAI Smart Citizen Complaint Management System. All rights reserved.",
    footer_secure: "Secure Municipal Platform"
  },
  kn: {
    badge_ai_active: "ಎಐ ಸಕ್ರಿಯವಾಗಿದೆ",
    nav_home: "ಮುಖಪುಟ",
    nav_report: "ದೂರು ದಾಖಲಿಸಿ",
    nav_track: "ಸ್ಥಿತಿ ಪರಿಶೀಲಿಸಿ",
    nav_dashboard: "ಆಡಳಿತ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    nav_manage: "ದೂರುಗಳ ನಿರ್ವಹಣೆ",
    nav_settings: "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
    btn_report_problem: "ದೂರು ದಾಖಲಿಸಿ",
    admin_portals: "ಆಡಳಿತ ವಿಭಾಗಗಳು",

    // Notifications
    notif_title: "ನಾಗರಿಕ ಅಧಿಸೂಚನೆಗಳು",
    notif_mark_read: "ಓದಿದೆ ಎಂದು ಗುರುತಿಸಿ",
    notif_view_all: "ಎಲ್ಲಾ ದೂರುಗಳನ್ನು ವೀಕ್ಷಿಸಿ",

    // Home Page Hero
    hero_badge: "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಆಧಾರಿತ ದೂರು ಪರಿಹಾರ ವೇದಿಕೆ",
    hero_title_1: "ಸ್ಮಾರ್ಟ್ ನಾಗರಿಕ ಕುಂದುಕೊರತೆ",
    hero_title_2: "ಪರಿಹಾರ ವೇದಿಕೆ",
    hero_subtitle: "ನಾಗರಿಕರು ಮತ್ತು ಪುರಸಭೆಯ ಆಡಳಿತಗಾರರಿಗೆ ಪಾರದರ್ಶಕ NLP ವರ್ಗೀಕರಣ, ತ್ವರಿತ ನಕಲು ಪತ್ತೆ ಮತ್ತು ಭೌಗೋಳಿಕ ಹಾಟ್‌ಸ್ಪಾಟ್ ಬುದ್ಧಿಮತ್ತೆಯೊಂದಿಗೆ ಸಬಲೀಕರಣ.",
    hero_btn_report: "ದೂರು ಸಲ್ಲಿಸಿ",
    hero_btn_track: "ದೂರು ಪರಿಶೀಲಿಸಿ",
    hero_btn_admin: "ಆಡಳಿತ ಕನ್ಸೋಲ್",

    // Stats
    stat_total: "ಒಟ್ಟು ದೂರುಗಳು",
    stat_urgent: "ತುರ್ತು ಎಚ್ಚರಿಕೆಗಳು",
    stat_in_progress: "ಪ್ರಗತಿಯಲ್ಲಿರುವ ಪ್ರಕರಣಗಳು",
    stat_resolved: "ಪರಿಹರಿಸಲಾದ ದೂರುಗಳು",

    // Categories
    cat_road: "ರಸ್ತೆ ಹಾನಿ",
    cat_waterlog: "ನೀರು ನಿಲ್ಲುವುದು",
    cat_garbage: "ತ್ಯಾಜ್ಯ ಮತ್ತು ಕಸ",
    cat_light: "ಬೀದಿ ದೀಪಗಳು",
    cat_drain: "ಒಳಚರಂಡಿ ವ್ಯವಸ್ಥೆ",
    cat_other: "ಇತರ ಸೌಲಭ್ಯಗಳು",

    // Priorities & Statuses
    priority_high: "ಹೆಚ್ಚು (High)",
    priority_medium: "ಮಧ್ಯಮ (Med)",
    priority_low: "ಕಡಿಮೆ (Low)",
    status_submitted: "ಸಲ್ಲಿಸಲಾಗಿದೆ",
    status_under_review: "ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ",
    status_assigned: "ನಿಯೋಜಿಸಲಾಗಿದೆ",
    status_in_progress: "ಪ್ರಗತಿಯಲ್ಲಿದೆ",
    status_resolved: "ಪರಿಹರಿಸಲಾಗಿದೆ",

    // Settings Page
    settings_title: "ಬಳಕೆದಾರರ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
    settings_subtitle: "ನಿಮ್ಮ ಆಡಳಿತಾತ್ಮಕ ಪ್ರೊಫೈಲ್, ಥೀಮ್, ಭಾಷಾ ಆದ್ಯತೆಗಳು ಮತ್ತು ಅಧಿಸೂಚನೆ ನಿಯಮಗಳನ್ನು ನಿರ್ವಹಿಸಿ.",
    settings_tab_profile: "ಅಧಿಕಾರಿಯ ಪ್ರೊಫೈಲ್",
    settings_tab_appearance: "ಗೋಚರತೆ ಮತ್ತು ಥೀಮ್",
    settings_tab_language: "ಭಾಷೆ ಮತ್ತು ಪ್ರಾದೇಶಿಕ",
    settings_tab_notifications: "ದೂರು ಅಧಿಸೂಚನೆಗಳು",
    settings_tab_diagnostics: "ಎಐ ಎಂಜಿನ್ ಸ್ಥಿತಿ",
    profile_heading: "ಅಧಿಕಾರಿಯ ಪ್ರೊಫೈಲ್",
    label_full_name: "ಪೂರ್ಣ ಹೆಸರು *",
    label_role: "ಹುದ್ದೆ / ಪಾತ್ರ *",
    label_department: "ಮುಖ್ಯ ಇಲಾಖೆ *",
    btn_save_changes: "ಪ್ರೊಫೈಲ್ ಉಳಿಸಿ",
    btn_reset: "ಮರುಹೊಂದಿಸಿ",
    theme_heading: "ಗೋಚರತೆ ಮತ್ತು ಥೀಮ್",
    theme_subheading: "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಬಣ್ಣ ಯೋಜನೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ. CivicAI ನಿಮ್ಮ ಆಯ್ಕೆಯನ್ನು ನೆನಪಿಟ್ಟುಕೊಳ್ಳುತ್ತದೆ.",
    theme_sync_note: "ಥೀಮ್ ನಿಮ್ಮ ಚಾರ್ಟ್‌ಗಳು, ನಕ್ಷೆಗಳು ಮತ್ತು ಕೋಷ್ಟಕಗಳನ್ನು ತಕ್ಷಣ ಸಿಂಕ್ ಮಾಡುತ್ತದೆ.",
    theme_switch_btn: "ಈಗಲೇ ಬದಲಾಯಿಸಿ",
    lang_heading: "ಭಾಷೆ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಆದ್ಯತೆಗಳು",
    lang_subheading: "CivicAI ನಾಗರಿಕರು ಮತ್ತು ಸಿಬ್ಬಂದಿಗೆ ಇಂಗ್ಲಿಷ್ ಮತ್ತು ಕನ್ನಡದಲ್ಲಿ ಸಂಪೂರ್ಣ ದ್ವಿಭಾಷಾ ಬೆಂಬಲವನ್ನು ನೀಡುತ್ತದೆ.",
    notif_heading: "ದೂರು ಅಧಿಸೂಚನೆ ಆದ್ಯತೆಗಳು",
    notif_subheading: "ತುರ್ತು ದೂರುಗಳು ಅಥವಾ ಭೌಗೋಳಿಕ ಹಾಟ್‌ಸ್ಪಾಟ್‌ಗಳು ಪತ್ತೆಯಾದಾಗ ಪುರಸಭೆಯ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಹೊಂದಿಸಿ.",
    btn_save_preferences: "ನಿಯಮಗಳನ್ನು ಉಳಿಸಿ",
    diag_heading: "ಎಐ ಎಂಜಿನ್ ಟೆಲಿಮೆಟ್ರಿ ಮತ್ತು ಸಿಸ್ಟಮ್ ಡಯಾಗ್ನೋಸ್ಟಿಕ್ಸ್",

    // Footer
    footer_desc: "ಮುಂದಿನ ಪೀಳಿಗೆಯ ನಾಗರಿಕ ಕುಂದುಕೊರತೆ ನಿವಾರಣೆ, ಪಾರದರ್ಶಕ NLP ಆದ್ಯತೆ ಮತ್ತು ಲೈಫ್‌ಸೈಕಲ್ ಟ್ರ್ಯಾಕಿಂಗ್‌ನೊಂದಿಗೆ ಸಶಕ್ತ.",
    footer_navigation: "ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ ನ್ಯಾವಿಗೇಷನ್",
    footer_ai_standards: "ಪುರಸಭೆಯ ಎಐ ಮಾನದಂಡಗಳು",
    footer_standards_desc: "CivicAI ಪರಿಶೀಲಿಸಿದ ಬಹು-ಅಂಶ ಅಪಾಯ ಮೌಲ್ಯಮಾಪನ, ನಕಲು ಪತ್ತೆ ಮತ್ತು ವಿವರಿಸಬಹುದಾದ NLP ಅಲ್ಗಾರಿದಮ್‌ಗಳನ್ನು ಬಳಸುತ್ತದೆ.",
    footer_copyright: "© 2026 CivicAI ಸ್ಮಾರ್ಟ್ ಸಿಟಿಜನ್ ದೂರು ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ. ಎಲ್ಲ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ.",
    footer_secure: "ಸುರಕ್ಷಿತ ಪುರಸಭಾ ವೇದಿಕೆ"
  }
};

// ==========================================
// 2. THEME MANAGER (Navy Dark & White Light)
// ==========================================
function getStoredTheme() {
  return localStorage.getItem('civicai_theme') || 'dark';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('civicai_theme', theme);

  // Update theme toggle icons
  const icon = document.getElementById('themeToggleIcon');
  if (icon) {
    if (theme === 'light') {
      icon.className = 'fa-solid fa-sun';
      icon.style.color = '#0284c7';
    } else {
      icon.className = 'fa-solid fa-moon';
      icon.style.color = '#00e5bc';
    }
  }

  // Update mobile drawer icon & label
  const mobileIcon = document.getElementById('mobileThemeIcon');
  const mobileLabel = document.getElementById('mobileThemeLabel');
  if (mobileIcon && mobileLabel) {
    if (theme === 'light') {
      mobileIcon.className = 'fa-solid fa-sun';
      mobileLabel.textContent = 'Light Mode';
    } else {
      mobileIcon.className = 'fa-solid fa-moon';
      mobileLabel.textContent = 'Dark Mode';
    }
  }

  // Dispatch custom event for Chart.js / Leaflet map listeners
  window.dispatchEvent(new CustomEvent('civicai_theme_changed', { detail: { theme } }));
}

function toggleTheme() {
  const current = getStoredTheme();
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  showToast(next === 'light' ? 'Switched to Light Mode' : 'Switched to Dark Mode (Navy & Teal)', 'success');
}

// ==========================================
// 3. LANGUAGE SWITCHER (EN / KN)
// ==========================================
function getStoredLanguage() {
  return localStorage.getItem('civicai_lang') || 'en';
}

function applyLanguage(lang) {
  const dict = I18N_TRANSLATIONS[lang] || I18N_TRANSLATIONS['en'];
  localStorage.setItem('civicai_lang', lang);
  document.documentElement.setAttribute('lang', lang);

  // Update all elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Update placeholder attributes
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (dict[key]) {
      el.setAttribute('placeholder', dict[key]);
    }
  });

  // Update navbar language badge
  const langLabel = document.getElementById('currentLangLabel');
  if (langLabel) {
    langLabel.textContent = lang === 'kn' ? 'ಕನ್' : 'EN';
  }

  const mobileLangLabel = document.getElementById('mobileLangLabel');
  if (mobileLangLabel) {
    mobileLangLabel.textContent = lang === 'kn' ? 'English' : 'ಕನ್ನಡ';
  }
}

function toggleLanguage() {
  const current = getStoredLanguage();
  const next = current === 'en' ? 'kn' : 'en';
  applyLanguage(next);
  showToast(next === 'kn' ? 'ಭಾಷೆ: ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ' : 'Language switched to English', 'success');
}

// ==========================================
// 4. NOTIFICATIONS DROPDOWN SYSTEM
// ==========================================
let notificationsLoaded = false;

async function loadNotifications() {
  const listEl = document.getElementById('notifList');
  const badgeEl = document.getElementById('notifBadge');
  if (!listEl) return;

  try {
    const res = await fetch('/api/notifications');
    if (!res.ok) throw new Error('Network error');
    const data = await res.json();

    if (data.success && data.notifications && data.notifications.length > 0) {
      if (badgeEl && data.unread_count > 0) {
        badgeEl.textContent = data.unread_count;
        badgeEl.style.display = 'flex';
      }

      listEl.innerHTML = data.notifications.map((n, idx) => {
        const isUnread = idx < data.unread_count;
        const pColor = (n.priority || '').toLowerCase() === 'high' ? 'var(--priority-critical)' : 'var(--blue-primary)';
        return `
          <div class="notif-item ${isUnread ? 'unread' : ''}" onclick="window.location.href='/track?tracking_id=${n.tracking_id}'">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
              <span class="notif-item-title">
                <i class="fa-solid fa-circle" style="color: ${pColor}; font-size: 0.5rem; margin-right: 6px;"></i>
                ${escapeHTML(n.title)}
              </span>
              <span class="notif-item-time">${formatDate(n.timestamp)}</span>
            </div>
            <div class="notif-item-msg">${escapeHTML(n.message)}</div>
          </div>
        `;
      }).join('');
    } else {
      listEl.innerHTML = `
        <div style="padding: 28px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
          <i class="fa-solid fa-bell-slash" style="font-size: 1.5rem; color: var(--text-dim); margin-bottom: 8px; display: block;"></i>
          No unread civic notifications.
        </div>
      `;
    }
    notificationsLoaded = true;
  } catch (err) {
    listEl.innerHTML = `
      <div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.82rem;">
        <i class="fa-solid fa-circle-check" style="color: var(--teal-primary);"></i> System notifications active.
      </div>
    `;
  }
}

function initNotifications() {
  const notifBtn = document.getElementById('notifBellBtn');
  const dropdown = document.getElementById('notifDropdownMenu');
  const markReadBtn = document.getElementById('markAllReadBtn');
  const badgeEl = document.getElementById('notifBadge');

  if (notifBtn && dropdown) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
      if (dropdown.classList.contains('show') && !notificationsLoaded) {
        loadNotifications();
      }
    });

    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  }

  if (markReadBtn) {
    markReadBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (badgeEl) badgeEl.style.display = 'none';
      document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
      showToast('All notifications marked as read', 'success');
    });
  }

  // Initial silent background load
  loadNotifications();
}

// ==========================================
// 5. CONFIRMATION DIALOG MODAL
// ==========================================
let currentConfirmCallback = null;

function showConfirmDialog(options = {}) {
  const {
    title = 'Confirm Action',
    message = 'Are you sure you want to proceed?',
    icon = 'fa-triangle-exclamation',
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    confirmColor = 'var(--priority-critical)',
    onConfirm = null
  } = options;

  const backdrop = document.getElementById('confirmModalBackdrop');
  const titleEl = document.getElementById('confirmModalTitle');
  const msgEl = document.getElementById('confirmModalMessage');
  const iconEl = document.getElementById('confirmModalIcon');
  const okBtn = document.getElementById('confirmModalOkBtn');
  const cancelBtn = document.getElementById('confirmModalCancelBtn');

  if (!backdrop) {
    if (confirm(message) && typeof onConfirm === 'function') onConfirm();
    return;
  }

  if (titleEl) titleEl.textContent = title;
  if (msgEl) msgEl.textContent = message;
  if (iconEl) iconEl.innerHTML = `<i class="fa-solid ${icon}"></i>`;
  if (okBtn) {
    okBtn.textContent = confirmText;
    okBtn.style.background = confirmColor;
    okBtn.style.borderColor = confirmColor;
  }
  if (cancelBtn) cancelBtn.textContent = cancelText;

  currentConfirmCallback = onConfirm;
  backdrop.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function hideConfirmDialog() {
  const backdrop = document.getElementById('confirmModalBackdrop');
  if (backdrop) {
    backdrop.classList.remove('show');
    document.body.style.overflow = '';
  }
  currentConfirmCallback = null;
}

function initConfirmModal() {
  const backdrop = document.getElementById('confirmModalBackdrop');
  const cancelBtn = document.getElementById('confirmModalCancelBtn');
  const okBtn = document.getElementById('confirmModalOkBtn');

  if (cancelBtn) cancelBtn.addEventListener('click', hideConfirmDialog);
  if (backdrop) {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) hideConfirmDialog();
    });
  }
  if (okBtn) {
    okBtn.addEventListener('click', () => {
      const cb = currentConfirmCallback;
      hideConfirmDialog();
      if (typeof cb === 'function') cb();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && backdrop && backdrop.classList.contains('show')) {
      hideConfirmDialog();
    }
  });
}

// Make accessible to all pages
window.showConfirmDialog = showConfirmDialog;

// ==========================================
// 6. BACK-TO-TOP BUTTON
// ==========================================
function initBackToTop() {
  const btn = document.getElementById('backToTopBtn');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 320) {
      btn.classList.add('show');
    } else {
      btn.classList.remove('show');
    }
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ==========================================
// 7. TOAST NOTIFICATION MANAGER
// ==========================================
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
  const iconColor = type === 'success' ? 'var(--teal-primary)' : 'var(--priority-critical)';

  toast.innerHTML = `
    <i class="fa-solid ${icon}" style="color: ${iconColor}; font-size: 1.15rem;"></i>
    <span style="font-size: 0.9rem; font-weight: 600;">${escapeHTML(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4200);
}
window.showToast = showToast;

// ==========================================
// 8. BADGES & UI UTILITIES (Preserves APIs)
// ==========================================
function getStatusBadge(status) {
  const slug = (status || 'submitted').toLowerCase().replace(/\s+/g, '-');
  let icon = 'fa-clock';
  if (status === 'Under Review') icon = 'fa-magnifying-glass';
  if (status === 'Assigned') icon = 'fa-user-gear';
  if (status === 'In Progress') icon = 'fa-screwdriver-wrench';
  if (status === 'Resolved') icon = 'fa-circle-check';

  return `<span class="badge badge-status-${slug}"><i class="fa-solid ${icon}"></i> ${escapeHTML(status)}</span>`;
}

function getPriorityBadge(priority, score = null) {
  const p = (priority || 'low').toLowerCase();
  let icon = 'fa-circle-info';
  if (p === 'critical' || p === 'high') icon = 'fa-triangle-exclamation';
  if (p === 'medium') icon = 'fa-arrow-up-right-dots';
  if (p === 'low') icon = 'fa-circle-check';

  const scoreText = score ? ` (${score}/100)` : '';
  return `<span class="badge badge-priority-${p}"><i class="fa-solid ${icon}"></i> ${escapeHTML(priority)}${scoreText}</span>`;
}

function getCategoryIcon(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('road')) return 'fa-road';
  if (cat.includes('waterlog')) return 'fa-water';
  if (cat.includes('garbage')) return 'fa-trash-can';
  if (cat.includes('light')) return 'fa-lightbulb';
  if (cat.includes('drain')) return 'fa-faucet-drip';
  return 'fa-layer-group';
}

function formatDate(dateStr) {
  if (!dateStr) return 'Just now';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Global exports
window.applyTheme = applyTheme;
window.toggleTheme = toggleTheme;
window.applyLanguage = applyLanguage;
window.toggleLanguage = toggleLanguage;
window.getStatusBadge = getStatusBadge;
window.getPriorityBadge = getPriorityBadge;
window.getCategoryIcon = getCategoryIcon;
window.formatDate = formatDate;
window.escapeHTML = escapeHTML;

// ==========================================
// 9. DOM INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Mobile Slide-out Drawer
  const drawerOpenBtn = document.getElementById('mobileDrawerOpen');
  const drawerCloseBtn = document.getElementById('mobileDrawerClose');
  const drawerBackdrop = document.getElementById('drawerBackdrop');
  const mobileDrawer = document.getElementById('mobileDrawer');

  function openDrawer() {
    if (mobileDrawer && drawerBackdrop) {
      mobileDrawer.classList.add('open');
      drawerBackdrop.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeDrawer() {
    if (mobileDrawer && drawerBackdrop) {
      mobileDrawer.classList.remove('open');
      drawerBackdrop.classList.remove('show');
      document.body.style.overflow = '';
    }
  }

  if (drawerOpenBtn) drawerOpenBtn.addEventListener('click', openDrawer);
  if (drawerCloseBtn) drawerCloseBtn.addEventListener('click', closeDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeDrawer);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileDrawer && mobileDrawer.classList.contains('open')) {
      closeDrawer();
    }
  });

  // Theme Toggles
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  if (themeToggleBtn) themeToggleBtn.addEventListener('click', toggleTheme);

  const mobileThemeToggleBtn = document.getElementById('mobileThemeToggleBtn');
  if (mobileThemeToggleBtn) mobileThemeToggleBtn.addEventListener('click', toggleTheme);

  // Language Toggles
  const langToggleBtn = document.getElementById('langToggleBtn');
  if (langToggleBtn) langToggleBtn.addEventListener('click', toggleLanguage);

  const mobileLangToggleBtn = document.getElementById('mobileLangToggleBtn');
  if (mobileLangToggleBtn) mobileLangToggleBtn.addEventListener('click', toggleLanguage);

  // Initialize Modules
  applyTheme(getStoredTheme());
  applyLanguage(getStoredLanguage());
  initNotifications();
  initConfirmModal();
  initBackToTop();
});
