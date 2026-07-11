# flight arrivals & departures fetcher

a small python script that fetches live flight arrival and departure data from public xml feeds, parses it into clean dictionaries, and prints a readable summary table for each, along with a per-airline flight count.

## what it does

1. fetches xml data from live arrivals and departures feeds:
   - `http://fis.com.mv/xml/arrive.xml`
   - `http://fis.com.mv/xml/depart.xml`
2. parses each `<Flight>` entry into a python dictionary
3. collapses the feed's separate `Route1`–`Route6` tags into a single, clean `Routes` field
4. prints a formatted table of flights for each feed (flight id, airline, routes, scheduled/estimated time, status)
5. counts and prints how many flights belong to each airline, per feed

## requirements

- python 3.7+
- [`requests`](https://pypi.org/project/requests/)

install the dependency:

```bash
pip install requests
```

no other external libraries are used — `xml.etree.ElementTree` and `collections.Counter` are both part of python's standard library.

## usage

```bash
python flights.py
```

example output:

```
--- ARRIVAL ---
FlightID  Airline             Routes              Sched   Est     Status
G9093     AIR ARABIA          SHARJAH             08:10   08:18   LA
Q2395     MALDIVIAN           BEIJING             08:10   06:31   LA
UL101     SRILANKAN AIRLINES  COLOMBO             08:15   08:35   LA
QR676     QATAR AIRWAYS       DOHA                08:25   08:50   LA
VP601     VILLA AIR           MAAMIGILI           08:30   08:24   LA
...
(93 flights total)

Flights per airline (arrival):
  MALDIVIAN: 31
  EMIRATES: 9
  MANTA AIR: 8
  FLYDUBAI: 6
  INDIGO: 5
  ...

--- DEPARTURE ---
FlightID  Airline             Routes              Sched   Est     Status
Q28140    MALDIVIAN           KAADEHDHOO          08:10   08:25   DP
FZ1025    FLYDUBAI            COLOMBO             08:15   08:47   DP
Q2192     MALDIVIAN           FUNADHOO            08:20   08:20   DP
Q2442     MALDIVIAN           KULHUDHUFFUSHI      08:25   08:35   DP
Q2182     MALDIVIAN           THIMARAFUSHI        08:50   08:57   DP
...
(94 flights total)

Flights per airline (departure):
  MALDIVIAN: 32
  EMIRATES: 9
  MANTA AIR: 9
  FLYDUBAI: 7
  ETIHAD AIRWAYS: 5
  ...
```

## the script

```python
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
```

## how it works

### `parse_feed(xml_text, tag)`

takes raw xml text and a label (`"arrival"` or `"departure"`) and returns a list of flight dictionaries.

- parses the xml with `ET.fromstring`
- finds every `<Flight>` element
- converts each flight's child tags into `{tag_name: text_value}` pairs, using an empty string for empty tags
- merges any non-empty `Route1`–`Route6` values into a single comma-separated `Routes` string
- tags each row with `FeedType` so arrivals and departures can be told apart if combined later

### `print_table(rows, label)`

takes the list of flight dictionaries and a label, then:

- prints a fixed-width table of key flight fields, using python's `:<N` string formatting for alignment
- counts flights per airline with `collections.Counter` and prints them sorted from most to least frequent

### main loop

the script loops over the `FEEDS` dictionary (arrivals and departures), fetching and parsing each with a 10 second timeout so it doesn't hang if the server is slow or unresponsive, then prints a table for each feed.

## notes

- the xml feeds reflect live data and update periodically at the source — this script simply reflects a single point-in-time snapshot each time it's run.
- no data is cached or stored between runs; for historical tracking, results would need to be logged to a file or database separately.
