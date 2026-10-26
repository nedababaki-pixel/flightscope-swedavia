"""Fictional demo flights shaped exactly like a Swedavia FlightInfo v2 response.

The demo payload goes through the same ``normalize_payload`` parser as live data,
so Demo mode also exercises the real API mapping. Flight numbers, times, gates and
statuses are generated, not real. The UI labels them clearly as DEMO.
"""
import random
from datetime import datetime, time, timedelta, timezone

from swedavia_client import AIRPORTS, SWEDEN

# (airline IATA, airline name, destination IATA, destination English name, region D/S/I)
_INTERNATIONAL = [
    ('SK', 'SAS', 'CPH', 'Copenhagen', 'S'), ('DY', 'Norwegian', 'OSL', 'Oslo', 'S'),
    ('AY', 'Finnair', 'HEL', 'Helsinki', 'S'), ('KL', 'KLM', 'AMS', 'Amsterdam', 'S'),
    ('LH', 'Lufthansa', 'FRA', 'Frankfurt', 'S'), ('AF', 'Air France', 'CDG', 'Paris', 'S'),
    ('BA', 'British Airways', 'LHR', 'London Heathrow', 'I'), ('LH', 'Lufthansa', 'MUC', 'Munich', 'S'),
    ('TK', 'Turkish Airlines', 'IST', 'Istanbul', 'I'), ('VY', 'Vueling', 'BCN', 'Barcelona', 'S'),
    ('EK', 'Emirates', 'DXB', 'Dubai', 'I'), ('FI', 'Icelandair', 'KEF', 'Reykjavik', 'S'),
]
_DOMESTIC = {
    'ARN': ('SK', 'SAS', 'Stockholm Arlanda'), 'BMA': ('TF', 'BRA', 'Stockholm Bromma'),
    'GOT': ('SK', 'SAS', 'Göteborg Landvetter'), 'MMX': ('SK', 'SAS', 'Malmö'),
    'LLA': ('SK', 'SAS', 'Luleå'), 'UME': ('SK', 'SAS', 'Umeå'),
    'OSD': ('TF', 'BRA', 'Åre Östersund'), 'VBY': ('TF', 'BRA', 'Visby'),
    'RNB': ('SK', 'SAS', 'Ronneby'), 'KRN': ('SK', 'SAS', 'Kiruna'),
}
_ROUTES = {
    'ARN': ['GOT', 'MMX', 'LLA', 'UME', 'KRN', 'VBY', 'OSD', 'RNB'],
    'BMA': ['GOT', 'MMX', 'UME', 'VBY', 'OSD', 'LLA'],
    'GOT': ['ARN', 'BMA', 'UME', 'LLA', 'VBY'],
    'MMX': ['ARN', 'BMA', 'UME', 'LLA', 'VBY'],
    'LLA': ['ARN', 'BMA', 'GOT', 'MMX', 'KRN'],
    'UME': ['ARN', 'BMA', 'GOT', 'MMX'],
    'OSD': ['ARN', 'BMA', 'GOT'],
    'VBY': ['ARN', 'BMA', 'GOT', 'MMX'],
    'RNB': ['ARN', 'BMA'],
    'KRN': ['ARN', 'LLA'],
}
_INTERNATIONAL_COUNT = {'ARN': 12, 'GOT': 8, 'MMX': 4, 'BMA': 2}
_FLIGHTS_PER_DAY = {'ARN': 28, 'GOT': 20, 'MMX': 16, 'BMA': 16}


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if dt else None


def build_demo_payload(airport, direction, day, now=None):
    """Return a fictional FlightInfo v2-style payload for one airport, direction and date.

    The same inputs always give the same flights; statuses are derived from ``now``
    so flights earlier in the day show as departed/landed.
    """
    now = now or datetime.now(timezone.utc)
    rng = random.Random(f'{airport}|{direction}|{day.isoformat()}')
    count = _FLIGHTS_PER_DAY.get(airport, 9)

    pool = []
    for code in _ROUTES[airport]:
        airline_iata, airline_name, city = _DOMESTIC[code]
        if 'BMA' in (airport, code):
            airline_iata, airline_name = 'TF', 'BRA'
        pool.append((airline_iata, airline_name, code, city, 'D'))
    pool += _INTERNATIONAL[:_INTERNATIONAL_COUNT.get(airport, 0)]

    start = datetime.combine(day, time(6, 0), tzinfo=SWEDEN)
    span_minutes = 16 * 60 + 30  # 06:00 – 22:30 local time
    slots = sorted(rng.sample(range(0, span_minutes, 5), count))
    cancelled_index = rng.randrange(count) if count >= 8 else -1
    is_departure = direction == 'departures'
    used_numbers = set()

    flights = []
    for i, minute in enumerate(slots):
        airline_iata, airline_name, city_iata, city, region = pool[i % len(pool)] if i < len(pool) else rng.choice(pool)
        number = rng.randint(100, 2999)
        while (airline_iata, number) in used_numbers:
            number += 1
        used_numbers.add((airline_iata, number))
        scheduled = start + timedelta(minutes=minute)
        delay = rng.choice([0] * 6 + [5, 20, 35, 55])
        estimated = scheduled + timedelta(minutes=delay) if delay else None
        effective = estimated or scheduled

        code, text, actual, gate_action, gate_text = 'SCH', 'Scheduled', None, None, None
        if i == cancelled_index:
            code, text, estimated = 'CAN', 'Cancelled', None
        elif effective < now - timedelta(minutes=10):
            actual = effective
            code, text = ('ACT', 'Departed') if is_departure else ('LAN', 'Landed')
        elif is_departure and effective - now < timedelta(minutes=35):
            gate_action, gate_text = 'O', 'Boarding'
        elif delay >= 15:
            text = 'New time'

        terminal = ('4' if region == 'D' else '5') if airport == 'ARN' else ('2' if airport == 'GOT' else '1')
        gate = f'{rng.choice("FG" if region != "D" else "AB")}{rng.randint(1, 38)}'
        flight = {
            'flightId': f'{airline_iata}{number}',
            'airlineOperator': {'iata': airline_iata, 'icao': None, 'name': airline_name},
            ('arrivalAirportEnglish' if is_departure else 'departureAirportEnglish'): city,
            ('arrivalAirportSwedish' if is_departure else 'departureAirportSwedish'): city,
            ('departureTime' if is_departure else 'arrivalTime'): {
                'scheduledUtc': _iso(scheduled), 'estimatedUtc': _iso(estimated), 'actualUtc': _iso(actual)},
            'locationAndStatus': {
                'terminal': terminal, 'gate': gate, 'flightLegStatus': code,
                'flightLegStatusEnglish': text, 'flightLegStatusSwedish': text,
                'gateAction': gate_action, 'gateActionEnglish': gate_text,
            },
            'codeShareData': [f'{rng.choice(["LH", "AC", "UA", "TP"])}{rng.randint(5000, 9999)}'] if rng.random() < 0.25 else [],
            'remarksEnglish': [{'text': 'Contact airline', 'indicator': 'I'}] if code == 'CAN' else [],
            'viaDestinations': [],
            'diIndicator': region,
        }
        if is_departure:
            desk = rng.randint(1, 60)
            flight['checkIn'] = {'checkInStatus': None, 'checkInDeskFrom': desk, 'checkInDeskTo': desk + 3}
        else:
            flight['baggage'] = {'baggageClaimUnit': str(rng.randint(1, 9))}
        flights.append(flight)

    key = 'from' if is_departure else 'to'
    return {
        key: {'airportIata': airport, 'airportEnglish': AIRPORTS[airport]},
        'numberOfFlights': len(flights),
        'flights': flights,
    }
