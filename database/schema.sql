-- CivicAI SQLite Database Schema with Geolocation Support

CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_id TEXT UNIQUE NOT NULL,
    citizen_name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    is_synthetic INTEGER DEFAULT 0,
    image_filename TEXT,
    status TEXT NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved')),
    assigned_department TEXT DEFAULT 'Unassigned',
    assigned_officer TEXT DEFAULT 'Pending Assignment',
    ai_category TEXT,
    ai_category_confidence REAL,
    ai_summary TEXT,
    ai_priority_score INTEGER,
    ai_priority_level TEXT,
    ai_priority_explanation TEXT,
    ai_duplicate_of INTEGER,
    ai_duplicate_score REAL,
    ai_duplicate_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_duplicate_of) REFERENCES complaints(id)
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    actor TEXT DEFAULT 'System',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_complaints_tracking_id ON complaints(tracking_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category);
CREATE INDEX IF NOT EXISTS idx_complaints_geo ON complaints(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_activity_complaint_id ON activity_logs(complaint_id);
