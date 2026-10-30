"""
CivicAI - Location Tracking & All-Location Map Test Suite
Validates:
1. Compulsory location collection (rejects missing/invalid coordinates).
2. Submissions from at least 5 distinct geographical locations across multiple areas/cities.
3. Accurate persistence of user-entered address, latitude, and longitude in SQLite without modification.
4. Old complaints remain visible alongside newly submitted complaints.
5. All 5+ locations appear on the all-location admin map (/api/map/complaints).
6. Multi-field filtering (category, priority, status, source, text search).
7. Complaints missing coordinates workflow & location correction API.
"""

import unittest
import json
import sqlite3
import os
import sys

# Ensure application modules can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from database.db import get_db_connection, init_db, query_db

class TestLocationTracking(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_01_mandatory_location_validation(self):
        """Test that complaints without latitude/longitude coordinates are rejected."""
        # Missing coordinates completely
        payload_no_coords = {
            "citizen_name": "Test User",
            "description": "Pothole on the main street with exposed gravel.",
            "category": "Road Damage",
            "location": "MG Road"
        }
        res = self.client.post('/api/complaints/submit', data=payload_no_coords)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertIn("Location coordinates are required", data['error'])

        # Invalid numerical coordinates
        payload_invalid_coords = {
            "citizen_name": "Test User",
            "description": "Pothole on the main street with exposed gravel.",
            "category": "Road Damage",
            "location": "MG Road",
            "latitude": 999.0, # Out of range
            "longitude": 77.59
        }
        res = self.client.post('/api/complaints/submit', data=payload_invalid_coords)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_02_submit_from_five_different_locations(self):
        """Submit complaints from at least 5 different distinct locations and verify exact coordinate persistence."""
        test_locations = [
            {
                "citizen_name": "Citizen A - Indiranagar",
                "description": "Hazardous open manhole chamber on 100ft road near metro station.",
                "category": "Drainage",
                "location": "100ft Road, Indiranagar, Ward 12",
                "latitude": 12.978412,
                "longitude": 77.640825
            },
            {
                "citizen_name": "Citizen B - Koramangala",
                "description": "Submerged street with deep stormwater flooding entering compound.",
                "category": "Waterlogging",
                "location": "80ft Road, 4th Block, Koramangala",
                "latitude": 12.935210,
                "longitude": 77.624530
            },
            {
                "citizen_name": "Citizen C - Whitefield",
                "description": "Streetlight pole sparked and light has been dark for 4 nights.",
                "category": "Streetlight",
                "location": "ITPL Main Road, Whitefield",
                "latitude": 12.969845,
                "longitude": 77.749910
            },
            {
                "citizen_name": "Citizen D - Electronic City",
                "description": "Overflowing waste container creating severe sanitary hazard on transit corridor.",
                "category": "Garbage",
                "location": "Phase 1 Toll Gate, Electronic City",
                "latitude": 12.845215,
                "longitude": 77.660235
            },
            {
                "citizen_name": "Citizen E - Malleshwaram",
                "description": "Massive road cave-in and asphalt crater damaging two-wheelers.",
                "category": "Road Damage",
                "location": "8th Cross, Sampige Road, Malleshwaram",
                "latitude": 13.003120,
                "longitude": 77.564340
            },
            {
                "citizen_name": "Citizen F - Mysuru Outstation",
                "description": "Damaged pedestrian pathway near Palace North Gate outside standard city cluster.",
                "category": "Road Damage",
                "location": "Sayyaji Rao Road, Mysuru",
                "latitude": 12.305150,
                "longitude": 76.655180
            }
        ]

        submitted_ids = []

        for loc in test_locations:
            res = self.client.post('/api/complaints/submit', data=loc)
            self.assertEqual(res.status_code, 201, f"Failed to submit from {loc['location']}: {res.data}")
            data = res.get_json()
            self.assertTrue(data['success'])
            self.assertTrue(data['tracking_id'].startswith("CIV-2026-"))
            tracking_id = data['tracking_id']
            submitted_ids.append((tracking_id, loc))

        # Query all complaints on map
        map_res = self.client.get('/api/map/complaints')
        self.assertEqual(map_res.status_code, 200)
        map_data = map_res.get_json()
        self.assertTrue(map_data['success'])

        map_complaints = {c['tracking_id']: c for c in map_data['complaints']}

        # Verify all 6 submitted complaints exist on the map and have EXACT coordinates
        for tracking_id, orig_loc in submitted_ids:
            self.assertIn(tracking_id, map_complaints, f"{tracking_id} not found on admin map!")
            saved = map_complaints[tracking_id]

            # Coordinate integrity check (no random replacement)
            self.assertAlmostEqual(saved['latitude'], orig_loc['latitude'], places=5)
            self.assertAlmostEqual(saved['longitude'], orig_loc['longitude'], places=5)
            self.assertEqual(saved['location'], orig_loc['location'])
            self.assertEqual(saved['is_synthetic'], 0) # Verified real citizen submission
            self.assertEqual(saved['status'], 'Submitted')

    def test_03_old_locations_persist_when_new_complaints_added(self):
        """Confirm older complaint locations remain visible when new complaints are submitted."""
        # Initial count
        res1 = self.client.get('/api/map/complaints')
        count_before = res1.get_json()['count']

        # Add a new complaint
        new_loc = {
            "citizen_name": "Citizen New Location",
            "description": "Dangerous pothole crater near Hebbal flyover ramp.",
            "category": "Road Damage",
            "location": "Hebbal Flyover Junction",
            "latitude": 13.035820,
            "longitude": 77.597010
        }
        submit_res = self.client.post('/api/complaints/submit', data=new_loc)
        new_tracking_id = submit_res.get_json()['tracking_id']

        # Check map count after
        res2 = self.client.get('/api/map/complaints')
        count_after = res2.get_json()['count']
        self.assertEqual(count_after, count_before + 1)

        # Confirm newly added is present
        tracking_ids = [c['tracking_id'] for c in res2.get_json()['complaints']]
        self.assertIn(new_tracking_id, tracking_ids)

    def test_04_admin_filters_and_search(self):
        """Test admin map filters: category, priority, status, source, and search query."""
        # 1. Filter by category
        res = self.client.get('/api/map/complaints?category=Waterlogging')
        data = res.get_json()
        self.assertTrue(data['success'])
        for c in data['complaints']:
            self.assertEqual(c['category'], 'Waterlogging')

        # 2. Filter by priority
        res = self.client.get('/api/map/complaints?priority=High')
        data = res.get_json()
        self.assertTrue(data['success'])
        for c in data['complaints']:
            self.assertEqual(c['ai_priority_level'], 'High')

        # 3. Filter by source (real citizen reports only)
        res_real = self.client.get('/api/map/complaints?source=real')
        data_real = res_real.get_json()
        self.assertTrue(data_real['success'])
        for c in data_real['complaints']:
            self.assertEqual(c['is_synthetic'], 0)

        # 4. Search by address
        res_search = self.client.get('/api/map/complaints?search=Malleshwaram')
        data_search = res_search.get_json()
        self.assertTrue(data_search['success'])
        self.assertGreater(data_search['count'], 0)
        for c in data_search['complaints']:
            self.assertTrue(
                'malleshwaram' in c['location'].lower() or 
                'malleshwaram' in c['citizen_name'].lower() or
                'malleshwaram' in c['tracking_id'].lower()
            )

    def test_05_missing_coordinates_workflow(self):
        """Test identifying and updating complaints that lack coordinates."""
        # Insert a complaint without coordinates to test the correction flow
        from database.db import execute_db
        import uuid
        test_tracking_id = f"CIV-TEST-NOCOORD-{uuid.uuid4().hex[:6]}"
        comp_id = execute_db("""
            INSERT INTO complaints (
                tracking_id, citizen_name, description, category, location,
                latitude, longitude, status, is_synthetic
            ) VALUES (?, 'Legacy Paper File', 'Old phone grievance without GPS', 'Streetlight', 'Town Hall Circle', NULL, NULL, 'Submitted', 0)
        """, (test_tracking_id,))

        # Query missing coordinates
        missing_res = self.client.get('/api/map/missing-coordinates')
        self.assertEqual(missing_res.status_code, 200)
        missing_data = missing_res.get_json()
        self.assertTrue(missing_data['success'])
        missing_ids = [c['id'] for c in missing_data['complaints']]
        self.assertIn(comp_id, missing_ids)

        # Update location via admin API
        update_res = self.client.post(f'/api/complaints/{comp_id}/update-location', json={
            "latitude": 12.9632,
            "longitude": 77.5841,
            "location": "Town Hall Circle, JC Road"
        })
        self.assertEqual(update_res.status_code, 200)
        self.assertTrue(update_res.get_json()['success'])

        # Verify it now appears on the all-location map
        map_res = self.client.get(f'/api/map/complaints?search={test_tracking_id}')
        map_data = map_res.get_json()
        self.assertEqual(map_data['count'], 1)
        self.assertAlmostEqual(map_data['complaints'][0]['latitude'], 12.9632, places=4)
        self.assertAlmostEqual(map_data['complaints'][0]['longitude'], 77.5841, places=4)

if __name__ == '__main__':
    unittest.main()
