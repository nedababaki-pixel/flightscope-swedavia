/* FlightScope frontend: loads flights from the Flask API, then searches and filters them
   in the browser. All API text is inserted with textContent (never innerHTML) to avoid XSS. */
'use strict';

const $ = (id) => document.getElementById(id);
const REFRESH_MS = 2 * 60 * 1000;
const FILTER_GROUPS = {
  'all': () => true,
  'on-time': (f) => f.category === 'on-time',
  'delayed': (f) => f.category === 'delayed',
  'boarding': (f) => f.category === 'boarding',
  'completed': (f) => f.category === 'departed' || f.category === 'landed',
  'disrupted': (f) => f.category === 'cancelled' || f.category === 'diverted',
};

const state = { flights: [], filter: 'all', query: '', requestId: 0, data: null };
const liveConfigured = document.body.dataset.liveConfigured === 'true';

/* ---------- Helpers ---------- */
const radioValue = (name) => document.querySelector(`input[name="${name}"]:checked`).value;
const setRadio = (name, value) => {
  const input = document.querySelector(`input[name="${name}"][value="${value}"]`);
  if (input) input.checked = true;
};
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}
function debounce(fn, ms) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}
function formatDate(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Intl.DateTimeFormat('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(Date.UTC(y, m - 1, d)));
}

/* ---------- Theme ---------- */
function applyTheme(theme) {
  if (theme) document.documentElement.dataset.theme = theme;
  const isLight = document.documentElement.dataset.theme === 'light' ||
    (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: light)').matches);
  document.documentElement.dataset.theme = isLight ? 'light' : 'dark';
  $('themeToggle').setAttribute('aria-label', isLight ? 'Switch to dark theme' : 'Switch to light theme');
}
try { applyTheme(localStorage.getItem('flightscope-theme')); } catch { applyTheme(null); }
$('themeToggle').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
  applyTheme(next);
  try { localStorage.setItem('flightscope-theme', next); } catch { /* storage unavailable */ }
});

/* ---------- URL state (shareable links) ---------- */
function readUrl() {
  const params = new URLSearchParams(location.search);
  const airport = params.get('airport');
  if (airport && [...$('airport').options].some((o) => o.value === airport.toUpperCase())) $('airport').value = airport.toUpperCase();
  if (params.get('direction')) setRadio('direction', params.get('direction'));
  if (params.get('mode')) setRadio('mode', params.get('mode'));
  const date = params.get('date');
  if (date && /^\d{4}-\d{2}-\d{2}$/.test(date) && date >= $('flightDate').min && date <= $('flightDate').max) $('flightDate').value = date;
  if (params.get('q')) $('search').value = state.query = params.get('q');
  if (params.get('status') in FILTER_GROUPS) state.filter = params.get('status');
}
function writeUrl() {
  const params = new URLSearchParams({
    airport: $('airport').value, direction: radioValue('direction'), date: $('flightDate').value, mode: radioValue('mode'),
  });
  if (state.query) params.set('q', state.query);
  if (state.filter !== 'all') params.set('status', state.filter);
  history.replaceState(null, '', `?${params}`);
}

/* ---------- Rendering ---------- */
function updateHeadings() {
  const direction = radioValue('direction');
  const arrivals = direction === 'arrivals';
  const airportName = $('airport').selectedOptions[0].textContent.replace(/\s*\(\w+\)$/, '');
  $('boardTitle').firstChild.textContent = arrivals ? 'Arrivals ' : 'Departures ';
  $('boardAirport').textContent = airportName;
  $('boardDate').textContent = formatDate($('flightDate').value);
  $('tableCaption').textContent = `${arrivals ? 'Arrivals at' : 'Departures from'} ${airportName}`;
  $('cityHead').textContent = arrivals ? 'From' : 'To';
  $('extraHead').textContent = arrivals ? 'Baggage' : 'Check-in';
  $('completedLabel').textContent = arrivals ? 'Landed' : 'Departed';
  $('chipBoarding').hidden = arrivals;
  if (arrivals && state.filter === 'boarding') state.filter = 'all';

  const live = radioValue('mode') === 'live';
  $('modeBadge').className = `mode-badge ${live ? 'live' : 'demo'}`;
  $('modeBadgeText').textContent = live ? 'Live API' : 'Demo data';
  $('demoBanner').hidden = live;
}

function matchesQuery(f, q) {
  if (!q) return true;
  const haystack = [f.flight, f.airline, f.airline_iata, f.city, f.gate, f.terminal, f.status, ...(f.via || []), ...(f.codeshares || [])]
    .filter(Boolean).join(' ').toLowerCase();
  return q.split(/\s+/).every((word) => haystack.includes(word));
}

function buildRow(f) {
  const tr = el('tr');
  if (f.category === 'departed' || f.category === 'landed') tr.classList.add('is-completed');

  const time = el('td'); time.dataset.col = 'time';
  time.appendChild(el('span', `time${f.new_time ? ' changed' : ''}`, f.scheduled));
  if (f.new_time) {
    const nt = el('span', 'new-time', f.new_time);
    nt.setAttribute('aria-label', `new time ${f.new_time}`);
    time.appendChild(nt);
  }

  const flight = el('td'); flight.dataset.col = 'flight';
  flight.appendChild(el('span', 'flight-no', f.flight));
  if (f.codeshares && f.codeshares.length) flight.appendChild(el('span', 'sub', `+ ${f.codeshares.join(', ')}`));

  const city = el('td'); city.dataset.col = 'city';
  city.appendChild(el('span', 'city', f.city));
  if (f.via && f.via.length) city.appendChild(el('span', 'sub', `via ${f.via.join(', ')}`));
  city.appendChild(el('span', 'sub mobile-only', f.airline));

  const airline = el('td', null, f.airline); airline.dataset.col = 'airline';

  const gate = el('td', 'gate'); gate.dataset.col = 'gate';
  gate.append('T', el('b', null, f.terminal), ' · Gate ', el('b', null, f.gate));

  const extra = el('td', null, f.extra || '—'); extra.dataset.col = 'extra';

  const status = el('td'); status.dataset.col = 'status';
  status.appendChild(el('span', `status ${f.category}`, f.status));
  if (f.remarks && f.remarks.length) status.appendChild(el('span', 'sub', f.remarks.join(' · ')));

  tr.append(time, flight, city, airline, gate, extra, status);
  return tr;
}

function render() {
  const q = state.query.trim().toLowerCase();
  const searched = state.flights.filter((f) => matchesQuery(f, q));
  const visible = searched.filter(FILTER_GROUPS[state.filter]);

  for (const [group, test] of Object.entries(FILTER_GROUPS)) {
    document.querySelector(`[data-count="${group}"]`).textContent = searched.filter(test).length;
  }
  document.querySelectorAll('.chip').forEach((chip) => chip.setAttribute('aria-pressed', String(chip.dataset.filter === state.filter)));

  const fragment = document.createDocumentFragment();
  visible.forEach((f) => fragment.appendChild(buildRow(f)));
  $('rows').replaceChildren(fragment);

  const noun = state.flights.length === 1 ? 'flight' : 'flights';
  $('resultCount').textContent = `${visible.length} of ${state.flights.length} ${noun} shown`;

  const msg = $('message');
  if (!msg.classList.contains('error')) {
    if (!state.flights.length && state.data) msg.textContent = 'No flights are scheduled for this airport and date.';
    else if (state.flights.length && !visible.length) msg.textContent = 'No flights match your search or filter. Try clearing them.';
    else msg.textContent = '';
  }
  writeUrl();
}

function renderStats(flights) {
  const count = (test) => flights.filter(test).length;
  $('statTotal').textContent = flights.length;
  $('statOnTime').textContent = count((f) => ['on-time', 'boarding', 'departed', 'landed'].includes(f.category) && f.delay_minutes < 15);
  $('statDelayed').textContent = count((f) => f.delay_minutes >= 15 && f.category !== 'cancelled');
  $('statDisrupted').textContent = count(FILTER_GROUPS.disrupted);
}

function showSkeleton() {
  const fragment = document.createDocumentFragment();
  for (let i = 0; i < 6; i += 1) {
    const tr = el('tr', 'skeleton');
    ['time', 'flight', 'city', 'airline', 'gate', 'extra', 'status'].forEach((col) => {
      const td = el('td'); td.dataset.col = col; td.appendChild(el('span')); tr.appendChild(td);
    });
    fragment.appendChild(tr);
  }
  $('rows').replaceChildren(fragment);
}

function showError(text) {
  const msg = $('message');
  msg.className = 'message error';
  msg.replaceChildren(el('strong', null, 'Could not load flights. '), text);
  const retry = el('button', null, 'Try again');
  retry.type = 'button';
  retry.addEventListener('click', () => loadFlights());
  msg.appendChild(retry);
}

/* ---------- Data loading ---------- */
async function loadFlights({ silent = false } = {}) {
  if (!$('flightDate').checkValidity()) {
    showError('Please choose a valid date within the allowed range.');
    return;
  }
  const requestId = ++state.requestId;   // ignore responses from older, slower requests
  updateHeadings();
  const button = $('refresh');
  button.disabled = true; button.classList.add('loading');
  $('flightTable').setAttribute('aria-busy', 'true');
  if (!silent) {
    $('message').className = 'message';
    $('message').textContent = 'Loading flight information…';
    showSkeleton();
  }

  const params = new URLSearchParams({
    airport: $('airport').value, direction: radioValue('direction'), date: $('flightDate').value, mode: radioValue('mode'),
  });
  try {
    const response = await fetch(`/api/flights?${params}`, { headers: { Accept: 'application/json' } });
    let data;
    try { data = await response.json(); } catch { throw new Error(`The server returned an unexpected response (HTTP ${response.status}).`); }
    if (!response.ok) throw new Error(data.error || `Request failed (HTTP ${response.status}).`);
    if (requestId !== state.requestId) return;

    state.data = data;
    state.flights = Array.isArray(data.flights) ? data.flights : [];
    $('message').className = 'message';
    $('message').textContent = '';
    renderStats(state.flights);
    $('statUpdated').textContent = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Stockholm', hour: '2-digit', minute: '2-digit' })
      .format(new Date(data.updated_at));
    render();
  } catch (err) {
    if (requestId !== state.requestId) return;
    if (silent && state.flights.length) return;   // keep showing the last good data on a failed auto-refresh
    state.data = null;
    state.flights = [];
    ['statTotal', 'statOnTime', 'statDelayed', 'statDisrupted', 'statUpdated'].forEach((id) => { $(id).textContent = '—'; });
    $('rows').replaceChildren();
    $('resultCount').textContent = '0 flights shown';
    showError(err instanceof TypeError ? 'The FlightScope server is not reachable. Is "python app.py" still running?' : err.message);
    document.querySelectorAll('[data-count]').forEach((c) => { c.textContent = '0'; });
  } finally {
    if (requestId === state.requestId) {
      button.disabled = false; button.classList.remove('loading');
      $('flightTable').setAttribute('aria-busy', 'false');
    }
  }
}

/* ---------- Events ---------- */
$('controls').addEventListener('submit', (event) => { event.preventDefault(); loadFlights(); });
$('airport').addEventListener('change', () => loadFlights());
$('flightDate').addEventListener('change', () => loadFlights());
document.querySelectorAll('input[name="direction"], input[name="mode"]').forEach((input) => input.addEventListener('change', () => loadFlights()));

$('search').addEventListener('input', debounce((event) => { state.query = event.target.value; render(); }, 150));
$('chips').addEventListener('click', (event) => {
  const chip = event.target.closest('.chip');
  if (!chip) return;
  state.filter = chip.dataset.filter;
  render();
});

document.addEventListener('keydown', (event) => {
  const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
  if (event.key === '/' && !typing) { event.preventDefault(); $('search').focus(); }
  if (event.key === 'Escape' && document.activeElement === $('search') && $('search').value) {
    $('search').value = state.query = ''; render();
  }
});

setInterval(() => { if (document.visibilityState === 'visible') loadFlights({ silent: true }); }, REFRESH_MS);

if (!liveConfigured) $('modeLive').nextElementSibling.title = 'No API key configured on the server';
readUrl();
loadFlights();
