import { createToast } from '../bs';
import { isTruthy, apiPatch, hasError, getElements } from '../util';

/**
 * When the toggle button is clicked, swap the connection status via the API and toggle CSS
 * classes to reflect the connection status.
 *
 * @param element Connection Toggle Button Element
 */
function setConnectionStatus(element: HTMLButtonElement, status: string): void {
  // Get the button's row to change its data-cable-status attribute
  const row = element.parentElement?.parentElement as HTMLTableRowElement;
  const url = element.getAttribute('data-url');

  if (isTruthy(url)) {
    apiPatch(url, { status }).then(res => {
      if (hasError(res)) {
        // If the API responds with an error, show it to the user.
        createToast('danger', 'Error', res.error).show();
        return;
      } else {
        // Update cable status in DOM
        row.setAttribute('data-cable-status', status);
      }
    });
  }
}

export function initConnectionToggle(): void {
  for (const element of getElements<HTMLButtonElement>('button.mark-planned')) {
    element.addEventListener('click', () => setConnectionStatus(element, 'planned'));
  }
  for (const element of getElements<HTMLButtonElement>('button.mark-installed')) {
    element.addEventListener('click', () => setConnectionStatus(element, 'connected'));
  }
}
