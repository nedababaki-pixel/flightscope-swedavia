"""Automated tests for FlightScope. Run with:  python -m unittest discover -s tests -v

No network access or API key is needed: live API calls are replaced with fakes.
"""
import os
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as app_module  # noqa: E402
from app import app, today_in_sweden  # noqa: E402
from demo_data import build_demo_payload  # noqa: E402
from swedavia_client import (FlightApiError, FlightInfoClient, field, formatted_time,  # noqa: E402
                             normalize_flight, normalize_payload)

FAKE_KEY = 'test-key-1234567890-do-not-leak'

# A departure shaped like the official FlightInfo v2 model (camelCase JSON).
DEPARTURE = {
    'flightId': 'SK1415',
    'arrivalAirportSwedish': 'Köpenhamn',
    'arrivalAirportEnglish': 'Copenhagen',
    'airlineOperator': {'iata': 'SK', 'icao': 'SAS', 'name': 'SAS'},
    'departureTime': {'scheduledUtc': '2026-01-02T12:00:00Z', 'estimatedUtc': '2026-01-02T12:30:00Z', 'actualUtc': None},
    'locationAndStatus': {'terminal': '5', 'gate': 'F34', 'gateAction': None,
                          'flightLegStatus': 'SCH', 'flightLegStatusEnglish': 'New time'},
    'checkIn': {'checkInDeskFrom': 10, 'checkInDeskTo': 14},
    'codeShareData': ['LH6014'],
    'remarksEnglish': [{'text': 'Go to gate', 'indicator': 'I'}],
    'viaDestinations': [],
    'diIndicator': 'S',
}
ARRIVAL = {
    'flightId': 'DY4321',
    'departureAirportEnglish': 'Oslo',
    'airlineOperator': {'iata': 'DY', 'name': 'Norwegian'},
    'arrivalTime': {'scheduledUtc': '2026-07-01T08:00:00Z', 'estimatedUtc': '2026-07-01T08:05:00Z', 'actualUtc': '2026-07-01T08:04:00Z'},
    'locationAndStatus': {'terminal': '5', 'gate': 'F1', 'flightLegStatus': 'LAN', 'flightLegStatusEnglish': 'Landed'},
    'baggage': {'baggageClaimUnit': '7'},
}


def fake_response(status=200, payload=None, json_error=False):
    response = mock.Mock()
    response.status_code = status
    response.ok = status < 400
    response.headers = {'Last-Modified': 'Fri, 02 Jan 2026 11:00:00 GMT'}
    if json_error:
        response.json.side_effect = ValueError('bad json')
    else:
        response.json.return_value = payload
    return response


class PageAndSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_renders_all_airports(self):
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        html = result.get_data(as_text=True)
        for code in ('ARN', 'BMA', 'GOT', 'MMX', 'LLA', 'UME', 'OSD', 'VBY', 'RNB', 'KRN'):
            self.assertIn(f'value="{code}"', html)
        self.assertIn('Skip to flight list', html)

    def test_security_headers(self):
        headers = self.client.get('/').headers
        self.assertIn("script-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(headers['X-Frame-Options'], 'DENY')

    def test_static_files(self):
        for path in ('/static/app.js', '/static/style.css', '/static/favicon.svg'):
            result = self.client.get(path)
            self.assertEqual(result.status_code, 200, path)
            result.close()

    def test_unknown_api_route_returns_json_404(self):
        result = self.client.get('/api/nope')
        self.assertEqual(result.status_code, 404)
        self.assertIn('error', result.json)

    def test_status_never_exposes_key(self):
        with mock.patch.object(app_module, 'client', FlightInfoClient(FAKE_KEY)):
            result = self.client.get('/api/status')
            self.assertTrue(result.json['live_configured'])
            self.assertNotIn(FAKE_KEY, result.get_data(as_text=True))
            self.assertNotIn(FAKE_KEY, self.client.get('/').get_data(as_text=True))


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def assert_bad(self, query):
        result = self.client.get(f'/api/flights?{query}')
        self.assertEqual(result.status_code, 400, query)
        self.assertIn('error', result.json)

    def test_invalid_inputs(self):
        self.assert_bad('airport=XXX')
        self.assert_bad('airport=<script>')
        self.assert_bad('direction=sideways')
        self.assert_bad('mode=hack')
        self.assert_bad('date=tomorrow')
        self.assert_bad('date=2026-02-30')

    def test_date_out_of_api_range(self):
        too_old = (today_in_sweden() - timedelta(days=8)).isoformat()
        too_far = (today_in_sweden() + timedelta(days=91)).isoformat()
        self.assert_bad(f'date={too_old}')
        self.assert_bad(f'date={too_far}')

    def test_lowercase_airport_is_accepted(self):
        self.assertEqual(self.client.get('/api/flights?airport=got').status_code, 200)


class DemoModeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_demo_works_for_every_airport_and_direction(self):
        for code in app_module.AIRPORTS:
            for direction in ('departures', 'arrivals'):
                result = self.client.get(f'/api/flights?mode=demo&airport={code}&direction={direction}')
                self.assertEqual(result.status_code, 200)
                body = result.json
                self.assertEqual(body['source'], 'demo')
                self.assertGreater(body['count'], 0)
                self.assertEqual(body['count'], len(body['flights']))
                cities = {f['city'] for f in body['flights']}
                self.assertNotIn(app_module.AIRPORTS[code], cities, 'an airport should not fly to itself')

    def test_demo_is_deterministic_and_sorted(self):
        day = date(2026, 10, 26)
        now = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
        first = normalize_payload(build_demo_payload('ARN', 'departures', day, now), 'departures')
        second = normalize_payload(build_demo_payload('ARN', 'departures', day, now), 'departures')
        self.assertEqual(first, second)
        times = [f['scheduled_utc'] for f in first]
        self.assertEqual(times, sorted(times))

    def test_demo_differs_between_airports(self):
        day = date(2026, 10, 26)
        arn = build_demo_payload('ARN', 'departures', day)['flights']
        vby = build_demo_payload('VBY', 'departures', day)['flights']
        self.assertNotEqual([f['flightId'] for f in arn], [f['flightId'] for f in vby])

    def test_demo_statuses_follow_the_clock(self):
        day = date(2026, 10, 26)
        evening = datetime(2026, 10, 26, 22, 30, tzinfo=timezone.utc)
        categories = {f['category'] for f in normalize_payload(build_demo_payload('ARN', 'arrivals', day, evening), 'arrivals')}
        self.assertIn('landed', categories)
        self.assertNotIn('departed', categories)


class NormalizationTests(unittest.TestCase):
    def test_formatted_time_converts_utc_to_swedish_time(self):
        self.assertEqual(formatted_time('2026-01-02T12:00:00Z'), '13:00')   # CET, winter
        self.assertEqual(formatted_time('2026-07-02T12:00:00Z'), '14:00')   # CEST, summer
        self.assertEqual(formatted_time('2026-07-02T12:00:00'), '14:00')    # naive = UTC
        self.assertEqual(formatted_time(None), '—')
        self.assertEqual(formatted_time('not a date'), '—')

    def test_field_is_case_insensitive(self):
        self.assertEqual(field({'FlightId': 'SK1'}, 'flightId'), 'SK1')
        self.assertIsNone(field('not a dict', 'x'))

    def test_departure_mapping(self):
        f = normalize_flight(DEPARTURE, 'departures')
        self.assertEqual(f['flight'], 'SK1415')
        self.assertEqual(f['city'], 'Copenhagen')
        self.assertEqual(f['airline'], 'SAS')
        self.assertEqual(f['gate'], 'F34')
        self.assertEqual(f['terminal'], '5')
        self.assertEqual(f['scheduled'], '13:00')
        self.assertEqual(f['new_time'], '13:30')
        self.assertEqual(f['category'], 'delayed')
        self.assertEqual(f['delay_minutes'], 30)
        self.assertEqual(f['status'], 'Delayed 30 min')
        self.assertEqual(f['extra'], 'Check-in 10–14')
        self.assertEqual(f['codeshares'], ['LH6014'])
        self.assertEqual(f['remarks'], ['Go to gate'])

    def test_arrival_mapping(self):
        f = normalize_flight(ARRIVAL, 'arrivals')
        self.assertEqual(f['city'], 'Oslo')
        self.assertEqual(f['category'], 'landed')
        self.assertEqual(f['status'], 'Landed')
        self.assertEqual(f['extra'], 'Belt 7')
        self.assertEqual(f['scheduled'], '10:00')

    def test_pascal_case_payload_also_works(self):
        f = normalize_flight({'FlightId': 'AY1', 'ArrivalAirportEnglish': 'Helsinki',
                              'LocationAndStatus': {'Gate': 'F2', 'FlightLegStatus': 'CAN', 'FlightLegStatusEnglish': 'Cancelled'}},
                             'departures')
        self.assertEqual((f['flight'], f['city'], f['gate'], f['category']), ('AY1', 'Helsinki', 'F2', 'cancelled'))

    def test_status_categories(self):
        def category(direction, **loc):
            raw = {'flightId': 'X1', 'locationAndStatus': loc,
                   'departureTime': {'scheduledUtc': '2026-01-02T12:00:00Z'}}
            return normalize_flight(raw, direction)['category']
        self.assertEqual(category('departures', flightLegStatus='SCH'), 'on-time')
        self.assertEqual(category('departures', flightLegStatus='SCH', gateAction='O'), 'boarding')
        self.assertEqual(category('departures', flightLegStatus='ACT'), 'departed')
        self.assertEqual(category('departures', flightLegStatus='DIV'), 'diverted')
        self.assertEqual(category('departures', flightLegStatus='FLS'), 'cancelled')

    def test_deleted_and_broken_flights_are_skipped(self):
        self.assertIsNone(normalize_flight({'locationAndStatus': {'flightLegStatus': 'DEL'}}, 'arrivals'))
        self.assertIsNone(normalize_flight('garbage', 'arrivals'))
        flights = normalize_payload({'flights': [DEPARTURE, 'garbage', {}]}, 'departures')
        self.assertEqual(len(flights), 2)
        self.assertEqual(flights[1]['flight'], '—')

    def test_payload_without_flights_list_is_rejected(self):
        with self.assertRaises(FlightApiError):
            normalize_payload({'oops': True}, 'departures')


class LiveModeTests(unittest.TestCase):
    """Live mode with the HTTP layer faked, so no key or internet is required."""

    def setUp(self):
        self.client = app.test_client()
        self.session = mock.Mock()
        self.live = FlightInfoClient(FAKE_KEY, session=self.session)
        patcher = mock.patch.object(app_module, 'client', self.live)
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_live(self, airport='ARN', direction='departures'):
        return self.client.get(f'/api/flights?mode=live&airport={airport}&direction={direction}')

    def test_missing_key_returns_503(self):
        with mock.patch.object(app_module, 'client', FlightInfoClient('')):
            result = self.get_live()
        self.assertEqual(result.status_code, 503)
        self.assertIn('SWEDAVIA_API_KEY', result.json['error'])

    def test_success_calls_official_endpoint_with_header(self):
        self.session.get.return_value = fake_response(200, {'numberOfFlights': 1, 'flights': [DEPARTURE]})
        result = self.get_live()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['source'], 'live')
        self.assertEqual(result.json['flights'][0]['flight'], 'SK1415')
        self.assertEqual(result.json['api_last_modified'], 'Fri, 02 Jan 2026 11:00:00 GMT')

        url = self.session.get.call_args.args[0]
        headers = self.session.get.call_args.kwargs['headers']
        self.assertEqual(url, f'https://api.swedavia.se/flightinfo/v2/ARN/departures/{today_in_sweden().isoformat()}')
        self.assertEqual(headers['Ocp-Apim-Subscription-Key'], FAKE_KEY)
        self.assertIn('timeout', self.session.get.call_args.kwargs)
        self.assertNotIn(FAKE_KEY, result.get_data(as_text=True))

    def test_responses_are_cached(self):
        self.session.get.return_value = fake_response(200, {'flights': [ARRIVAL]})
        self.get_live(direction='arrivals')
        self.get_live(direction='arrivals')
        self.assertEqual(self.session.get.call_count, 1)

    def test_api_errors_are_translated(self):
        cases = [(401, 502, 'rejected'), (403, 502, 'rejected'), (404, 404, '7 days'),
                 (429, 503, 'rate limit'), (500, 502, 'HTTP 500')]
        for upstream, expected, text in cases:
            with self.subTest(upstream=upstream):
                self.live._cache.clear()
                self.session.get.return_value = fake_response(upstream, {})
                result = self.get_live()
                self.assertEqual(result.status_code, expected)
                self.assertIn(text, result.json['error'])
                self.assertNotIn(FAKE_KEY, result.json['error'])

    def test_timeout_connection_and_bad_json(self):
        self.session.get.side_effect = requests.exceptions.Timeout()
        self.assertEqual(self.get_live().status_code, 504)
        self.session.get.side_effect = requests.exceptions.ConnectionError('host secret details')
        result = self.get_live()
        self.assertEqual(result.status_code, 502)
        self.assertNotIn('secret', result.json['error'])
        self.session.get.side_effect = None
        self.session.get.return_value = fake_response(200, json_error=True)
        self.assertEqual(self.get_live().status_code, 502)
        self.session.get.return_value = fake_response(200, ['not', 'a', 'dict'])
        self.assertEqual(self.get_live().status_code, 502)


class RepositoryHygieneTests(unittest.TestCase):
    """Guards against accidentally publishing secrets."""

    ROOT = Path(__file__).resolve().parents[1]

    def test_env_is_git_ignored(self):
        ignored = (self.ROOT / '.gitignore').read_text(encoding='utf-8').splitlines()
        self.assertIn('.env', ignored)

    def test_env_example_has_no_key(self):
        for line in (self.ROOT / '.env.example').read_text(encoding='utf-8').splitlines():
            if line.startswith('SWEDAVIA_API_KEY='):
                self.assertEqual(line.strip(), 'SWEDAVIA_API_KEY=')

    def test_real_key_not_in_tracked_files(self):
        key = os.getenv('SWEDAVIA_API_KEY', '').strip()
        if len(key) < 8:
            self.skipTest('No real API key configured; nothing to search for.')
        for path in self.ROOT.rglob('*'):
            if path.is_file() and path.name != '.env' and not any(p in path.parts for p in ('.venv', 'venv', '.git', '__pycache__')):
                try:
                    self.assertNotIn(key, path.read_text(encoding='utf-8'), str(path))
                except (UnicodeDecodeError, PermissionError):
                    continue


if __name__ == '__main__':
    unittest.main()
