import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import duration from 'dayjs/plugin/duration';
import advancedFormat from 'dayjs/plugin/advancedFormat';

import { createToast } from '../bs';
import { apiGetBase, getNetboxData, hasError, toggleLoader, createElement, cToF } from '../util';

type Uptime = {
  utc: string;
  zoned: string | null;
  duration: string;
};

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(advancedFormat);
dayjs.extend(duration);

const factKeys = [
  'hostname',
  'fqdn',
  'vendor',
  'model',
  'serial_number',
  'os_version',
] as (keyof DeviceFacts)[];

type DurationKeys = 'years' | 'months' | 'days' | 'hours' | 'minutes' | 'seconds';
const formatKeys = ['years', 'months', 'days', 'hours', 'minutes', 'seconds'] as DurationKeys[];

/**
 * From a number of seconds that have elapsed since reboot, extract human-readable dates in the
 * following formats:
 *     - Relative time since reboot (e.g. 1 month, 28 days, 1 hour, 30 seconds).
 *     - Time stamp in browser-relative timezone.
 *     - Time stamp in UTC.
 * @param seconds Seconds since reboot.
 */
function getUptime(seconds: number): Uptime {
  const relDate = new Date();

  // Get the user's UTC offset, to determine if the user is in UTC or not.
  const offset = relDate.getTimezoneOffset();
  const relNow = dayjs(relDate);

  // Get a dayjs object for the device reboot time (now - number of seconds).
  const relThen = relNow.subtract(seconds, 'seconds');

  // Get a human-readable version of the time in UTC.
  const utc = relThen.tz('Etc/UTC').format('YYYY-MM-DD HH:MM:ss z');

  // We only want to show the UTC time if the user is not already in UTC time.
  let zoned = null;
  if (offset !== 0) {
    // If the user is not in UTC time, return a human-readable version in the user's timezone.
    zoned = relThen.format('YYYY-MM-DD HH:MM:ss z');
  }
  // Get a dayjs duration object to create a human-readable relative time string.
  const between = dayjs.duration(seconds, 'seconds');

  // Array of all non-zero-value duration properties. For example, if duration.year() is 0, we
  // don't care about it and shouldn't show it to the user.
  let parts = [] as string[];
  for (const key of formatKeys) {
    // Get the property value. For example, duration.year(), duration.month(), etc.
    const value = between[key]();
    if (value === 1) {
      // If the duration for this key is 1, drop the trailing 's'. For example, '1 seconds' would
      // become '1 second'.
      const label = key.replace(/s$/, '');
      parts = [...parts, `${value} ${label}`];
    } else if (value > 1) {
      // If the duration for this key is more than one, add it to the array as-is.
      parts = [...parts, `${value} ${key}`];
    }
  }
  // Set the duration to something safe, so we don't show 'undefined' or an empty string to the user.
  let duration = 'None';
  if (parts.length > 0) {
    // If the array actually has elements, reassign the duration to a human-readable version.
    duration = parts.join(', ');
  }

  return { utc, zoned, duration };
}

/**
 * After the `get_facts` result is received, parse its content and update HTML elements
 * accordingly.
 *
 * @param facts NAPALM Device Facts
 */
function processFacts(facts: DeviceFacts) {
  for (const key of factKeys) {
    if (key in facts) {
      // Find the target element which should have its innerHTML/innerText set to a NAPALM value.
      const element = document.getElementById(key);
      if (element !== null) {
        element.innerHTML = String(facts[key]);
      }
    }
  }
  const { uptime } = facts;
  const { utc, zoned, duration } = getUptime(uptime);

  // Find the duration (relative time) element and set its value.
  const uptimeDurationElement = document.getElementById('uptime-duration');
  if (uptimeDurationElement !== null) {
    uptimeDurationElement.innerHTML = duration;
  }
  // Find the time stamp element and set its value.
  const uptimeElement = document.getElementById('uptime');
  if (uptimeElement !== null) {
    if (zoned === null) {
      // If the user is in UTC time, only add the UTC time stamp.
      uptimeElement.innerHTML = utc;
    } else {
      // Otherwise, add both time stamps.
      uptimeElement.innerHTML = [zoned, `<span class="fst-italic d-block">${utc}</span>`].join('');
    }
  }
}

/**
 * Insert a title row before the next table row. The title row describes each environment key/value
 * pair from the NAPALM response.
 *
 * @param next Next adjacent element. For example, if this is the CPU data, `next` would be the
 *             memory row.
 * @param title1 Column 1 Title
 * @param title2 Column 2 Title
 */
function insertTitleRow<E extends HTMLElement>(next: E, title1: string, title2: string): void {
  // Create cell element that contains the key title.
  const col1Title = createElement('th', { innerText: title1 }, ['border-end', 'text-end']);
  // Create cell element that contains the value title.
  const col2Title = createElement('th', { innerText: title2 }, ['border-start', 'text-start']);
  // Create title row element with the two header cells as children.
  const titleRow = createElement('tr', {}, [], [col1Title, col2Title]);
  // Insert the entire row just before the beginning of the next row (i.e., at the end of this row).
  next.insertAdjacentElement('beforebegin', titleRow);
}

/**
 * Insert a "No Data" row, for when the NAPALM response doesn't contain this type of data.
 *
 * @param next Next adjacent element.For example, if this is the CPU data, `next` would be the
 *             memory row.
 */
function insertNoneRow<E extends Nullable<HTMLElement>>(next: E) {
  const none = createElement('td', { colSpan: '2', innerText: 'No Data' }, [
    'text-muted',
    'text-center',
  ]);
  const titleRow = createElement('tr', {}, [], [none]);
  if (next !== null) {
    next.insertAdjacentElement('beforebegin', titleRow);
  }
}

function getNext<E extends HTMLElement>(id: string): Nullable<E> {
  const element = document.getElementById(id);
  if (element !== null) {
    return element.nextElementSibling as Nullable<E>;
  }
  return null;
}

/**
 * Create & insert table rows for each CPU in the NAPALM response.
 *
 * @param cpu NAPALM CPU data.
 */
function processCpu(cpu: DeviceEnvironment['cpu']) {
  // Find the next adjacent element, so we can insert elements before it.
  const next = getNext<HTMLTableRowElement>('status-cpu');
  if (typeof cpu !== 'undefined') {
    if (next !== null) {
      insertTitleRow(next, 'Name', 'Usage');
      for (const [core, data] of Object.entries(cpu)) {
        const usage = data['%usage'];
        const kCell = createElement('td', { innerText: core }, ['border-end', 'text-end']);
        const vCell = createElement('td', { innerText: `${usage} %` }, [
          'border-start',
          'text-start',
        ]);
        const row = createElement('tr', {}, [], [kCell, vCell]);
        next.insertAdjacentElement('beforebegin', row);
      }
    }
  } else {
    insertNoneRow(next);
  }
}

/**
 * Create & insert table rows for the memory in the NAPALM response.
 *
 * @param mem NAPALM memory data.
 */
function processMemory(mem: DeviceEnvironment['memory']) {
  // Find the next adjacent element, so we can insert elements before it.
  const next = getNext<HTMLTableRowElement>('status-memory');
  if (typeof mem !== 'undefined') {
    if (next !== null) {
      insertTitleRow(next, 'Available', 'Used');
      const { available_ram: avail, used_ram: used } = mem;
      const aCell = createElement('td', { innerText: avail }, ['border-end', 'text-end']);
      const uCell = createElement('td', { innerText: used }, ['border-start', 'text-start']);
      const row = createElement('tr', {}, [], [aCell, uCell]);
      next.insertAdjacentElement('beforebegin', row);
    }
  } else {
    insertNoneRow(next);
  }
}

/**
 * Create & insert table rows for each temperature sensor in the NAPALM response.
 *
 * @param temp NAPALM temperature data.
 */
function processTemp(temp: DeviceEnvironment['temperature']) {
  // Find the next adjacent element, so we can insert elements before it.
  const next = getNext<HTMLTableRowElement>('status-temperature');
  if (typeof temp !== 'undefined') {
    if (next !== null) {
      insertTitleRow(next, 'Sensor', 'Value');
      for (const [sensor, data] of Object.entries(temp)) {
        const tempC = data.temperature;
        const tempF = cToF(tempC);
        const innerHTML = `${tempC} °C <span class="ms-1 text-muted small">${tempF} °F</span>`;
        const status = data.is_alert ? 'warning' : data.is_critical ? 'danger' : 'success';
        const kCell = createElement('td', { innerText: sensor }, ['border-end', 'text-end']);
        const vCell = createElement('td', { innerHTML }, ['border-start', 'text-start']);
        const row = createElement('tr', {}, [`table-${status}`], [kCell, vCell]);
        next.insertAdjacentElement('beforebegin', row);
      }
    }
  } else {
    insertNoneRow(next);
  }
}

/**
 * Create & insert table rows for each fan in the NAPALM response.
 *
 * @param fans NAPALM fan data.
 */
function processFans(fans: DeviceEnvironment['fans']) {
  // Find the next adjacent element, so we can insert elements before it.
  const next = getNext<HTMLTableRowElement>('status-fans');
  if (typeof fans !== 'undefined') {
    if (next !== null) {
      insertTitleRow(next, 'Fan', 'Status');
      for (const [fan, data] of Object.entries(fans)) {
        const { status } = data;
        const goodIcon = createElement('i', {}, ['mdi', 'mdi-check-bold', 'text-success']);
        const badIcon = createElement('i', {}, ['mdi', 'mdi-close', 'text-warning']);
        const kCell = createElement('td', { innerText: fan }, ['border-end', 'text-end']);
        const vCell = createElement(
          'td',
          {},
          ['border-start', 'text-start'],
          [status ? goodIcon : badIcon],
        );
        const row = createElement(
          'tr',
          {},
          [`table-${status ? 'success' : 'warning'}`],
          [kCell, vCell],
        );
        next.insertAdjacentElement('beforebegin', row);
      }
    }
  } else {
    insertNoneRow(next);
  }
}

/**
 * Create & insert table rows for each PSU in the NAPALM response.
 *
 * @param power NAPALM power data.
 */
function processPower(power: DeviceEnvironment['power']) {
  // Find the next adjacent element, so we can insert elements before it.
  const next = getNext<HTMLTableRowElement>('status-power');
  if (typeof power !== 'undefined') {
    if (next !== null) {
      insertTitleRow(next, 'PSU', 'Status');
      for (const [psu, data] of Object.entries(power)) {
        const { status } = data;
        const goodIcon = createElement('i', {}, ['mdi', 'mdi-check-bold', 'text-success']);
        const badIcon = createElement('i', {}, ['mdi', 'mdi-close', 'text-warning']);
        const kCell = createElement('td', { innerText: psu }, ['border-end', 'text-end']);
        const vCell = createElement(
          'td',
          {},
          ['border-start', 'text-start'],
          [status ? goodIcon : badIcon],
        );
        const row = createElement(
          'tr',
          {},
          [`table-${status ? 'success' : 'warning'}`],
          [kCell, vCell],
        );
        next.insertAdjacentElement('beforebegin', row);
      }
    }
  } else {
    insertNoneRow(next);
  }
}

/**
 * After the `get_environment` result is received, parse its content and update HTML elements
 * accordingly.
 *
 * @param env NAPALM Device Environment
 */
function processEnvironment(env: DeviceEnvironment) {
  const { cpu, memory, temperature, fans, power } = env;
  processCpu(cpu);
  processMemory(memory);
  processTemp(temperature);
  processFans(fans);
  processPower(power);
}

/**
 * Initialize NAPALM device status handlers.
 */
function initStatus() {
  // Show loading state for both Facts & Environment cards.
  toggleLoader('show');

  const url = getNetboxData('data-object-url');

  if (url !== null) {
    apiGetBase<DeviceStatus>(url)
      .then(data => {
        if (hasError(data)) {
          // If the API returns an error, show it to the user.
          createToast('danger', 'Error Fetching Device Status', data.error).show();
        } else {
          if (!hasError(data.get_facts)) {
            processFacts(data.get_facts);
          } else {
            // If the device facts data contains an error, show it to the user.
            createToast('danger', 'Error Fetching Device Facts', data.get_facts.error).show();
          }
          if (!hasError(data.get_environment)) {
            processEnvironment(data.get_environment);
          } else {
            // If the device environment data contains an error, show it to the user.
            createToast(
              'danger',
              'Error Fetching Device Environment Data',
              data.get_environment.error,
            ).show();
          }
        }
        return;
      })
      .finally(() => toggleLoader('hide'));
  } else {
    toggleLoader('hide');
  }
}

if (document.readyState !== 'loading') {
  initStatus();
} else {
  document.addEventListener('DOMContentLoaded', initStatus);
}
