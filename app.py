"""FlightScope: a flight information dashboard for Swedavia's ten Swedish airports.

Demo mode (default) uses fictional flights and needs no API key.
Live mode calls the official Swedavia FlightInfo API v2 using SWEDAVIA_API_KEY from .env.
The key is only ever used server-side; it is never sent to the browser or logged.
"""
import logging
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from demo_data import build_demo_payload
from swedavia_client import (AIRPORTS, DIRECTIONS, SWEDEN, FlightApiError, FlightInfoClient,
                             formatted_time, normalize_flight, normalize_payload)

load_dotenv(Path(__file__).with_name('.env'))

app = Flask(__name__)
app.json.sort_keys = False
app.json.ensure_ascii = False
client = FlightInfoClient(os.getenv('SWEDAVIA_API_KEY', ''))
log = logging.getLogger('flightscope')

# The API keeps data from 7 days back to 90 days ahead (official guide, section 2.1).
DAYS_BACK, DAYS_AHEAD = 7, 90

# Re-exported for tests and backwards compatibility.
__all__ = ['app', 'formatted_time', 'normalize_flight']


def today_in_sweden():
    return datetime.now(SWEDEN).date()


def api_error(message, status):
    return jsonify({'error': message}), status


@app.after_request
def security_headers(response):
    """Basic hardening: no inline scripts, no framing, no MIME sniffing."""
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.errorhandler(HTTPException)
def handle_http_error(exc):
    if request.path.startswith('/api/'):
        return api_error(exc.description or exc.name, exc.code)
    return exc


@app.errorhandler(Exception)
def handle_unexpected(exc):
    log.exception('Unhandled error')  # message only; the API key is never part of exceptions we raise
    if request.path.startswith('/api/'):
        return api_error('Something went wrong on the server. Please try again.', 500)
    return 'Internal server error', 500


@app.get('/')
def index():
    today = today_in_sweden()
    return render_template('index.html', airports=AIRPORTS, live_configured=client.configured,
                           today=today.isoformat(),
                           min_date=(today - timedelta(days=DAYS_BACK)).isoformat(),
                           max_date=(today + timedelta(days=DAYS_AHEAD)).isoformat())


@app.get('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.svg')


@app.get('/api/status')
def status():
    """Tells the UI whether live mode is available (a boolean, never the key itself)."""
    return jsonify({'live_configured': client.configured, 'airports': AIRPORTS})


@app.get('/api/flights')
def get_flights():
    airport = request.args.get('airport', 'ARN').strip().upper()
    direction = request.args.get('direction', 'departures').strip().lower()
    mode = request.args.get('mode', 'demo').strip().lower()
    raw_date = request.args.get('date', '').strip() or today_in_sweden().isoformat()

    if airport not in AIRPORTS:
        return api_error('Unknown airport. Choose one of the ten Swedavia airports.', 400)
    if direction not in DIRECTIONS:
        return api_error('Flight type must be "departures" or "arrivals".', 400)
    if mode not in ('demo', 'live'):
        return api_error('Data source must be "demo" or "live".', 400)
    try:
        day = date.fromisoformat(raw_date)
    except ValueError:
        return api_error('Date must use the format YYYY-MM-DD.', 400)
    today = today_in_sweden()
    if not today - timedelta(days=DAYS_BACK) <= day <= today + timedelta(days=DAYS_AHEAD):
        return api_error(f'Choose a date between {DAYS_BACK} days ago and {DAYS_AHEAD} days ahead.', 400)

    last_modified = None
    if mode == 'demo':
        flights = normalize_payload(build_demo_payload(airport, direction, day), direction)
    else:
        try:
            flights, last_modified = client.get_flights(airport, direction, day)
        except FlightApiError as exc:
            return api_error(exc.message, exc.status)

    return jsonify({
        'source': mode,
        'airport': airport,
        'airport_name': AIRPORTS[airport],
        'direction': direction,
        'date': day.isoformat(),
        'count': len(flights),
        'flights': flights,
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'api_last_modified': last_modified,
    })


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    port = int(os.getenv('PORT', '5055'))
    mode = 'Live API key found' if client.configured else 'no API key - Demo mode only'
    print(f'\n  FlightScope running at http://127.0.0.1:{port}  ({mode})\n  Press CTRL+C to stop.\n')
    app.run(host='127.0.0.1', port=port, debug=False)
