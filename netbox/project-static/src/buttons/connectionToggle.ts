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
        // Get the button's row to change its styles.
        const row = element.parentElement?.parentElement as HTMLTableRowElement;
        // Get the button's icon to change its CSS class.
        const icon = element.querySelector('i.mdi, span.mdi') as HTMLSpanElement;
        if (connected) {
          row.classList.remove('success');
          row.classList.add('info');
          element.classList.remove('connected', 'btn-warning');
          element.classList.add('btn-info');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-disconnect');
          icon.classList.add('mdi-lan-connect');
        } else {
          row.classList.remove('info');
          row.classList.add('success');
          element.classList.remove('btn-success');
          element.classList.add('connected', 'btn-warning');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-connect');
          icon.classList.add('mdi-lan-disconnect');
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
