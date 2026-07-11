import requests
import xml.etree.ElementTree as ET
from collections import Counter

FEEDS = {
    "arrival": "http://fis.com.mv/xml/arrive.xml",
    "departure": "http://fis.com.mv/xml/depart.xml",
}

def parse_feed(xml_text, tag):
    root = ET.fromstring(xml_text)
    rows = []
    for flight_el in root.findall("Flight"):
        d = {c.tag: (c.text.strip() if c.text else "") for c in flight_el}
        routes = [d.pop(f"Route{i}") for i in range(1, 7) if d.get(f"Route{i}")]
        d["Routes"] = ", ".join(routes)
        d["FeedType"] = tag
        rows.append(d)
    return rows

def print_table(rows, label):
    print(f"\n--- {label.upper()} ---")
    print(f"{'FlightID':<10}{'Airline':<20}{'Routes':<20}{'Sched':<8}{'Est':<8}{'Status':<10}")
    for r in rows:
        print(f"{r['FlightID']:<10}{r['AirLineName']:<20}{r['Routes']:<20}{r['Scheduled']:<8}{r['Estimated']:<8}{r['Status']:<10}")

    counts = Counter(r["AirLineName"] for r in rows)
    print(f"\nFlights per airline ({label}):")
    for airline, n in counts.most_common():
        print(f"  {airline}: {n}")

for feed_type, url in FEEDS.items():
    resp = requests.get(url, timeout=10)
    rows = parse_feed(resp.text, feed_type)
    print_table(rows, feed_type)