import { setColorMode } from '../colorMode';
import { getElement } from '../util';

/**
 * Perform actions in the UI based on the value of user profile updates.
 *
 * @param event Form Submit
 */
function handlePreferenceSave(event: Event): void {
  // Create a FormData instance to access the form values.
  const form = event.currentTarget as HTMLFormElement;
  const formData = new FormData(form);

  // Update the UI color mode immediately when the user preference changes.
  if (formData.get('ui.colormode') === 'dark') {
    setColorMode('dark');
  } else if (formData.get('ui.colormode') === 'light') {
    setColorMode('light');
  }
}

/**
 * Initialize handlers for user profile updates.
 */
export function initPreferenceUpdate(): void {
  const form = getElement<HTMLFormElement>('preferences-update');
  if (form !== null) {
    form.addEventListener('submit', handlePreferenceSave);
  }
}
