import { getElements } from '../util';
import { Modal } from 'bootstrap';

export function initLaunchModal(): void {
  console.log('initLaunchModal()');
  const modal_element = document.getElementById('htmx-modal');
  if (modal_element == null) return;
  console.log('found modal element');
  const modal = new Modal(modal_element);
  console.log('created modal');

  for (const launchButton of getElements<HTMLButtonElement>('button.launch-htmx-modal')) {
    console.log(`found button: {launchButton}`);
    launchButton.addEventListener('click', () => {
      modal.show();
    });
  }
}
