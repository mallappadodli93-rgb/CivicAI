"""
CivicAI - GIS Hotspot Detection Engine
Clusters geospatial complaint coordinates using Haversine distance
to identify concentrated municipal problem zones, dominant failure modes,
and elevated priority hotspots for field deployment.
"""
import math
from collections import Counter

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def detect_hotspots(complaints, radius_km=0.85, min_complaints=2):
    """
    Identifies geographic clusters of complaints within radius_km.
    Returns structured list of municipal hotspots with centroid,
    dominant category, and severity assessment.
    """
    valid_points = []
    for c in complaints:
        lat = c.get("latitude")
        lng = c.get("longitude")
        if lat is not None and lng is not None:
            try:
                lat_f = float(lat)
                lng_f = float(lng)
                if -90.0 <= lat_f <= 90.0 and -180.0 <= lng_f <= 180.0:
                    valid_points.append({
                        "id": c.get("id"),
                        "tracking_id": c.get("tracking_id"),
                        "citizen_name": c.get("citizen_name"),
                        "category": c.get("category"),
                        "location": c.get("location"),
                        "lat": lat_f,
                        "lng": lng_f,
                        "priority": c.get("ai_priority_level", "Medium"),
                        "status": c.get("status", "Submitted"),
                        "summary": c.get("ai_summary", "")
                    })
            except (ValueError, TypeError):
                continue

    if len(valid_points) < min_complaints:
        return []

    # Density-based clustering
    clusters = []
    visited = set()

    for i, p in enumerate(valid_points):
        if i in visited:
            continue

        cluster = [p]
        visited.add(i)

        for j, other in enumerate(valid_points):
            if j in visited:
                continue

            dist = haversine_distance_km(p["lat"], p["lng"], other["lat"], other["lng"])
            if dist <= radius_km:
                cluster.append(other)
                visited.add(j)

        if len(cluster) >= min_complaints:
            clusters.append(cluster)

    hotspots = []
    for idx, cluster in enumerate(clusters, 1):
        lats = [pt["lat"] for pt in cluster]
        lngs = [pt["lng"] for pt in cluster]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)

        # Calculate max distance to centroid for radius in meters
        max_dist_m = max(haversine_distance_km(center_lat, center_lng, pt["lat"], pt["lng"]) * 1000 for pt in cluster)
        visual_radius_meters = max(350, int(max_dist_m + 80))

        # Dominant category calculation
        categories = [pt["category"] for pt in cluster]
        cat_counts = Counter(categories)
        dominant_category = cat_counts.most_common(1)[0][0]

        # Severity determination
        priorities = [pt["priority"] for pt in cluster]
        if "High" in priorities or "Critical" in priorities:
            severity = "High"
            severity_label = "Critical Hotspot"
        elif "Medium" in priorities:
            severity = "Medium"
            severity_label = "Moderate Hotspot"
        else:
            severity = "Low"
            severity_label = "Minor Hotspot"

        # Determine prominent locality name from locations in cluster
        common_locations = [pt["location"] for pt in cluster]
        area_name = common_locations[0].split(",")[0].strip() if common_locations else f"Municipal Zone #{idx}"

        hotspots.append({
            "hotspot_id": f"HOTSPOT-0{idx}",
            "name": f"{area_name} Cluster",
            "center_lat": round(center_lat, 6),
            "center_lng": round(center_lng, 6),
            "radius_meters": visual_radius_meters,
            "complaint_count": len(cluster),
            "dominant_category": dominant_category,
            "category_breakdown": dict(cat_counts),
            "severity": severity,
            "severity_label": severity_label,
            "complaint_ids": [pt["tracking_id"] for pt in cluster],
            "complaints": cluster,
            "summary": (
                f"{len(cluster)} complaints concentrated within {visual_radius_meters}m zone. "
                f"Primary issue: {dominant_category}. Severity: {severity_label}."
            )
        })

    # Sort hotspots by severity and complaint count
    severity_order = {"High": 3, "Medium": 2, "Low": 1}
    hotspots.sort(key=lambda h: (severity_order.get(h["severity"], 0), h["complaint_count"]), reverse=True)

    return hotspots

