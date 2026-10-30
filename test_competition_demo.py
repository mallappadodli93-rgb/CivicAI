#!/usr/bin/env python3
"""
CivicAI - Competition Demonstration Comprehensive Test Suite
Validates all competition requirements:
1. 40 Synthetic complaints in SQLite
2. Deliberate duplicate complaints
3. Urgent safety complaints
4. Multiple categories (all 6)
5. Geographical hotspot detection
6. SQLite data integrity
7. Complaint submission API
8. AI categorization & priority scoring
9. Duplicate detection engine
10. Map & Hotspot detection APIs
11. Admin assignment & status lifecycle updates
12. Citizen complaint tracking
"""
import io
import sys
import unittest
import app
from database.db import query_db
from ai_engine.categorizer import categorize_complaint
from ai_engine.priority_scorer import calculate_priority
from ai_engine.duplicate_detector import detect_duplicate
from ai_engine.hotspot_detector import detect_hotspots

class TestCompetitionDemo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.app.test_client()

    def test_01_sqlite_dataset_count_and_categories(self):
        """Verifies exactly >= 40 synthetic records exist with all 6 categories."""
        total_row = query_db("SELECT COUNT(*) as count FROM complaints", one=True)
        self.assertGreaterEqual(total_row["count"], 40, f"Expected at least 40 complaints, found {total_row['count']}")

        categories = query_db("SELECT DISTINCT category FROM complaints")
        found_cats = {r["category"] for r in categories}
        expected_cats = {"Road Damage", "Waterlogging", "Garbage", "Streetlight", "Drainage", "Other"}
        self.assertEqual(expected_cats, found_cats, f"All 6 categories must be present, found {found_cats}")

        # Verify synthetic labeling
        names = query_db("SELECT citizen_name FROM complaints LIMIT 10")
        for n in names:
            self.assertTrue(n["citizen_name"].startswith("[Synthetic]"), f"Must be synthetic: {n['citizen_name']}")

    def test_02_urgent_safety_complaints(self):
        """Verifies high-priority urgent safety complaints exist in database."""
        high_rows = query_db("SELECT * FROM complaints WHERE ai_priority_level = 'High'")
        self.assertGreaterEqual(len(high_rows), 5, "Expected at least 5 high-priority urgent safety complaints")

    def test_03_deliberate_duplicate_detection_in_db(self):
        """Verifies deliberate duplicates are present and identified in SQLite."""
        dup_rows = query_db("SELECT * FROM complaints WHERE ai_duplicate_of IS NOT NULL")
        self.assertGreaterEqual(len(dup_rows), 4, f"Expected at least 4 flagged duplicates, found {len(dup_rows)}")

    def test_04_complaint_submission(self):
        """Test #7: Tests submitting a new complaint via API."""
        payload = {
            "citizen_name": "[Synthetic] Demo Tester",
            "description": "Exposed high-voltage sparking transformer next to pedestrian bus shelter.",
            "category": "Streetlight",
            "location": "Residency Road Bus Stop, Ward 14",
            "latitude": 12.9712,
            "longitude": 77.6015
        }
        res = self.client.post("/api/complaints/submit", data=payload)
        self.assertIn(res.status_code, (200, 201))
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["tracking_id"].startswith("CIV-2026-"))
        self.assertEqual(data["analysis"]["ai_priority_level"], "High")

    def test_05_ai_categorization_and_priority(self):
        """Test #8: Tests AI categorization and transparent priority scoring."""
        # 1. Road Damage
        res_r = categorize_complaint("Deep crater pothole on highway carriageway")
        self.assertEqual(res_r["category"], "Road Damage")

        # 2. Waterlogging user example
        res_w = categorize_complaint("Water is entering houses because of road flooding.")
        self.assertEqual(res_w["category"], "Waterlogging")
        prio_result = calculate_priority("Water is entering houses because of road flooding.", res_w["category"])
        self.assertEqual(prio_result["level"], "High")
        self.assertIn("residential", prio_result["explanation"].lower())

        # 3. Live wire urgent safety
        res_s = categorize_complaint("Live electrical wire dangling and sparking near school")
        self.assertEqual(res_s["category"], "Streetlight")
        prio_s = calculate_priority("Live electrical wire dangling and sparking near school", res_s["category"])
        self.assertEqual(prio_s["level"], "High")

    def test_06_duplicate_detection_engine(self):
        """Test #9: Tests duplicate detection logic with spatial constraint."""
        existing = [{
            "id": 100,
            "tracking_id": "CIV-TEST-001",
            "description": "Massive deep pothole near Metro Pillar 182 causing bike skids",
            "category": "Road Damage",
            "location": "Outer Ring Road Pillar 182",
            "latitude": 12.9238,
            "longitude": 77.6835,
            "status": "In Progress"
        }]

        # Duplicate: same location (50m away) + similar text
        dup = detect_duplicate(
            description="Deep pothole near Pillar 182 Outer Ring Road bikes skidding dangerously",
            category="Road Damage",
            location="Outer Ring Road Pillar 182",
            existing_complaints=existing
        )
        self.assertTrue(dup["is_duplicate"])
        self.assertEqual(dup["duplicate_of_id"], 100)
        self.assertEqual(dup["duplicate_tracking_id"], "CIV-TEST-001")

        # Not a duplicate: 15km away
        dup_far = detect_duplicate(
            description="Massive deep pothole near Metro Pillar 182 causing bike skids",
            category="Road Damage",
            location="Malleshwaram 7th Cross",
            existing_complaints=existing
        )
        self.assertFalse(dup_far["is_duplicate"], "Complaint in distant neighborhood must not be flagged as duplicate")

    def test_07_map_and_hotspot_detection(self):
        """Test #10: Tests interactive map complaints and hotspot cluster detection."""
        # 1. Map Complaints API
        res_map = self.client.get("/api/map/complaints")
        self.assertEqual(res_map.status_code, 200)
        map_data = res_map.get_json()
        self.assertTrue(map_data["success"])
        self.assertGreaterEqual(len(map_data["complaints"]), 35)

        # 2. Map Hotspots API
        res_hot = self.client.get("/api/map/hotspots")
        self.assertEqual(res_hot.status_code, 200)
        hot_data = res_hot.get_json()
        self.assertTrue(hot_data["success"])
        hotspots = hot_data["hotspots"]
        self.assertGreaterEqual(len(hotspots), 1, "At least 1 geographical hotspot must be detected")
        print(f"\n[GIS Hotspot Engine] Detected {len(hotspots)} municipal hotspots:")
        for h in hotspots:
            print(f"  * {h['name']}: {h['complaint_count']} complaints ({h['severity_label']}, Dominant: {h['dominant_category']})")

    def test_08_admin_assignment_and_status_updates(self):
        """Test #11: Tests admin updating complaint status and assigning departments."""
        target_id = "CIV-2026-SYN01"
        res = self.client.post(
            f"/api/admin/complaints/{target_id}/update",
            json={
                "status": "In Progress",
                "assigned_department": "Stormwater & Flood Management Division",
                "assigned_officer": "Eng. Vikrant Patil",
                "note": "Suction truck operating on 5th Main. Drain intake cleared.",
                "actor": "Competition Demo Admin"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["complaint"]["status"], "In Progress")
        self.assertEqual(data["complaint"]["assigned_officer"], "Eng. Vikrant Patil")

        # Verify SQLite activity_logs updated
        c_row = query_db("SELECT id FROM complaints WHERE tracking_id = ?", (target_id,), one=True)
        logs = query_db("SELECT * FROM activity_logs WHERE complaint_id = ?", (c_row["id"],))
        self.assertGreaterEqual(len(logs), 2)

    def test_09_citizen_complaint_tracking(self):
        """Test #12: Tests citizen tracking by complaint ID with timeline and map data."""
        res = self.client.get("/api/complaints/track/CIV-2026-SYN40")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        c = data["complaint"]
        self.assertEqual(c["tracking_id"], "CIV-2026-SYN40")
        self.assertEqual(c["status"], "Resolved")
        self.assertIsNotNone(c["latitude"])
        self.assertIsNotNone(c["longitude"])
        self.assertGreaterEqual(len(data["activity_logs"]), 2)

if __name__ == "__main__":
    unittest.main()
