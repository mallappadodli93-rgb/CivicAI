#!/usr/bin/env python3
"""
CivicAI - Complete Complaint Management Workflow Test Suite
Verifies all 8 requirements:
1. Unique complaint ID generation
2. Citizen tracking by ID
3. Current status display
4. Chronological timeline of progress
5. Department and officer assignment
6. Admin status updates across all 5 lifecycle stages
7. SQLite persistence verification
8. Citizen tracking view reflection
"""
import sys
import unittest
import app
from database.db import query_db

class TestComplaintWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.app.test_client()

    def test_complete_lifecycle_workflow(self):
        print("\n" + "="*70)
        print("RUNNING COMPLETE CIVICAI COMPLAINT MANAGEMENT WORKFLOW TEST")
        print("="*70)

        # -------------------------------------------------------------
        # 1. SUBMIT COMPLAINT & VERIFY UNIQUE ID GENERATION
        # -------------------------------------------------------------
        print("\n[Step 1] Submitting new citizen grievance...")
        submission_payload = {
            "citizen_name": "Meera Krishnan",
            "description": "Hazardous open drainage chamber with exposed rebar near primary school entrance. High risk of child injury.",
            "category": "Drainage",
            "location": "MG Road Sector 4 near St. Anne's School",
            "latitude": 12.9735,
            "longitude": 77.6102
        }
        res = self.client.post("/api/complaints/submit", data=submission_payload)
        self.assertIn(res.status_code, (200, 201), f"Submission failed: {res.data}")
        data = res.get_json()
        self.assertTrue(data.get("success"), "Response success must be True")

        tracking_id = data.get("tracking_id")
        comp_id = data.get("complaint_id")
        self.assertIsNotNone(tracking_id, "Unique tracking ID must be generated")
        self.assertTrue(tracking_id.startswith("CIV-"), f"Tracking ID must start with CIV-, got {tracking_id}")
        print(f"  -> Successfully generated Complaint ID: #{comp_id} (Tracking ID: {tracking_id})")

        # -------------------------------------------------------------
        # 2. CITIZEN TRACKS COMPLAINT (INITIAL STAGE: SUBMITTED)
        # -------------------------------------------------------------
        print("\n[Step 2] Citizen tracking complaint by Tracking ID...")
        res = self.client.get(f"/api/complaints/track/{tracking_id}")
        self.assertEqual(res.status_code, 200)
        track_data = res.get_json()
        self.assertTrue(track_data["success"])
        c = track_data["complaint"]
        self.assertEqual(c["status"], "Submitted")
        self.assertEqual(c["citizen_name"], "Meera Krishnan")
        print(f"  -> Current Status: {c['status']}")
        print(f"  -> AI Category: {c['ai_category']} ({c['ai_priority_level']} Priority)")

        # Verify initial timeline
        logs = track_data["activity_logs"]
        self.assertGreaterEqual(len(logs), 2, "Should have submission and AI triage logs")
        print(f"  -> Timeline events recorded: {len(logs)}")
        for l in logs:
            print(f"     * [{l['actor']}] {l['action']}: {l['details']}")

        # -------------------------------------------------------------
        # 3. ADMIN REVIEW & TRANSITION TO 'UNDER REVIEW'
        # -------------------------------------------------------------
        print("\n[Step 3] Admin reviewing complaint and setting status to 'Under Review'...")
        res = self.client.post(
            f"/api/admin/complaints/{tracking_id}/update",
            json={
                "status": "Under Review",
                "note": "School safety emergency intake logged. Fast-tracked for municipal engineering inspection.",
                "actor": "Central Dispatch Desk"
            }
        )
        self.assertEqual(res.status_code, 200)
        up_data = res.get_json()
        self.assertTrue(up_data["success"])
        self.assertEqual(up_data["complaint"]["status"], "Under Review")
        print("  -> Status updated to 'Under Review' in SQLite")

        # -------------------------------------------------------------
        # 4. ADMIN ASSIGNS TO DEPARTMENT & FIELD OFFICER ('ASSIGNED')
        # -------------------------------------------------------------
        print("\n[Step 4] Admin assigning complaint to Drainage Board & Field Officer...")
        res = self.client.post(
            f"/api/admin/complaints/{comp_id}/update",
            json={
                "status": "Assigned",
                "assigned_department": "Water Supply & Sewerage Board",
                "assigned_officer": "Assistant Engineer Priya Sharma",
                "note": "Emergency maintenance order dispatched to Central Drainage Unit.",
                "actor": "Municipal Chief Engineer"
            }
        )
        self.assertEqual(res.status_code, 200)
        assign_data = res.get_json()
        self.assertTrue(assign_data["success"])
        self.assertEqual(assign_data["complaint"]["status"], "Assigned")
        self.assertEqual(assign_data["complaint"]["assigned_department"], "Water Supply & Sewerage Board")
        self.assertEqual(assign_data["complaint"]["assigned_officer"], "Assistant Engineer Priya Sharma")
        print(f"  -> Assigned Department: {assign_data['complaint']['assigned_department']}")
        print(f"  -> Assigned Officer: {assign_data['complaint']['assigned_officer']}")

        # -------------------------------------------------------------
        # 5. ADMIN ADVANCES TO 'IN PROGRESS'
        # -------------------------------------------------------------
        print("\n[Step 5] Field officer updating status to 'In Progress'...")
        res = self.client.post(
            f"/api/admin/complaints/{tracking_id}/update",
            json={
                "status": "In Progress",
                "note": "Safety barricades erected around open chamber. New heavy-duty cast iron slab being installed.",
                "actor": "Assistant Engineer Priya Sharma"
            }
        )
        self.assertEqual(res.status_code, 200)
        prog_data = res.get_json()
        self.assertEqual(prog_data["complaint"]["status"], "In Progress")
        print("  -> Status advanced to 'In Progress' with field repair notes")

        # -------------------------------------------------------------
        # 6. ADMIN RESOLVES COMPLAINT ('RESOLVED')
        # -------------------------------------------------------------
        print("\n[Step 6] Admin marking complaint as 'Resolved'...")
        res = self.client.post(
            f"/api/admin/complaints/{tracking_id}/update",
            json={
                "status": "Resolved",
                "note": "New reinforced concrete cover installed and sealed. Site inspected and certified safe.",
                "actor": "Assistant Engineer Priya Sharma"
            }
        )
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertEqual(res_data["complaint"]["status"], "Resolved")
        print("  -> Status marked 'Resolved' in SQLite")

        # -------------------------------------------------------------
        # 7. DIRECT SQLITE PERSISTENCE VERIFICATION
        # -------------------------------------------------------------
        print("\n[Step 7] Querying SQLite database directly to verify persistence...")
        db_row = query_db("SELECT * FROM complaints WHERE id = ?", (comp_id,), one=True)
        self.assertIsNotNone(db_row)
        self.assertEqual(db_row["status"], "Resolved")
        self.assertEqual(db_row["assigned_department"], "Water Supply & Sewerage Board")
        self.assertEqual(db_row["assigned_officer"], "Assistant Engineer Priya Sharma")

        db_logs = query_db("SELECT * FROM activity_logs WHERE complaint_id = ? ORDER BY timestamp ASC", (comp_id,))
        self.assertGreaterEqual(len(db_logs), 6, "Must have recorded all 6 lifecycle events")
        print(f"  -> Verified SQLite complaints row: status={db_row['status']}, dept={db_row['assigned_department']}")
        print(f"  -> Verified SQLite activity_logs rows: {len(db_logs)} permanent audit entries found")

        # -------------------------------------------------------------
        # 8. FINAL CITIZEN TRACKING VERIFICATION
        # -------------------------------------------------------------
        print("\n[Step 8] Citizen tracks complaint to view resolved state and full timeline...")
        # Verify tracking works case-insensitively
        res = self.client.get(f"/api/complaints/track/{tracking_id.lower()}")
        self.assertEqual(res.status_code, 200)
        final_track = res.get_json()
        fc = final_track["complaint"]
        f_logs = final_track["activity_logs"]

        self.assertEqual(fc["status"], "Resolved")
        self.assertEqual(fc["assigned_department"], "Water Supply & Sewerage Board")
        self.assertEqual(fc["assigned_officer"], "Assistant Engineer Priya Sharma")
        print(f"  -> Tracking Verified: Status={fc['status']}, Officer={fc['assigned_officer']}")
        print("  -> Complete Redressal Audit Trail:")
        for idx, l in enumerate(f_logs, 1):
            print(f"     {idx}. [{l['actor']}] {l['action']} -> {l['details']}")

        print("\n" + "="*70)
        print("ALL 8 REQUIREMENTS TESTED AND PASSED SUCCESSFULLY!")
        print("="*70)

    def test_invalid_status_rejected(self):
        """Verifies invalid lifecycle status is rejected with 400 Bad Request."""
        row = query_db("SELECT id FROM complaints LIMIT 1", one=True)
        cid = row["id"] if row else 1
        res = self.client.post(f"/api/admin/complaints/{cid}/update", json={"status": "FakeStatus"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Invalid status", data["error"])

    def test_nonexistent_complaint_returns_404(self):
        """Verifies non-existent complaint lookup returns 404."""
        res = self.client.get("/api/complaints/track/CIV-9999-NOTFOUND")
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
