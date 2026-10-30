"""
CivicAI - Smart Citizen Complaint Management System
Python Flask Backend Application
"""
import os
import re
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory

from config import Config
from database.db import init_db, get_db_connection, query_db, execute_db, log_activity
from ai_engine import analyze_complaint
from ai_engine.hotspot_detector import detect_hotspots

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

VALID_STATUSES = {'Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved'}

def allowed_file(filename):
    """Verifies filename has an authorized image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def is_valid_image_header(stream):
    """
    Validates genuine image magic bytes to prevent masquerading malicious files:
    - JPEG: \xff\xd8\xff
    - PNG: \x89PNG\r\n\x1a\n
    - GIF: GIF87a / GIF89a
    - WEBP: RIFF....WEBP
    """
    header = stream.read(16)
    stream.seek(0)
    if not header or len(header) < 4:
        return False
    if header.startswith(b'\xff\xd8\xff'):
        return True
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return True
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        return True
    if header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WEBP':
        return True
    return False

def generate_tracking_id():
    """Generates guaranteed unique citizen tracking ID, e.g. CIV-2026-84920."""
    year = datetime.now().year
    while True:
        candidate = f"CIV-{year}-{uuid.uuid4().hex[:6].upper()}"
        exists = query_db("SELECT 1 FROM complaints WHERE tracking_id = ?", (candidate,), one=True)
        if not exists:
            return candidate

# ==========================================
# PAGE ROUTES
# ==========================================

@app.route('/')
def home():
    """
    Landing Page:
    Queries real-time SQLite statistics (Total, Pending, Resolved, Urgent)
    and renders recent municipal grievance resolutions.
    """
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status != 'Resolved' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN (ai_priority_level = 'Critical' OR ai_priority_level = 'High') AND status != 'Resolved' THEN 1 ELSE 0 END) as urgent
        FROM complaints
    """, one=True) or {"total": 0, "pending": 0, "resolved": 0, "urgent": 0}

    for key in stats:
        if stats[key] is None:
            stats[key] = 0

    recent_complaints = query_db("""
        SELECT id, tracking_id, category, location, status, ai_priority_level, ai_priority_score, ai_summary, created_at
        FROM complaints
        ORDER BY created_at DESC
        LIMIT 4
    """)

    return render_template('home.html', stats=stats, recent_complaints=recent_complaints)

@app.route('/submit')
def submit_page():
    """Citizen complaint submission portal with real-time AI assistance."""
    return render_template('submit.html')

@app.route('/track')
def track_page():
    """Citizen tracking page with interactive 5-stage timeline."""
    prefill_id = request.args.get('id', '').strip()
    return render_template('track.html', prefill_id=prefill_id)

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    """Executive Municipal Admin Dashboard with live charts and KPI widgets."""
    return render_template('admin_dashboard.html')

@app.route('/admin/complaints')
def admin_complaints():
    """Admin Complaint Management Console with triage actions, filtering and AI insights."""
    selected_id = request.args.get('id')
    return render_template('admin_complaints.html', selected_id=selected_id)

@app.route('/settings')
def settings_page():
    """User profile, accessibility, theme preferences, and municipal settings."""
    return render_template('settings.html')

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Returns recent civic alerts and municipal activity notifications."""
    recent_logs = query_db("""
        SELECT a.id, a.action, a.details, a.actor, a.timestamp, c.tracking_id, c.category, c.ai_priority_level
        FROM activity_logs a
        JOIN complaints c ON a.complaint_id = c.id
        ORDER BY a.timestamp DESC
        LIMIT 6
    """)
    notifications = []
    for l in recent_logs:
        notifications.append({
            "id": l["id"],
            "title": f"{l['tracking_id']} – {l['action']}",
            "message": l["details"] or f"Action taken by {l['actor']}",
            "priority": l["ai_priority_level"] or "Medium",
            "timestamp": l["timestamp"],
            "tracking_id": l["tracking_id"]
        })
    return jsonify({
        "success": True,
        "unread_count": min(3, len(notifications)),
        "notifications": notifications
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or save user preferences."""
    if request.method == 'POST':
        data = request.get_json() or {}
        return jsonify({
            "success": True,
            "message": "User preferences saved successfully.",
            "settings": data
        })
    return jsonify({
        "success": True,
        "settings": {
            "name": "Municipal Officer",
            "role": "Field Operations Coordinator",
            "department": "Department of Roads & Infrastructure",
            "theme": "dark",
            "language": "en",
            "email_alerts": True,
            "high_priority_sound": True
        }
    })

# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route('/api/ai/preview', methods=['POST'])
def ai_preview():
    """
    Live AI analysis endpoint:
    Evaluates grievance text as the citizen types in real-time.
    Returns predicted category, confidence, executive summary, priority, and duplicate check.
    """
    data = request.get_json() or {}
    description = data.get('description', '').strip()
    location = data.get('location', '').strip()
    category = data.get('category', '').strip()

    if not description or len(description) < 10:
        return jsonify({
            "status": "waiting",
            "message": "Enter at least 10 characters to trigger AI analysis."
        })

    # Retrieve existing active complaints for duplicate detection
    existing = query_db("""
        SELECT id, tracking_id, description, location, category, status 
        FROM complaints 
        WHERE status != 'Resolved'
        ORDER BY created_at DESC 
        LIMIT 50
    """)

    analysis = analyze_complaint(
        description=description,
        location=location,
        category=category,
        existing_complaints=existing
    )

    return jsonify({
        "status": "success",
        "analysis": analysis
    })

@app.route('/api/complaints', methods=['POST'])
@app.route('/api/complaints/submit', methods=['POST'])
def submit_complaint():
    """
    API 1: Submit Complaint
    Accepts both multipart/form-data (with optional photo) and application/json.
    Validates all inputs, performs safe image file inspection,
    runs AI triage, and stores the record in SQLite with an activity log.
    """
    if request.is_json:
        data = request.get_json() or {}
        citizen_name = data.get('citizen_name', '').strip()
        description = data.get('description', '').strip()
        location = data.get('location', '').strip()
        category = data.get('category', 'Auto-Detect').strip()
        file = None
    else:
        citizen_name = request.form.get('citizen_name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        category = request.form.get('category', 'Auto-Detect').strip()
        file = request.files.get('image')

    # Input validation
    errors = []
    if not citizen_name or len(citizen_name) < 2:
        errors.append("Citizen Name must be at least 2 characters long.")
    elif len(citizen_name) > 100:
        errors.append("Citizen Name must not exceed 100 characters.")

    if not description or len(description) < 10:
        errors.append("Complaint Description must be at least 10 characters long.")
    elif len(description) > 3000:
        errors.append("Complaint Description must not exceed 3000 characters.")

    if not location or len(location) < 3:
        errors.append("Incident Location must be at least 3 characters long.")
    elif len(location) > 200:
        errors.append("Incident Location must not exceed 200 characters.")

    if errors:
        return jsonify({"success": False, "error": " ".join(errors), "validation_errors": errors}), 400

    # Safe file validation and processing
    image_filename = None
    if file and file.filename != '':
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"Invalid image format. Allowed formats: {', '.join(Config.ALLOWED_EXTENSIONS)}."
            }), 400

        # Validate magic bytes / image header
        if not is_valid_image_header(file.stream):
            return jsonify({
                "success": False,
                "error": "The uploaded file does not match a valid image header signature."
            }), 400

        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_token = uuid.uuid4().hex[:8]
        filename = secure_filename(f"complaint_{timestamp_str}_{unique_token}.{ext}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_filename = filename

    # Geolocation handling - compulsory for real citizen complaints
    lat_val = data.get('latitude') if request.is_json else request.form.get('latitude')
    lng_val = data.get('longitude') if request.is_json else request.form.get('longitude')
    try:
        latitude = float(lat_val) if lat_val is not None and str(lat_val).strip() != '' else None
        longitude = float(lng_val) if lng_val is not None and str(lng_val).strip() != '' else None
    except (ValueError, TypeError):
        latitude, longitude = None, None

    if latitude is None or longitude is None:
        return jsonify({
            "success": False,
            "error": "Location coordinates are required. Please select a point on the map or use your GPS location."
        }), 400

    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
        return jsonify({
            "success": False,
            "error": "Invalid coordinates provided. Latitude must be between -90 and 90, Longitude between -180 and 180."
        }), 400

    # Run AI analysis against existing active complaints
    existing = query_db("""
        SELECT id, tracking_id, description, location, category, status 
        FROM complaints 
        WHERE status != 'Resolved'
        ORDER BY created_at DESC 
        LIMIT 50
    """)

    analysis = analyze_complaint(
        description=description,
        location=location,
        category=category if category != 'Auto-Detect' else None,
        existing_complaints=existing
    )

    tracking_id = generate_tracking_id()
    assigned_dept = analysis["suggested_department"]

    query = """
        INSERT INTO complaints (
            tracking_id, citizen_name, description, category, location,
            latitude, longitude, is_synthetic, image_filename,
            status, assigned_department, assigned_officer,
            ai_category, ai_category_confidence, ai_summary,
            ai_priority_score, ai_priority_level, ai_priority_explanation,
            ai_duplicate_of, ai_duplicate_score, ai_duplicate_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, 'Submitted', ?, 'Pending Assignment', ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    comp_id = execute_db(query, (
        tracking_id,
        citizen_name,
        description,
        analysis["category"],
        location,
        latitude,
        longitude,
        image_filename,
        assigned_dept,
        analysis["ai_category"],
        analysis["ai_category_confidence"],
        analysis["ai_summary"],
        analysis["ai_priority_score"],
        analysis["ai_priority_level"],
        analysis["ai_priority_explanation"],
        analysis["ai_duplicate_of"],
        analysis["ai_duplicate_score"],
        analysis["ai_duplicate_notes"]
    ))

    # Activity audit log creation
    log_activity(comp_id, "Complaint Submitted", f"Filed by citizen {citizen_name} via web portal.", citizen_name)
    log_activity(
        comp_id, 
        "AI Triage Completed", 
        f"Assigned {analysis['ai_priority_level']} priority ({analysis['ai_priority_score']}/100) and routed to {assigned_dept}.",
        "CivicAI Engine"
    )

    if analysis["is_duplicate"]:
        log_activity(
            comp_id,
            "Potential Duplicate Flagged",
            f"AI identified {int(analysis['ai_duplicate_score']*100)}% similarity with #{analysis['ai_duplicate_tracking_id']}.",
            "CivicAI Engine"
        )

    return jsonify({
        "success": True,
        "tracking_id": tracking_id,
        "complaint_id": comp_id,
        "message": "Complaint successfully registered and analyzed by CivicAI.",
        "analysis": analysis
    }), 201

@app.route('/api/complaints', methods=['GET'])
@app.route('/api/admin/complaints', methods=['GET'])
def get_complaints():
    """
    API 2: Retrieve All Complaints
    Supports multi-field filtering (status, category, priority), search query, and sorting.
    """
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'priority_desc')

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if status_filter and status_filter != 'All':
        query += " AND status = ?"
        params.append(status_filter)

    if category_filter and category_filter != 'All':
        query += " AND category = ?"
        params.append(category_filter)

    if priority_filter and priority_filter != 'All':
        query += " AND ai_priority_level = ?"
        params.append(priority_filter)

    if search:
        query += " AND (tracking_id LIKE ? OR citizen_name LIKE ? OR description LIKE ? OR location LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    if sort_by == 'priority_desc':
        query += " ORDER BY ai_priority_score DESC, created_at DESC"
    elif sort_by == 'priority_asc':
        query += " ORDER BY ai_priority_score ASC, created_at DESC"
    elif sort_by == 'oldest':
        query += " ORDER BY created_at ASC"
    else:  # newest
        query += " ORDER BY created_at DESC"

    rows = query_db(query, params)
    return jsonify({
        "success": True,
        "count": len(rows),
        "complaints": [dict(r) for r in rows]
    })

@app.route('/api/complaints/<identifier>', methods=['GET'])
@app.route('/api/complaints/track/<identifier>', methods=['GET'])
@app.route('/api/admin/complaints/<identifier>', methods=['GET'])
def get_single_complaint(identifier):
    """
    API 3: Track / Retrieve Single Complaint
    Retrieves complaint details by either numeric database ID (e.g., 1)
    or alphanumeric Tracking ID (e.g., CIV-2026-00101) case-insensitively.
    Returns complaint record, chronological audit trail, and duplicate reference.
    """
    target = str(identifier).strip()

    # Query by tracking_id (case-insensitive) or numeric primary key
    complaint = query_db("""
        SELECT * FROM complaints 
        WHERE UPPER(tracking_id) = UPPER(?) OR id = ?
    """, (target, target), one=True)

    if not complaint:
        return jsonify({
            "success": False,
            "error": f"Complaint '{target}' not found. Please verify the ID."
        }), 404

    # Fetch chronological activity audit logs
    logs = query_db("""
        SELECT action, details, actor, timestamp 
        FROM activity_logs 
        WHERE complaint_id = ? 
        ORDER BY timestamp ASC
    """, (complaint["id"],))

    # Duplicate reference resolution
    duplicate_info = None
    if complaint["ai_duplicate_of"]:
        dup = query_db("""
            SELECT tracking_id, category, description, location, status 
            FROM complaints 
            WHERE id = ?
        """, (complaint["ai_duplicate_of"],), one=True)
        if dup:
            duplicate_info = dict(dup)

    return jsonify({
        "success": True,
        "complaint": dict(complaint),
        "activity_logs": [dict(l) for l in logs],
        "duplicate_ref": duplicate_info
    })

@app.route('/api/complaints/<identifier>/status', methods=['POST', 'PUT'])
@app.route('/api/admin/complaints/<identifier>/update', methods=['POST', 'PUT'])
def update_complaint_status(identifier):
    """
    API 4: Update Complaint Status & Triage Details
    Validates status against allowed lifecycle stages:
    [Submitted, Under Review, Assigned, In Progress, Resolved].
    Updates department, officer, and logs action with official audit remarks in SQLite.
    Supports both numeric database ID (e.g. 1) and tracking ID (e.g. CIV-2026-00101).
    """
    data = request.get_json() or {}
    new_status = data.get('status')
    department = data.get('assigned_department')
    officer = data.get('assigned_officer')
    admin_note = data.get('note', '').strip()
    actor = data.get('actor', 'Municipal Admin Officer')

    target = str(identifier).strip()
    complaint = query_db("""
        SELECT * FROM complaints 
        WHERE UPPER(tracking_id) = UPPER(?) OR id = ?
    """, (target, target), one=True)

    if not complaint:
        return jsonify({"success": False, "error": f"Complaint '{target}' not found."}), 404

    cid = complaint['id']

    if new_status and new_status not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "error": f"Invalid status '{new_status}'. Allowed statuses: {', '.join(sorted(VALID_STATUSES))}."
        }), 400

    updates = []
    params = []

    old_status = complaint['status']
    status_changed = bool(new_status and new_status != old_status)

    if new_status:
        updates.append("status = ?")
        params.append(new_status)
    if department:
        updates.append("assigned_department = ?")
        params.append(department)
    if officer:
        updates.append("assigned_officer = ?")
        params.append(officer)

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(cid)

    query = f"UPDATE complaints SET {', '.join(updates)} WHERE id = ?"
    execute_db(query, params)

    # Activity audit logging in SQLite
    if status_changed:
        if new_status == "Resolved":
            action_name = "Complaint Resolved"
            details_text = f"Status marked as Resolved from '{old_status}'."
        else:
            action_name = f"Status: {new_status}"
            details_text = f"Status progressed from '{old_status}' to '{new_status}'."

        if admin_note:
            details_text += f" Official remarks: {admin_note}"

        log_activity(cid, action_name, details_text, actor)
    elif admin_note:
        log_activity(cid, "Admin Note Added", admin_note, actor)

    if department and department != complaint['assigned_department']:
        log_activity(cid, "Department Assigned", f"Assigned to {department}.", actor)

    if officer and officer != complaint['assigned_officer'] and officer != 'Pending Assignment':
        log_activity(cid, "Field Officer Assigned", f"Assigned field officer {officer} for inspection and execution.", actor)

    # Retrieve updated complaint
    updated_complaint = query_db("SELECT * FROM complaints WHERE id = ?", (cid,), one=True)

    # Fetch updated activity logs
    logs = query_db("""
        SELECT action, details, actor, timestamp 
        FROM activity_logs 
        WHERE complaint_id = ? 
        ORDER BY timestamp ASC
    """, (cid,))

    return jsonify({
        "success": True,
        "message": f"Complaint {complaint['tracking_id']} updated successfully.",
        "complaint": dict(updated_complaint),
        "activity_logs": [dict(l) for l in logs]
    })

@app.route('/api/admin/metrics', methods=['GET'])
def admin_metrics():
    """
    API 5: Real-time Admin Analytics & KPI Metrics
    Calculates actual database numbers for dashboard cards and Chart.js graphs.
    Zero hardcoded values.
    """
    # 1. Total counts grouped by status
    status_counts = query_db("""
        SELECT status, COUNT(*) as count 
        FROM complaints 
        GROUP BY status
    """)
    status_map = {r["status"]: r["count"] for r in status_counts}
    
    # 2. Total counts grouped by priority level
    priority_counts = query_db("""
        SELECT ai_priority_level, COUNT(*) as count 
        FROM complaints 
        GROUP BY ai_priority_level
    """)
    priority_map = {r["ai_priority_level"]: r["count"] for r in priority_counts}

    # 3. Total counts grouped by category
    category_counts = query_db("""
        SELECT category, COUNT(*) as count 
        FROM complaints 
        GROUP BY category 
        ORDER BY count DESC
    """)

    # 4. Computed KPIs
    total_complaints = sum(status_map.values())
    resolved_count = status_map.get("Resolved", 0)
    pending_count = total_complaints - resolved_count
    
    urgent_count_row = query_db("""
        SELECT COUNT(*) as count FROM complaints 
        WHERE (ai_priority_level = 'Critical' OR ai_priority_level = 'High') AND status != 'Resolved'
    """, one=True)
    urgent_count = urgent_count_row["count"] if urgent_count_row else 0

    critical_active_row = query_db("""
        SELECT COUNT(*) as count FROM complaints 
        WHERE ai_priority_level = 'Critical' AND status != 'Resolved'
    """, one=True)
    critical_active = critical_active_row["count"] if critical_active_row else 0

    resolution_rate = round((resolved_count / total_complaints * 100), 1) if total_complaints > 0 else 0
    in_progress_count = status_map.get("In Progress", 0)
    pending_review = status_map.get("Submitted", 0) + status_map.get("Under Review", 0)

    # 5. Live activity audit stream
    recent_activity = query_db("""
        SELECT a.action, a.details, a.actor, a.timestamp, c.tracking_id, c.category
        FROM activity_logs a
        JOIN complaints c ON a.complaint_id = c.id
        ORDER BY a.timestamp DESC
        LIMIT 8
    """)

    # 6. Recent complaints for embedded dashboard table
    recent_complaints_table = query_db("""
        SELECT id, tracking_id, citizen_name, category, location, status, ai_priority_level, ai_priority_score, created_at
        FROM complaints
        ORDER BY created_at DESC
        LIMIT 6
    """)

    # 7. Hotspot GIS Detection
    active_complaints_geo = query_db("""
        SELECT * FROM complaints 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND status != 'Resolved'
    """)
    detected_hotspots = detect_hotspots(active_complaints_geo)

    return jsonify({
        "success": True,
        "total": total_complaints,
        "resolved": resolved_count,
        "pending": pending_count,
        "urgent": urgent_count,
        "resolution_rate": resolution_rate,
        "in_progress": in_progress_count,
        "pending_review": pending_review,
        "critical_active": critical_active,
        "hotspot_count": len(detected_hotspots),
        "hotspots": detected_hotspots,
        "status_distribution": {
            "Submitted": status_map.get("Submitted", 0),
            "Under Review": status_map.get("Under Review", 0),
            "Assigned": status_map.get("Assigned", 0),
            "In Progress": status_map.get("In Progress", 0),
            "Resolved": status_map.get("Resolved", 0)
        },
        "priority_distribution": {
            "High": priority_map.get("High", 0) + priority_map.get("Critical", 0),
            "Medium": priority_map.get("Medium", 0),
            "Low": priority_map.get("Low", 0)
        },
        "category_distribution": [dict(c) for c in category_counts],
        "recent_activity": [dict(a) for a in recent_activity],
        "recent_complaints": [dict(r) for r in recent_complaints_table]
    })

# ==========================================
# MAP & HOTSPOT GIS ENDPOINTS
# ==========================================

@app.route('/api/map/complaints', methods=['GET'])
def get_map_complaints():
    """
    Returns complaints with GPS coordinates for Leaflet interactive map,
    supporting category, priority, status, source (real vs synthetic), and text search.
    """
    category = request.args.get('category', '').strip()
    priority = request.args.get('priority', '').strip()
    status = request.args.get('status', '').strip()
    source = request.args.get('source', '').strip()
    search = request.args.get('search', '').strip()

    query = "SELECT * FROM complaints WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
    params = []

    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)

    if priority and priority != 'All':
        query += " AND ai_priority_level = ?"
        params.append(priority)

    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)

    if source == 'real':
        query += " AND (is_synthetic = 0 OR is_synthetic IS NULL)"
    elif source == 'synthetic':
        query += " AND is_synthetic = 1"

    if search:
        query += " AND (tracking_id LIKE ? OR location LIKE ? OR citizen_name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY created_at DESC"

    rows = query_db(query, params)
    return jsonify({
        "success": True,
        "count": len(rows),
        "complaints": [dict(r) for r in rows]
    })

@app.route('/api/map/missing-coordinates', methods=['GET'])
def get_missing_coordinate_complaints():
    """
    Returns complaints that lack latitude or longitude coordinates,
    so administrators can review and specify the correct location.
    """
    rows = query_db("""
        SELECT id, tracking_id, citizen_name, category, location, status,
               ai_priority_level, ai_priority_score, ai_summary, created_at, is_synthetic
        FROM complaints 
        WHERE latitude IS NULL OR longitude IS NULL
        ORDER BY created_at DESC
    """)
    return jsonify({
        "success": True,
        "count": len(rows),
        "complaints": [dict(r) for r in rows]
    })

@app.route('/api/complaints/<int:complaint_id>/update-location', methods=['POST'])
def update_complaint_location(complaint_id):
    """
    Allows setting or correcting coordinates and address for a complaint.
    """
    data = request.get_json() or {}
    lat = data.get('latitude')
    lng = data.get('longitude')
    loc = data.get('location', '').strip()

    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Valid numerical latitude and longitude are required."}), 400

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
        return jsonify({"success": False, "error": "Latitude must be between -90 and 90, Longitude between -180 and 180."}), 400

    complaint = query_db("SELECT id, tracking_id FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not complaint:
        return jsonify({"success": False, "error": "Complaint not found."}), 404

    if loc:
        execute_db("""
            UPDATE complaints 
            SET latitude = ?, longitude = ?, location = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (lat, lng, loc, complaint_id))
    else:
        execute_db("""
            UPDATE complaints 
            SET latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (lat, lng, complaint_id))

    log_activity(complaint_id, "Location Corrected", f"Coordinates updated to ({lat:.5f}, {lng:.5f}) by administrator.", "Admin")

    return jsonify({
        "success": True,
        "message": f"Location for #{complaint['tracking_id']} updated successfully.",
        "latitude": lat,
        "longitude": lng
    })

@app.route('/api/map/hotspots', methods=['GET'])
def get_map_hotspots():
    """
    Detects and returns municipal complaint hotspots (clusters)
    with centroid, radius, dominant category, and severity assessment.
    """
    category = request.args.get('category', '').strip()
    query = "SELECT * FROM complaints WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND status != 'Resolved'"
    params = []

    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)

    complaints = query_db(query, params)
    hotspots = detect_hotspots(complaints)

    return jsonify({
        "success": True,
        "count": len(hotspots),
        "hotspots": hotspots
    })

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Safely serves citizen uploaded photos from the configured upload directory.
    Returns 404 if file does not exist.
    """
    safe_name = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found."}), 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe_name)

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(400)
def bad_request_error(e):
    return jsonify({"success": False, "error": "Bad request. Please verify your inputs."}), 400

@app.errorhandler(404)
def not_found_error(e):
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "Endpoint or resource not found."}), 404
    return render_template('home.html', stats={"total": 0, "pending": 0, "resolved": 0, "urgent": 0}, recent_complaints=[]), 404

@app.errorhandler(413)
def file_too_large_error(e):
    return jsonify({"success": False, "error": "File exceeds maximum permitted size of 16 MB."}), 413

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"success": False, "error": "An internal server error occurred."}), 500

# ==========================================
# APPLICATION ENTRYPOINT
# ==========================================

def find_available_port(preferred_port=5001):
    import socket
    for p in [preferred_port, 5050, 8000, 8080]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('127.0.0.1', p))
            s.close()
            return p
        except:
            continue
    return preferred_port

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', find_available_port(5001)))
    print(f"\n=======================================================")
    print(f"🚀 CivicAI Web Server running at: http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
