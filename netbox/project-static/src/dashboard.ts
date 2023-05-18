import { GridStack, GridStackOptions, GridStackWidget } from 'gridstack';
import { createToast } from './bs';
import { apiPatch, hasError } from './util';

function lockDashboard(): void {
  const dashboard = document.getElementById('dashboard') as any;
  const gridUnlockButton = document.getElementById('unlock_dashboard') as HTMLButtonElement;
  const gridLockButton = document.getElementById('lock_dashboard') as HTMLButtonElement;

  if (dashboard) {
    dashboard.gridstack.disable();
    // Hide the grid stack items buttons
    Array.from(document.getElementsByClassName("grid-stack-item-button")).forEach(function (element) {
      element.classList.add('invisible');
    });
  }
  if (gridUnlockButton && gridLockButton) {
    gridUnlockButton.classList.remove('invisible');
    gridLockButton.classList.add('invisible');
  }
}

function unlockDashboard(): void {
  const dashboard = document.getElementById('dashboard') as any;
  const gridUnlockButton = document.getElementById('unlock_dashboard') as HTMLButtonElement;
  const gridLockButton = document.getElementById('lock_dashboard') as HTMLButtonElement;
  if (dashboard) {
    dashboard.gridstack.enable();
    // Show the grid stack items buttons
    Array.from(document.getElementsByClassName("grid-stack-item-button")).forEach(function (element) {
      element.classList.remove('invisible');
    });
  }
  if (gridUnlockButton && gridLockButton) {
    gridUnlockButton.classList.add('invisible');
    gridLockButton.classList.remove('invisible');
  }
}

async function saveDashboardLayout(
  url: string,
  gridData: GridStackWidget[] | GridStackOptions,
): Promise<APIResponse<APIUserConfig>> {
  let data = {
    layout: gridData
  }
  return await apiPatch<APIUserConfig>(url, data);
}

export function initDashboard(): void {
  // Exit if this page does not contain a dashboard
  const dashboard = document.getElementById('dashboard') as Nullable<HTMLDivElement>;
  if (dashboard == null) {
    return;
  }

  // Initialize the grid
  let grid = GridStack.init({
    cellHeight: 48,
    disableDrag: true,
    disableResize: true,
    draggable: {
      handle: '.grid-stack-item-content .card-header',
      appendTo: 'body',
      scroll: true
    }
  });

  // Create a listener for the dashboard lock button
  const gridLockButton = document.getElementById('lock_dashboard') as HTMLButtonElement;
  if (gridLockButton) {
    gridLockButton.addEventListener('click', () => {
      lockDashboard();
    });
  }

  // Create a listener for the dashboard unlock button
  const gridUnlockButton = document.getElementById('unlock_dashboard') as HTMLButtonElement;
  if (gridUnlockButton) {
    gridUnlockButton.addEventListener('click', () => {
      unlockDashboard();
    });
  }

  // Create a listener for the dashboard save button
  const gridSaveButton = document.getElementById('save_dashboard') as HTMLButtonElement;
  if (gridSaveButton === null) {
    return;
  }
  gridSaveButton.addEventListener('click', () => {
    const url = gridSaveButton.getAttribute('data-url');
    if (url == null) {
      return;
    }
    let gridData = grid.save(false);
    saveDashboardLayout(url, gridData).then(res => {
      if (hasError(res)) {
        const toast = createToast('danger', 'Error Saving Dashboard Config', res.error);
        toast.show();
      } else {
        location.reload();
      }
    });
  });
}
