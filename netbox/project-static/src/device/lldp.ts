import { createToast } from '../bs';
import { getNetboxData, apiGetBase, hasError, isTruthy, toggleLoader } from '../util';

// Match an interface name that begins with a capital letter and is followed by at least one other
// alphabetic character, and ends with a forward-slash-separated numeric sequence such as 0/1/2.
const CISCO_IOS_PATTERN = new RegExp(/^([A-Z][A-Za-z]+)[^0-9]*([0-9/]+)$/);

// Mapping of overrides to default Cisco IOS interface alias behavior (default behavior is to use
// the first two characters).
const CISCO_IOS_OVERRIDES = new Map<string, string>([
  // Cisco IOS abbreviates 25G (TwentyFiveGigE) interfaces as 'Twe'.
  ['TwentyFiveGigE', 'Twe'],
]);

/**
 * Get an attribute from a row's cell.
 *
 * @param row Interface row
 * @param query CSS media query
 * @param attr Cell attribute
 */
function getData(row: HTMLTableRowElement, query: string, attr: string): string | null {
  return row.querySelector(query)?.getAttribute(attr) ?? null;
}

/**
 * Get preconfigured alias for given interface. Primarily for matching long-form Cisco IOS
 * interface names with short-form Cisco IOS interface names. For example, `GigabitEthernet0/1/2`
 * would become `Gi0/1/2`.
 *
 * This should probably be replaced with something in the primary application (Django), such as
 * a database field attached to given interface types. However, this is a temporary measure to
 * replace the functionality of this one-liner:
 *
 * @see https://github.com/netbox-community/netbox/blob/9cc4992fad2fe04ef0211d998c517414e8871d8c/netbox/templates/dcim/device/lldp_neighbors.html#L69
 *
 * @param name Long-form/original interface name.
 */
function getInterfaceAlias(name: string | null): string | null {
  if (name === null) {
    return name;
  }
  if (name.match(CISCO_IOS_PATTERN)) {
    // Extract the base name and numeric portions of the interface. For example, an input interface
    // of `GigabitEthernet0/0/1` would result in an array of `['GigabitEthernet', '0/0/1']`.
    const [base, numeric] = (name.match(CISCO_IOS_PATTERN) ?? []).slice(1, 3);

    if (isTruthy(base) && isTruthy(numeric)) {
      // Check the override map and use its value if the base name is present in the map.
      // Otherwise, use the first two characters of the base name. For example,
      // `GigabitEthernet0/0/1` would become `Gi0/0/1`, but `TwentyFiveGigE0/0/1` would become
      // `Twe0/0/1`.
      const aliasBase = CISCO_IOS_OVERRIDES.get(base) || base.slice(0, 2);
      return `${aliasBase}${numeric}`;
    }
  }
  return name;
}

/**
 * Update row styles based on LLDP neighbor data.
 */
function updateRowStyle(data: LLDPNeighborDetail) {
  for (const [fullIface, neighbors] of Object.entries(data.get_lldp_neighbors_detail)) {
    const [iface] = fullIface.split('.');

    const row = document.getElementById(iface) as Nullable<HTMLTableRowElement>;

    if (row !== null) {
      for (const neighbor of neighbors) {
        const deviceCell = row.querySelector<HTMLTableCellElement>('td.device');
        const interfaceCell = row.querySelector<HTMLTableCellElement>('td.interface');
        const configuredDevice = getData(row, 'td.configured_device', 'data');
        const configuredChassis = getData(row, 'td.configured_chassis', 'data-chassis');
        const configuredIface = getData(row, 'td.configured_interface', 'data');

        const interfaceAlias = getInterfaceAlias(configuredIface);

        const remoteName = neighbor.remote_system_name ?? '';
        const remotePort = neighbor.remote_port ?? '';
        const [neighborDevice] = remoteName.split('.');
        const [neighborIface] = remotePort.split('.');

        if (deviceCell !== null) {
          deviceCell.innerText = neighborDevice;
        }

        if (interfaceCell !== null) {
          interfaceCell.innerText = neighborIface;
        }

        // Interface has an LLDP neighbor, but the neighbor is not configured in NetBox.
        const nonConfiguredDevice = !isTruthy(configuredDevice) && isTruthy(neighborDevice);

        // NetBox device or chassis matches LLDP neighbor.
        const validNode =
          configuredDevice === neighborDevice || configuredChassis === neighborDevice;

        // NetBox configured interface matches LLDP neighbor interface.
        const validInterface =
          configuredIface === neighborIface || interfaceAlias === neighborIface;

        if (nonConfiguredDevice) {
          row.classList.add('info');
        } else if (validNode && validInterface) {
          row.classList.add('success');
        } else {
          row.classList.add('danger');
        }
      }
    }
  }
}

/**
 * Initialize LLDP Neighbor fetching.
 */
function initLldpNeighbors() {
  toggleLoader('show');
  const url = getNetboxData('object-url');
  if (url !== null) {
    apiGetBase<LLDPNeighborDetail>(url)
      .then(data => {
        if (hasError(data)) {
          createToast('danger', 'Error Retrieving LLDP Neighbor Information', data.error).show();
          toggleLoader('hide');
          return;
        } else {
          updateRowStyle(data);
        }
        return;
      })
      .finally(() => {
        toggleLoader('hide');
      });
  }
}

if (document.readyState !== 'loading') {
  initLldpNeighbors();
} else {
  document.addEventListener('DOMContentLoaded', initLldpNeighbors);
}
