"""
CivicAI - Competition Demonstration Dataset Generator (40 Synthetic Records)
Populates SQLite with 40 realistic synthetic civic complaints:
- 6 categories: Road Damage, Waterlogging, Garbage, Streetlight, Drainage, Other
- Multiple deliberate duplicate pairs with spatial & textual overlap
- Urgent safety hazards (High priority) and routine maintenance (Medium, Low)
- 4 distinct geographical hotspots (Indiranagar, Outer Ring Road, Commercial Market, Koramangala)
- Full lifecycle statuses: Submitted, Under Review, Assigned, In Progress, Resolved
- Chronological activity audit trails
- Clearly labeled as synthetic data with zero real personal information
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_db, get_db_connection, execute_db, log_activity
from ai_engine import analyze_complaint

SYNTHETIC_COMPLAINTS = [
    # =========================================================================
    # HOTSPOT 1: Indiranagar Ward 12 (Waterlogging & Drainage Crisis Cluster)
    # Center: ~12.9784, 77.6408 (9 complaints)
    # =========================================================================
    {
        "tracking_id": "CIV-2026-SYN01",
        "citizen_name": "[Synthetic] Citizen Rohan M.",
        "category": "Waterlogging",
        "location": "Indiranagar 5th Main, Near City Bank, Ward 12",
        "latitude": 12.9784,
        "longitude": 77.6408,
        "description": "Water is entering houses because of road flooding. Storm drains are overwhelmed and standing water is rising into residential living rooms.",
        "status": "In Progress",
        "assigned_department": "Stormwater & Flood Management Division",
        "assigned_officer": "Eng. Vikrant Patil",
        "created_days_ago": 3,
        "logs": [
            ("Complaint Submitted", "Citizen reported severe residential water ingress.", "[Synthetic] Citizen Rohan M."),
            ("AI Triage Completed", "Categorized as Waterlogging. Priority: High. Reason: Risk to residential properties; Potential safety hazard; Immediate attention required.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Water pumping suction truck dispatched.", "Eng. Vikrant Patil")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN02",
        "citizen_name": "[Synthetic] Citizen Karthik V.",
        "category": "Waterlogging",
        "location": "5th Main Road, Indiranagar, Ward 12",
        "latitude": 12.9788,
        "longitude": 77.6412,
        "description": "Heavy road flooding and water entering homes on Indiranagar 5th Main.",
        "status": "Submitted",
        "assigned_department": "Stormwater & Flood Management Division",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported road flooding entering homes.", "[Synthetic] Citizen Karthik V."),
            ("AI Triage Completed", "Categorized as Waterlogging. Flagged as duplicate of CIV-2026-SYN01.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN03",
        "citizen_name": "[Synthetic] Citizen Anita S.",
        "category": "Drainage",
        "location": "4th Cross Indiranagar, Near Corner Bakery, Ward 12",
        "latitude": 12.9775,
        "longitude": 77.6398,
        "description": "Stormwater drain is completely choked with silt and overflowing onto the road, worsening the flooding situation.",
        "status": "Under Review",
        "assigned_department": "Water Supply & Sewerage Board",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen reported choked stormwater drain.", "[Synthetic] Citizen Anita S."),
            ("AI Triage Completed", "Categorized as Drainage. Priority: Medium.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN04",
        "citizen_name": "[Synthetic] Citizen Harish N.",
        "category": "Drainage",
        "location": "4th Cross Road, Indiranagar, Ward 12",
        "latitude": 12.9779,
        "longitude": 77.6402,
        "description": "Choked drain gutter spilling black sewage water on 4th Cross Indiranagar.",
        "status": "Submitted",
        "assigned_department": "Water Supply & Sewerage Board",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen filed report for choked drainage gutter.", "[Synthetic] Citizen Harish N."),
            ("AI Triage Completed", "Categorized as Drainage. Flagged as duplicate of CIV-2026-SYN03.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN05",
        "citizen_name": "[Synthetic] Citizen Meenakshi R.",
        "category": "Waterlogging",
        "location": "Indiranagar 100ft Road Junction, Ward 12",
        "latitude": 12.9795,
        "longitude": 77.6420,
        "description": "Severe waterlogging at 100ft Road junction. Vehicles stuck in 2 feet deep water causing total gridlock.",
        "status": "Assigned",
        "assigned_department": "Stormwater & Flood Management Division",
        "assigned_officer": "Eng. Vikrant Patil",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen reported gridlock from deep standing water.", "[Synthetic] Citizen Meenakshi R."),
            ("AI Triage Completed", "Categorized as Waterlogging. Priority: High.", "CivicAI Engine"),
            ("Department Assigned", "Assigned to Stormwater Division for high-volume dewatering pump.", "Municipal Desk")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN06",
        "citizen_name": "[Synthetic] Citizen Suresh K.",
        "category": "Waterlogging",
        "location": "100 Feet Road Near Underpass, Indiranagar, Ward 12",
        "latitude": 12.9798,
        "longitude": 77.6423,
        "description": "Flooding on 100ft Road underpass with stranded commuters in two feet deep water.",
        "status": "Under Review",
        "assigned_department": "Stormwater & Flood Management Division",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported flooded underpass.", "[Synthetic] Citizen Suresh K."),
            ("AI Triage Completed", "Categorized as Waterlogging. Flagged as duplicate of CIV-2026-SYN05.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN07",
        "citizen_name": "[Synthetic] Citizen Tanvi B.",
        "category": "Drainage",
        "location": "Indiranagar 6th Cross, Near Bus Shelter, Ward 12",
        "latitude": 12.9770,
        "longitude": 77.6410,
        "description": "Broken drain culvert slab broken open near bus shelter. Pedestrians can fall into open drain.",
        "status": "In Progress",
        "assigned_department": "Water Supply & Sewerage Board",
        "assigned_officer": "Inspector Manoj Hegde",
        "created_days_ago": 3,
        "logs": [
            ("Complaint Submitted", "Citizen reported broken slab near bus shelter.", "[Synthetic] Citizen Tanvi B."),
            ("AI Triage Completed", "Categorized as Drainage. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Barricades placed around broken slab.", "Inspector Manoj Hegde")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN08",
        "citizen_name": "[Synthetic] Citizen Alok G.",
        "category": "Streetlight",
        "location": "Indiranagar 5th Main 8th Cross Corner, Ward 12",
        "latitude": 12.9782,
        "longitude": 77.6425,
        "description": "Streetlight base submerged in flood runoff with visible sparking near residential apartment gate.",
        "status": "Assigned",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Technician Sunil Rao",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported underwater sparking lamp post.", "[Synthetic] Citizen Alok G."),
            ("AI Triage Completed", "Categorized as Streetlight. Priority: High.", "CivicAI Engine"),
            ("Department Assigned", "Urgent electrical dispatch team sent to isolate power.", "Central Dispatch")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN09",
        "citizen_name": "[Synthetic] Citizen Divya J.",
        "category": "Waterlogging",
        "location": "Indiranagar 3rd Main Playground Edge, Ward 12",
        "latitude": 12.9768,
        "longitude": 77.6401,
        "description": "Stagnant standing pool of rain floodwater breeding mosquitoes for past 4 days on playground edge.",
        "status": "Resolved",
        "assigned_department": "Stormwater & Flood Management Division",
        "assigned_officer": "Eng. Vikrant Patil",
        "created_days_ago": 5,
        "logs": [
            ("Complaint Submitted", "Citizen reported stagnant water pool.", "[Synthetic] Citizen Divya J."),
            ("AI Triage Completed", "Categorized as Waterlogging. Priority: Low.", "CivicAI Engine"),
            ("Complaint Resolved", "Water pumped out and anti-larval chemical fogging completed.", "Eng. Vikrant Patil")
        ]
    },

    # =========================================================================
    # HOTSPOT 2: Outer Ring Road Tech Corridor (Road Damage & Potholes Hub)
    # Center: ~12.9245, 77.6840 (8 complaints)
    # =========================================================================
    {
        "tracking_id": "CIV-2026-SYN10",
        "citizen_name": "[Synthetic] Citizen Priya S.",
        "category": "Road Damage",
        "location": "Outer Ring Road Junction, Near Metro Pillar 182, Ward 22",
        "latitude": 12.9238,
        "longitude": 77.6835,
        "description": "Deep sinkhole and massive road crater on main highway carriageway. Two-wheelers are skidding and swerving dangerously.",
        "status": "In Progress",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Inspector Manoj Hegde",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen reported hazardous road crater on highway.", "[Synthetic] Citizen Priya S."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Cold mix asphalt patch deployed.", "Inspector Manoj Hegde")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN11",
        "citizen_name": "[Synthetic] Citizen Rajesh N.",
        "category": "Road Damage",
        "location": "Outer Ring Road, Near Pillar 182 Bellandur, Ward 22",
        "latitude": 12.9241,
        "longitude": 77.6839,
        "description": "Massive road crater and sinkhole near Pillar 182 Outer Ring Road two wheelers skidding dangerously.",
        "status": "Submitted",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen filed report for dangerous pothole.", "[Synthetic] Citizen Rajesh N."),
            ("AI Triage Completed", "Categorized as Road Damage. Flagged as duplicate of CIV-2026-SYN10.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN12",
        "citizen_name": "[Synthetic] Citizen Deepak C.",
        "category": "Road Damage",
        "location": "Outer Ring Road, Near Bellandur Flyover Ascent, Ward 22",
        "latitude": 12.9251,
        "longitude": 77.6854,
        "description": "Multiple severe potholes and broken asphalt surface creating extreme traffic slowdown and vehicle rim damage.",
        "status": "Assigned",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Inspector Manoj Hegde",
        "created_days_ago": 3,
        "logs": [
            ("Complaint Submitted", "Citizen reported multiple deep potholes on flyover approach.", "[Synthetic] Citizen Deepak C."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: Medium.", "CivicAI Engine"),
            ("Department Assigned", "Work order issued to East Division resurfacing unit.", "Chief Engineer")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN13",
        "citizen_name": "[Synthetic] Citizen Sandeep T.",
        "category": "Road Damage",
        "location": "Bellandur Flyover Ascent, Outer Ring Road, Ward 22",
        "latitude": 12.9254,
        "longitude": 77.6858,
        "description": "Broken bitumen and multiple potholes causing heavy traffic jam on Outer Ring Road flyover.",
        "status": "Under Review",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported broken bitumen.", "[Synthetic] Citizen Sandeep T."),
            ("AI Triage Completed", "Categorized as Road Damage. Flagged as duplicate of CIV-2026-SYN12.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN14",
        "citizen_name": "[Synthetic] Citizen Varun B.",
        "category": "Road Damage",
        "location": "Outer Ring Road Fast Lane, Near Ecospace Gate, Ward 22",
        "latitude": 12.9232,
        "longitude": 77.6828,
        "description": "Damaged concrete median barrier with sharp exposed rebar protruding into fast lane. Fatal collision risk.",
        "status": "Assigned",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Eng. Ramesh Rao",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported dangerous exposed rebar on highway.", "[Synthetic] Citizen Varun B."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: High.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN15",
        "citizen_name": "[Synthetic] Citizen Pooja M.",
        "category": "Road Damage",
        "location": "Outer Ring Road Service Road, Opp Tech Park, Ward 22",
        "latitude": 12.9260,
        "longitude": 77.6865,
        "description": "Unmarked dangerous illegal speed breaker causing spine jerks and vehicle undercarriage scrapes.",
        "status": "Under Review",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen filed complaint regarding unmarked hump.", "[Synthetic] Citizen Pooja M."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: Medium.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN16",
        "citizen_name": "[Synthetic] Citizen Nikhil D.",
        "category": "Road Damage",
        "location": "Outer Ring Road Overpass Joint, Ward 22",
        "latitude": 12.9248,
        "longitude": 77.6845,
        "description": "Cracked flyover expansion joint with loose steel plates vibrating dangerously under heavy trucks.",
        "status": "In Progress",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Eng. Ramesh Rao",
        "created_days_ago": 4,
        "logs": [
            ("Complaint Submitted", "Citizen reported loose expansion joint on flyover.", "[Synthetic] Citizen Nikhil D."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Structural inspection team dispatched.", "Eng. Ramesh Rao")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN17",
        "citizen_name": "[Synthetic] Citizen Kavita U.",
        "category": "Road Damage",
        "location": "Outer Ring Road Service Lane Corner, Ward 22",
        "latitude": 12.9228,
        "longitude": 77.6820,
        "description": "Loose gravel and crushed stone scattered all over service road causing tire slips.",
        "status": "Resolved",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Eng. Ramesh Rao",
        "created_days_ago": 6,
        "logs": [
            ("Complaint Submitted", "Citizen reported slippery gravel spill.", "[Synthetic] Citizen Kavita U."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: Low.", "CivicAI Engine"),
            ("Complaint Resolved", "Street sweeping and road vacuum crew cleared gravel.", "Eng. Ramesh Rao")
        ]
    },

    # =========================================================================
    # HOTSPOT 3: Commercial Market Shivaji Ward 5 (Garbage & Sanitation Hub)
    # Center: ~12.9835, 77.6045 (8 complaints)
    # =========================================================================
    {
        "tracking_id": "CIV-2026-SYN18",
        "citizen_name": "[Synthetic] Citizen Fatima B.",
        "category": "Garbage",
        "location": "Commercial Market Lane, Near Fish Market, Ward 5",
        "latitude": 12.9832,
        "longitude": 77.6042,
        "description": "Large pile of uncollected garbage and rotting trash dumped near the vegetable market creating terrible stench and health hazard.",
        "status": "In Progress",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Supervisor Tariq Ahmed",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen filed report regarding solid waste accumulation.", "[Synthetic] Citizen Fatima B."),
            ("AI Triage Completed", "Categorized as Garbage. Priority: Medium.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Sanitation compactor dispatched.", "Supervisor Tariq Ahmed")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN19",
        "citizen_name": "[Synthetic] Citizen Zeeshan K.",
        "category": "Garbage",
        "location": "Fish Market Cross Road, Shivaji Market, Ward 5",
        "latitude": 12.9835,
        "longitude": 77.6046,
        "description": "Rotting uncollected garbage pile and foul waste near Shivaji vegetable market walkway.",
        "status": "Submitted",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported foul waste near market.", "[Synthetic] Citizen Zeeshan K."),
            ("AI Triage Completed", "Categorized as Garbage. Flagged as duplicate of CIV-2026-SYN18.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN20",
        "citizen_name": "[Synthetic] Citizen Mohammed Z.",
        "category": "Garbage",
        "location": "Old Market Cross Road, Opposite Meat Stall, Ward 5",
        "latitude": 12.9841,
        "longitude": 77.6052,
        "description": "Commercial waste dumping and public dustbins overflowing on the pedestrian pathway since weekend.",
        "status": "Assigned",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Supervisor Tariq Ahmed",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen filed grievance for bin overflow.", "[Synthetic] Citizen Mohammed Z."),
            ("AI Triage Completed", "Categorized as Garbage. Priority: Medium.", "CivicAI Engine"),
            ("Department Assigned", "Assigned to Ward 5 sanitation tipper truck.", "Sanitation Officer")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN21",
        "citizen_name": "[Synthetic] Citizen Ayesha M.",
        "category": "Garbage",
        "location": "Opposite Meat Stall Lane, Shivaji Ward 5",
        "latitude": 12.9843,
        "longitude": 77.6055,
        "description": "Overflowing waste bins and commercial trash blocking sidewalk near market opposite meat stall.",
        "status": "Submitted",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 0,
        "logs": [
            ("Complaint Submitted", "Citizen reported blocked sidewalk from trash bins.", "[Synthetic] Citizen Ayesha M."),
            ("AI Triage Completed", "Categorized as Garbage. Flagged as duplicate of CIV-2026-SYN20.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN22",
        "citizen_name": "[Synthetic] Citizen Imran S.",
        "category": "Garbage",
        "location": "Market Back Alley Behind Food Stalls, Ward 5",
        "latitude": 12.9828,
        "longitude": 77.6038,
        "description": "Dead animal carcass and rotting organic fish waste dumped beside food stalls posing severe contagion risk and vermin infestation.",
        "status": "In Progress",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Health Inspector Arvind Roy",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported hazardous bio-waste contamination.", "[Synthetic] Citizen Imran S."),
            ("AI Triage Completed", "Categorized as Garbage. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Bio-hazard removal crew on-site.", "Health Inspector Arvind Roy")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN23",
        "citizen_name": "[Synthetic] Citizen Salma P.",
        "category": "Garbage",
        "location": "Market West Entry Gate, Ward 5",
        "latitude": 12.9848,
        "longitude": 77.6060,
        "description": "Construction debris and concrete rubble illegally dumped on market access road preventing delivery carts.",
        "status": "Under Review",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 3,
        "logs": [
            ("Complaint Submitted", "Citizen filed report for debris obstruction.", "[Synthetic] Citizen Salma P."),
            ("AI Triage Completed", "Categorized as Garbage. Priority: Low.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN24",
        "citizen_name": "[Synthetic] Citizen Bilal T.",
        "category": "Garbage",
        "location": "Fruit Stall Lane Drainage Edge, Ward 5",
        "latitude": 12.9830,
        "longitude": 77.6049,
        "description": "Plastic bottles and single-use polythene bags clogging the open gutter near fruit stalls causing foul stagnation.",
        "status": "Assigned",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Supervisor Tariq Ahmed",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen reported gutter choke from plastic trash.", "[Synthetic] Citizen Bilal T."),
            ("AI Triage Completed", "Categorized as Garbage. Priority: Medium.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN25",
        "citizen_name": "[Synthetic] Citizen Rehana B.",
        "category": "Garbage",
        "location": "South End Commercial Street, Ward 5",
        "latitude": 12.9822,
        "longitude": 77.6032,
        "description": "Public community bin broken and overturned with garbage scattered over 50 meters of street.",
        "status": "Resolved",
        "assigned_department": "Solid Waste & Sanitation Department",
        "assigned_officer": "Supervisor Tariq Ahmed",
        "created_days_ago": 5,
        "logs": [
            ("Complaint Submitted", "Citizen reported broken metal bin.", "[Synthetic] Citizen Rehana B."),
            ("AI Triage Completed", "Categorized as Garbage. Priority: Low.", "CivicAI Engine"),
            ("Complaint Resolved", "New 240L wheelie bin installed and area swept clean.", "Supervisor Tariq Ahmed")
        ]
    },

    # =========================================================================
    # HOTSPOT 4: Koramangala 4th Block Ward 15 (Streetlight & Electrical Hub)
    # Center: ~12.9345, 77.6250 (6 complaints)
    # =========================================================================
    {
        "tracking_id": "CIV-2026-SYN26",
        "citizen_name": "[Synthetic] Citizen Arun K.",
        "category": "Streetlight",
        "location": "Koramangala 4th Block, 10th Main, Near Park Gate, Ward 15",
        "latitude": 12.9340,
        "longitude": 77.6245,
        "description": "Live electrical wire dangling from broken streetlight pole sparking near primary school gate. Extreme electrocution risk.",
        "status": "In Progress",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Chief Lineman Satish Gowda",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported sparking live wire near school.", "[Synthetic] Citizen Arun K."),
            ("AI Triage Completed", "Categorized as Streetlight. Priority: High. Reason: Severe public electrocution hazard; Emergency repair required.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Power feeder isolated and lineman on-site.", "Chief Lineman Satish Gowda")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN27",
        "citizen_name": "[Synthetic] Citizen Shreya V.",
        "category": "Streetlight",
        "location": "10th Main Near Park Gate, Koramangala, Ward 15",
        "latitude": 12.9343,
        "longitude": 77.6248,
        "description": "Broken streetlight pole with sparking live wire hanging near school entrance.",
        "status": "Submitted",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 0,
        "logs": [
            ("Complaint Submitted", "Citizen reported broken sparking pole.", "[Synthetic] Citizen Shreya V."),
            ("AI Triage Completed", "Categorized as Streetlight. Flagged as duplicate of CIV-2026-SYN26.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN28",
        "citizen_name": "[Synthetic] Citizen Raghavan P.",
        "category": "Streetlight",
        "location": "80ft Road Koramangala 4th Block, Ward 15",
        "latitude": 12.9352,
        "longitude": 77.6258,
        "description": "Entire stretch of 8 streetlights non-functional on 80ft Road Koramangala causing pitch black corridor and safety concern for women commuters.",
        "status": "Assigned",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Chief Lineman Satish Gowda",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen filed report for dark road stretch.", "[Synthetic] Citizen Raghavan P."),
            ("AI Triage Completed", "Categorized as Streetlight. Priority: Medium.", "CivicAI Engine"),
            ("Department Assigned", "Assigned to BESCOM electrical contractor.", "Assistant Executive Engineer")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN29",
        "citizen_name": "[Synthetic] Citizen Preeti K.",
        "category": "Streetlight",
        "location": "80 Feet Road, Koramangala 4th Block, Ward 15",
        "latitude": 12.9355,
        "longitude": 77.6261,
        "description": "Streetlights completely dark on 80ft road Koramangala for past week.",
        "status": "Submitted",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported blackout on street.", "[Synthetic] Citizen Preeti K."),
            ("AI Triage Completed", "Categorized as Streetlight. Flagged as duplicate of CIV-2026-SYN28.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN30",
        "citizen_name": "[Synthetic] Citizen Manoj D.",
        "category": "Streetlight",
        "location": "Koramangala 4th Block Community Ground, Ward 15",
        "latitude": 12.9335,
        "longitude": 77.6238,
        "description": "Exposed junction box on lamp post with open fuse panel accessible to children in park.",
        "status": "Under Review",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen reported open fuse box.", "[Synthetic] Citizen Manoj D."),
            ("AI Triage Completed", "Categorized as Streetlight. Priority: High.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN31",
        "citizen_name": "[Synthetic] Citizen Sneha R.",
        "category": "Streetlight",
        "location": "7th Cross Koramangala 4th Block, Ward 15",
        "latitude": 12.9360,
        "longitude": 77.6268,
        "description": "Flickering sodium vapor lamp creating blinding strobe effect for approaching vehicles.",
        "status": "Resolved",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Chief Lineman Satish Gowda",
        "created_days_ago": 6,
        "logs": [
            ("Complaint Submitted", "Citizen reported blinking lamp.", "[Synthetic] Citizen Sneha R."),
            ("AI Triage Completed", "Categorized as Streetlight. Priority: Low.", "CivicAI Engine"),
            ("Complaint Resolved", "Old bulb replaced with new 90W LED fitting.", "Chief Lineman Satish Gowda")
        ]
    },

    # =========================================================================
    # SCATTERED MUNICIPAL INCIDENTS (Wards across Bangalore - 9 complaints)
    # =========================================================================
    {
        "tracking_id": "CIV-2026-SYN32",
        "citizen_name": "[Synthetic] Citizen David F.",
        "category": "Drainage",
        "location": "12th Main Road, Silver Oaks Layout, BTM Ward 18",
        "latitude": 12.9121,
        "longitude": 77.6098,
        "description": "Open manhole with missing broken lid submerged in murky water right next to the school walking path. High risk of child injury.",
        "status": "In Progress",
        "assigned_department": "Water Supply & Sewerage Board",
        "assigned_officer": "Officer Rajesh Varma",
        "created_days_ago": 3,
        "logs": [
            ("Complaint Submitted", "Citizen reported missing manhole cover.", "[Synthetic] Citizen David F."),
            ("AI Triage Completed", "Categorized as Drainage. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Emergency barricading placed.", "Officer Rajesh Varma")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN33",
        "citizen_name": "[Synthetic] Citizen Sunita D.",
        "category": "Drainage",
        "location": "7th Cross, Malleshwaram, Ward 8",
        "latitude": 13.0031,
        "longitude": 77.5643,
        "description": "Open sewer line overflowing with raw human effluent onto residential lane in Malleshwaram 7th Cross.",
        "status": "Assigned",
        "assigned_department": "Water Supply & Sewerage Board",
        "assigned_officer": "Inspector Vinod Kumar",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen reported sewage leak on residential street.", "[Synthetic] Citizen Sunita D."),
            ("AI Triage Completed", "Categorized as Drainage. Priority: High.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN34",
        "citizen_name": "[Synthetic] Citizen Ramesh T.",
        "category": "Drainage",
        "location": "Jayanagar 4th T Block, 14th Main, Ward 16",
        "latitude": 12.9298,
        "longitude": 77.5832,
        "description": "Underground drinking water supply pipeline burst shooting clean potable water 15 feet high wasting thousands of liters.",
        "status": "In Progress",
        "assigned_department": "Water Supply & Sewerage Board",
        "assigned_officer": "Engineer S. Murthy",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported high-pressure water pipe burst.", "[Synthetic] Citizen Ramesh T."),
            ("AI Triage Completed", "Categorized as Drainage. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Sluice valve shut off to contain water loss.", "Engineer S. Murthy")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN35",
        "citizen_name": "[Synthetic] Citizen Vinay H.",
        "category": "Other",
        "location": "Whitefield Main Road, Near ITPL Gate 3, Ward 28",
        "latitude": 12.9865,
        "longitude": 77.7289,
        "description": "Fallen massive banyan tree branch blocking both lanes of Whitefield Main Road after squall storm.",
        "status": "Assigned",
        "assigned_department": "General Municipal Administration",
        "assigned_officer": "Forest Wing Officer C. Joseph",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported fallen heavy branch blocking arterial road.", "[Synthetic] Citizen Vinay H."),
            ("AI Triage Completed", "Categorized as Other. Priority: High.", "CivicAI Engine"),
            ("Department Assigned", "Chainsaw crew and crane mobilized for wood clearing.", "Forest Wing Officer C. Joseph")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN36",
        "citizen_name": "[Synthetic] Citizen Rashmi C.",
        "category": "Other",
        "location": "Rajajinagar 3rd Block Community Park, Ward 10",
        "latitude": 12.9912,
        "longitude": 77.5534,
        "description": "Damaged children swing set with broken rusty metal chains in Rajajinagar community park.",
        "status": "Submitted",
        "assigned_department": "General Municipal Administration",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 2,
        "logs": [
            ("Complaint Submitted", "Citizen filed report for broken park playground swing.", "[Synthetic] Citizen Rashmi C."),
            ("AI Triage Completed", "Categorized as Other. Priority: Low.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN37",
        "citizen_name": "[Synthetic] Citizen Arvind G.",
        "category": "Other",
        "location": "MG Road Trinity Junction, Ward 14",
        "latitude": 12.9734,
        "longitude": 77.6189,
        "description": "Traffic signal light permanently stuck on red at MG Road Trinity junction causing huge gridlock and confusion.",
        "status": "In Progress",
        "assigned_department": "Public Lighting & Electrical Works",
        "assigned_officer": "Traffic Systems Tech Ravi S.",
        "created_days_ago": 1,
        "logs": [
            ("Complaint Submitted", "Citizen reported frozen traffic signal controller.", "[Synthetic] Citizen Arvind G."),
            ("AI Triage Completed", "Categorized as Other. Priority: High.", "CivicAI Engine"),
            ("Status Updated", "Status changed to In Progress. Manual signal override enabled.", "Traffic Systems Tech Ravi S.")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN38",
        "citizen_name": "[Synthetic] Citizen Shilpa B.",
        "category": "Other",
        "location": "Majestic Skywalk Overpass, Platform Road, Ward 7",
        "latitude": 12.9772,
        "longitude": 77.5714,
        "description": "Broken public handrail on pedestrian skywalk with missing glass panel near railway station.",
        "status": "Under Review",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 3,
        "logs": [
            ("Complaint Submitted", "Citizen reported missing handrail panel.", "[Synthetic] Citizen Shilpa B."),
            ("AI Triage Completed", "Categorized as Other. Priority: Medium.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN39",
        "citizen_name": "[Synthetic] Citizen Kiran J.",
        "category": "Other",
        "location": "Yeshwanthpur Market Lane, Ward 6",
        "latitude": 13.0224,
        "longitude": 77.5489,
        "description": "Pack of aggressive stray dogs chasing two-wheelers and pedestrians near municipal dispensary.",
        "status": "Submitted",
        "assigned_department": "General Municipal Administration",
        "assigned_officer": "Pending Assignment",
        "created_days_ago": 0,
        "logs": [
            ("Complaint Submitted", "Citizen reported aggressive canine behavior.", "[Synthetic] Citizen Kiran J."),
            ("AI Triage Completed", "Categorized as Other. Priority: Low.", "CivicAI Engine")
        ]
    },
    {
        "tracking_id": "CIV-2026-SYN40",
        "citizen_name": "[Synthetic] Citizen Manjunath K.",
        "category": "Road Damage",
        "location": "General Post Office Road, Ward 1",
        "latitude": 12.9754,
        "longitude": 77.5982,
        "description": "Pothole filled and road surface restored near Central Post Office. Inspection confirmed and work verified.",
        "status": "Resolved",
        "assigned_department": "Department of Roads & Infrastructure",
        "assigned_officer": "Eng. Ramesh Rao",
        "created_days_ago": 7,
        "logs": [
            ("Complaint Submitted", "Citizen reported road damage near GPO.", "[Synthetic] Citizen Manjunath K."),
            ("AI Triage Completed", "Categorized as Road Damage. Priority: Low.", "CivicAI Engine"),
            ("Complaint Resolved", "Road patch resurfacing completed with dense bitumen concrete.", "Eng. Ramesh Rao")
        ]
    }
]

def seed_database(skip_init=False):
    """Seeds exactly 40 synthetic complaints into SQLite."""
    print("="*70)
    print("INITIALIZING CIVICAI DEMONSTRATION DATASET (40 SYNTHETIC COMPLAINTS)")
    print("="*70)
    if not skip_init:
        init_db(auto_seed=False)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activity_logs")
        cursor.execute("DELETE FROM complaints")
        conn.commit()
    finally:
        conn.close()

    seeded_records = []
    category_counts = {}
    priority_counts = {}
    status_counts = {}
    duplicate_count = 0

    for idx, item in enumerate(SYNTHETIC_COMPLAINTS, 1):
        analysis = analyze_complaint(
            description=item["description"],
            location=item["location"],
            category=item["category"],
            existing_complaints=seeded_records
        )

        query = """
            INSERT INTO complaints (
                tracking_id, citizen_name, description, category, location,
                latitude, longitude,
                status, assigned_department, assigned_officer,
                ai_category, ai_category_confidence, ai_summary,
                ai_priority_score, ai_priority_level, ai_priority_explanation,
                ai_duplicate_of, ai_duplicate_score, ai_duplicate_notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', ?), datetime('now', ?))
        """
        days_offset = f"-{item['created_days_ago']} days"

        comp_id = execute_db(query, (
            item["tracking_id"],
            item["citizen_name"],
            item["description"],
            analysis["category"],
            item["location"],
            item.get("latitude"),
            item.get("longitude"),
            item["status"],
            item["assigned_department"],
            item["assigned_officer"],
            analysis["ai_category"],
            analysis["ai_category_confidence"],
            analysis["ai_summary"],
            analysis["ai_priority_score"],
            analysis["ai_priority_level"],
            analysis["ai_priority_explanation"],
            analysis["ai_duplicate_of"],
            analysis["ai_duplicate_score"],
            analysis["ai_duplicate_notes"],
            days_offset,
            days_offset
        ))

        for action, details, actor in item["logs"]:
            log_activity(comp_id, action, details, actor)

        seeded_records.append({
            "id": comp_id,
            "tracking_id": item["tracking_id"],
            "description": item["description"],
            "location": item["location"],
            "category": analysis["category"],
            "status": item["status"],
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude")
        })

        # Statistics
        c_cat = analysis["category"]
        category_counts[c_cat] = category_counts.get(c_cat, 0) + 1
        p_lvl = analysis["ai_priority_level"]
        priority_counts[p_lvl] = priority_counts.get(p_lvl, 0) + 1
        s_stat = item["status"]
        status_counts[s_stat] = status_counts.get(s_stat, 0) + 1
        if analysis["is_duplicate"]:
            duplicate_count += 1

    print(f"\nSuccessfully seeded {len(SYNTHETIC_COMPLAINTS)} synthetic complaints!")
    print(f"\nCategory Distribution: {category_counts}")
    print(f"Priority Distribution: {priority_counts}")
    print(f"Status Distribution:   {status_counts}")
    print(f"Detected Duplicates:   {duplicate_count}")
    print("="*70)

if __name__ == "__main__":
    seed_database()
