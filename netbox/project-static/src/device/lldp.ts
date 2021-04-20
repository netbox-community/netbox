import { createToast } from '../toast';
import { getNetboxData, apiGetBase, hasError, isTruthy, toggleLoader } from '../util';

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
 * Update row styles based on LLDP neighbor data.
 */
function updateRowStyle(data: LLDPNeighborDetail) {
  for (const [fullIface, neighbors] of Object.entries(data.get_lldp_neighbors_detail)) {
    const [iface] = fullIface.split('.');

    const row = document.getElementById(iface) as Nullable<HTMLTableRowElement>;

    if (row !== null) {
      for (const neighbor of neighbors) {
        const cellDevice = row.querySelector<HTMLTableCellElement>('td.device');
        const cellInterface = row.querySelector<HTMLTableCellElement>('td.interface');
        const cDevice = getData(row, 'td.configured_device', 'data');
        const cChassis = getData(row, 'td.configured_chassis', 'data-chassis');
        const cInterface = getData(row, 'td.configured_interface', 'data');

        let cInterfaceShort = null;
        if (isTruthy(cInterface)) {
          cInterfaceShort = cInterface.replace(/^([A-Z][a-z])[^0-9]*([0-9\/]+)$/, '$1$2');
        }

        const nHost = neighbor.remote_system_name ?? '';
        const nPort = neighbor.remote_port ?? '';
        const [nDevice] = nHost.split('.');
        const [nInterface] = nPort.split('.');

        if (cellDevice !== null) {
          cellDevice.innerText = nDevice;
        }

        if (cellInterface !== null) {
          cellInterface.innerText = nInterface;
        }

        if (!isTruthy(cDevice) && isTruthy(nDevice)) {
          row.classList.add('info');
        } else if (
          (cDevice === nDevice || cChassis === nDevice) &&
          cInterfaceShort === nInterface
        ) {
          row.classList.add('success');
        } else if (cDevice === nDevice || cChassis === nDevice) {
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
