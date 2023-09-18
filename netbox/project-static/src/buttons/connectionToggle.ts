import { createToast } from '../bs';
import { isTruthy, apiPatch, hasError, getElements } from '../util';

/**
 * When the toggle button is clicked, swap the connection status via the API and toggle CSS
 * classes to reflect the connection status.
 *
 * @param element Connection Toggle Button Element
 */
function toggleConnection(element: HTMLButtonElement): void {
  const url = element.getAttribute('data-url');
  const connected = element.classList.contains('connected');
  const status = connected ? 'planned' : 'connected';

  if (isTruthy(url)) {
    apiPatch(url, { status }).then(res => {
      if (hasError(res)) {
        // If the API responds with an error, show it to the user.
        createToast('danger', 'Error', res.error).show();
        return;
      } else {
        // Get the button's icon to change its CSS class.
        const icon = element.querySelector('i.mdi, span.mdi') as HTMLSpanElement;
        if (connected) {
          element.classList.remove('connected', 'btn-warning');
          element.classList.add('btn-info');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-disconnect');
          icon.classList.add('mdi-lan-connect');
        } else {
          element.classList.remove('btn-success');
          element.classList.add('connected', 'btn-warning');
          element.title = 'Mark Planned';
          icon.classList.remove('mdi-lan-connect');
          icon.classList.add('mdi-lan-disconnect');
        }

        // Get the button's row to change its styles.
        const row = element.parentElement?.parentElement as HTMLTableRowElement;

        // Get the previous state of the cable so we know what CSS class was there before
        const wasConnected = row.classList.contains('green');
        const wasPlanned = row.classList.contains('blue');
        const wasDecommissioning = row.classList.contains('yellow');

        // Remove the appropriate CSS classes
        if (wasConnected) {
          row.classList.remove('green');
        }
        if (wasPlanned) {
          row.classList.remove('blue');
        }
        if (wasDecommissioning) {
          row.classList.remove('yellow');
        }

        // Only add a new CSS class if we removed an old one! Not removing an old CSS class
        // can happen if the interface is disabled. In that case the row colour should be
        // red no matter what, so don't touch it to add a new one.
        if (wasConnected || wasPlanned || wasDecommissioning) {
          if (status == 'connected') {
            row.classList.add('green'); // connected
          } else {
            row.classList.add('blue'); // planned
          }
        }
      }
    });
  }
}

export function initConnectionToggle(): void {
  for (const element of getElements<HTMLButtonElement>('button.cable-toggle')) {
    element.addEventListener('click', () => toggleConnection(element));
  }
}
