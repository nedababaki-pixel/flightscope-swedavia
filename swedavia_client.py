"""Client and response normalizer for the Swedavia FlightInfo API v2.

Verified against Swedavia's official document "Using the FlightInfo API V2"
(model version 2.0.0), available from https://apideveloper.swedavia.se/documentation

    GET https://api.swedavia.se/flightinfo/v2/{airportIATA}/arrivals/{yyyy-mm-dd}
    GET https://api.swedavia.se/flightinfo/v2/{airportIATA}/departures/{yyyy-mm-dd}
    Header: Ocp-Apim-Subscription-Key: <your key>

All times in the response are UTC. Status lives in ``locationAndStatus``
(``flightLegStatus`` code + ``flightLegStatusEnglish`` text) and the gate in
``locationAndStatus.gate``.
"""
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

BASE_URL = 'https://api.swedavia.se/flightinfo/v2'
SWEDEN = ZoneInfo('Europe/Stockholm')
REQUEST_TIMEOUT = 15          # seconds
CACHE_TTL = 60                # seconds; avoids hitting the API on every click
DELAY_THRESHOLD_MIN = 15      # estimated time this late or more counts as "delayed"

# Official IATA codes for Swedavia's ten airports (section 1.3.1 of the API guide).
AIRPORTS = {
    'ARN': 'Stockholm Arlanda',
    'BMA': 'Stockholm Bromma',
    'GOT': 'Göteborg Landvetter',
    'MMX': 'Malmö',
    'LLA': 'Luleå',
    'UME': 'Umeå',
    'OSD': 'Åre Östersund',
    'VBY': 'Visby',
    'RNB': 'Ronneby',
    'KRN': 'Kiruna',
}
DIRECTIONS = ('departures', 'arrivals')

# FlightLegStatus codes from the API model appendix.
STATUS_CODES = {
    'SCH': 'Scheduled', 'FPL': 'Flight plan', 'FLS': 'Suspended', 'SEQ': 'Sequenced',
    'ACT': 'Active', 'CAN': 'Cancelled', 'LAN': 'Landed', 'RER': 'Rerouted',
    'DIV': 'Diverted', 'DEL': 'Deleted',
}
_GENERIC_TEXTS = {'', 'scheduled', 'flight plan', 'sequenced', 'new time', 'active'}


class FlightApiError(Exception):
    """A user-safe error message plus the HTTP status our API should return."""

    def __init__(self, message, status=502):
        super().__init__(message)
        self.message = message
        self.status = status


def field(obj, name, default=None):
    """Case-insensitive dict lookup (the API document uses PascalCase, JSON uses camelCase)."""
    if not isinstance(obj, dict):
        return default
    if name in obj:
        return obj[name]
    lowered = name.lower()
    for key, value in obj.items():
        if isinstance(key, str) and key.lower() == lowered:
            return value
    return default


def parse_utc(value):
    """Parse an ISO-8601 timestamp into an aware UTC datetime, or None."""
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def local_hhmm(dt):
    """Format a datetime as HH:MM in Swedish local time, or None."""
    return dt.astimezone(SWEDEN).strftime('%H:%M') if dt else None


def formatted_time(value):
    """Return HH:MM in Sweden for an ISO timestamp, or an em dash if missing/malformed."""
    return local_hhmm(parse_utc(value)) or '—'


def _text(value):
    return value.strip() if isinstance(value, str) else ''


def classify(direction, code, scheduled, estimated, actual, gate_action):
    """Return (category, delay_minutes). Categories drive the UI colours and filters."""
    delay = 0
    if scheduled and (estimated or actual):
        delay = max(0, round(((actual or estimated) - scheduled).total_seconds() / 60))
    if code in ('CAN', 'FLS'):
        return 'cancelled', delay
    if code in ('DIV', 'RER'):
        return 'diverted', delay
    if code == 'LAN' or (direction == 'arrivals' and actual):
        return 'landed', delay
    if direction == 'departures' and (actual or code == 'ACT'):
        return 'departed', delay
    if delay >= DELAY_THRESHOLD_MIN:
        return 'delayed', delay
    if direction == 'departures' and _text(gate_action).upper() == 'O':
        return 'boarding', delay
    return 'on-time', delay


def status_label(category, api_text, delay, gate_text=''):
    """Prefer Swedavia's English status text, but make derived states readable."""
    text = _text(api_text)
    if category == 'delayed' and text.lower() in _GENERIC_TEXTS:
        return f'Delayed {delay} min'
    if category == 'boarding' and text.lower() in _GENERIC_TEXTS:
        return _text(gate_text) or 'Gate open'
    if text:
        return text
    return {'on-time': 'On time', 'departed': 'Departed', 'landed': 'Landed',
            'cancelled': 'Cancelled', 'diverted': 'Diverted', 'boarding': 'Gate open'}.get(category, category.title())


def normalize_flight(flight, direction):
    """Map one FlightInfo v2 flight object to the stable shape used by the frontend.

    Returns None for flights the API marks as deleted (DEL).
    """
    if not isinstance(flight, dict):
        return None
    times = field(flight, 'departureTime' if direction == 'departures' else 'arrivalTime') or {}
    loc = field(flight, 'locationAndStatus') or {}
    airline = field(flight, 'airlineOperator') or {}

    code = _text(field(loc, 'flightLegStatus')).upper()
    if code == 'DEL':
        return None

    scheduled = parse_utc(field(times, 'scheduledUtc'))
    estimated = parse_utc(field(times, 'estimatedUtc'))
    actual = parse_utc(field(times, 'actualUtc'))
    gate_action = field(loc, 'gateAction')
    category, delay = classify(direction, code, scheduled, estimated, actual, gate_action)

    if direction == 'arrivals':
        city = _text(field(flight, 'departureAirportEnglish')) or _text(field(flight, 'departureAirportSwedish'))
    else:
        city = _text(field(flight, 'arrivalAirportEnglish')) or _text(field(flight, 'arrivalAirportSwedish'))

    via = []
    for stop in field(flight, 'viaDestinations') or []:
        name = _text(field(stop, 'airportEnglish')) or _text(field(stop, 'airportSwedish')) or _text(field(stop, 'airportIata'))
        if name:
            via.append(name)

    remarks = [_text(field(r, 'text')) for r in field(flight, 'remarksEnglish') or [] if _text(field(r, 'text'))]
    codeshares = [c for c in (field(flight, 'codeShareData') or []) if isinstance(c, str) and c.strip()]

    extra = None
    if direction == 'arrivals':
        belt = _text(field(field(flight, 'baggage') or {}, 'baggageClaimUnit'))
        extra = f'Belt {belt}' if belt else None
    else:
        check_in = field(flight, 'checkIn') or {}
        desk_from, desk_to = field(check_in, 'checkInDeskFrom'), field(check_in, 'checkInDeskTo')
        if desk_from:
            extra = f'Check-in {desk_from}' + (f'–{desk_to}' if desk_to and desk_to != desk_from else '')

    airline_name = field(airline, 'name') if isinstance(airline, dict) else airline
    new_time = actual or estimated
    return {
        'flight': _text(field(flight, 'flightId')) or '—',
        'airline': _text(airline_name) or '—',
        'airline_iata': _text(field(airline, 'iata')),
        'city': city or 'Unknown',
        'via': via,
        'scheduled': local_hhmm(scheduled) or '—',
        'scheduled_utc': scheduled.isoformat() if scheduled else None,
        'new_time': local_hhmm(new_time) if new_time and new_time != scheduled else None,
        'terminal': _text(field(loc, 'terminal')) or '—',
        'gate': _text(field(loc, 'gate')) or '—',
        'extra': extra,
        'status': status_label(category, field(loc, 'flightLegStatusEnglish') or STATUS_CODES.get(code, ''),
                               delay, field(loc, 'gateActionEnglish')),
        'status_code': code or None,
        'category': category,
        'delay_minutes': delay,
        'codeshares': codeshares,
        'remarks': remarks,
        'region': _text(field(flight, 'diIndicator')).upper() or None,
    }


def normalize_payload(payload, direction):
    """Validate a raw API payload and return a sorted list of normalized flights."""
    flights = field(payload, 'flights')
    if not isinstance(flights, list):
        raise FlightApiError('Unexpected response format from the FlightInfo API.', 502)
    items = [f for f in (normalize_flight(raw, direction) for raw in flights) if f]
    return sorted(items, key=lambda f: (f['scheduled_utc'] is None, f['scheduled_utc'] or ''))  # untimed flights last


class FlightInfoClient:
    """Fetches flights from Swedavia with a short in-memory cache."""

    def __init__(self, api_key, session=None, ttl=CACHE_TTL):
        self._key = (api_key or '').strip()
        self._session = session or requests.Session()
        self._ttl = ttl
        self._cache = {}
        self._lock = threading.Lock()

    @property
    def configured(self):
        return bool(self._key)

    def get_flights(self, airport, direction, day):
        """Return (flights, last_modified). ``day`` is a ``datetime.date``."""
        if not self.configured:
            raise FlightApiError('Live mode needs SWEDAVIA_API_KEY in your .env file. Use Demo mode until it is configured.', 503)
        cache_key = (airport, direction, day.isoformat())
        with self._lock:
            hit = self._cache.get(cache_key)
            if hit and time.monotonic() - hit[0] < self._ttl:
                return hit[1], hit[2]

        url = f'{BASE_URL}/{airport}/{direction}/{day.isoformat()}'
        try:
            response = self._session.get(
                url,
                headers={'Ocp-Apim-Subscription-Key': self._key, 'Accept': 'application/json',
                         'Cache-Control': 'no-cache'},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise FlightApiError('The FlightInfo API did not respond in time. Please try again.', 504) from None
        except requests.exceptions.RequestException:
            raise FlightApiError('Could not connect to the FlightInfo API. Check your internet connection.', 502) from None

        if response.status_code in (401, 403):
            raise FlightApiError('The API key was rejected. Check that it is correct and subscribed to FlightInfo.', 502)
        if response.status_code == 429:
            raise FlightApiError('The FlightInfo API rate limit was reached. Wait a minute and try again.', 503)
        if response.status_code == 404:
            raise FlightApiError('No FlightInfo data exists for that airport/date (the API keeps 7 days back to 90 days ahead).', 404)
        if not response.ok:
            raise FlightApiError(f'The FlightInfo API returned HTTP {response.status_code}.', 502)
        try:
            payload = response.json()
        except ValueError:
            raise FlightApiError('The FlightInfo API returned data that is not valid JSON.', 502) from None

        flights = normalize_payload(payload, direction)
        last_modified = response.headers.get('Last-Modified')
        with self._lock:
            if len(self._cache) > 100:
                self._cache.clear()
            self._cache[cache_key] = (time.monotonic(), flights, last_modified)
        return flights, last_modified
