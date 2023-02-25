import { GridStack, GridStackOptions, GridStackWidget } from 'gridstack';
import { createToast } from './bs';
import { apiPatch, hasError } from './util';

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
    cellHeight: 100,
  });

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
