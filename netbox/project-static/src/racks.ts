import { rackImagesState } from './stores';
import { getElements } from './util';

import type { StateManager } from './state';

type RackToggleState = { hidden: boolean };

/**
 * Toggle the Rack Image button to reflect the current state. If the current state is hidden and
 * the images are therefore hidden, the button should say "Show Images". Likewise, if the current
 * state is *not* hidden, and therefore the images are shown, the button should say "Hide Images".
 *
 * @param hidden Current State - `true` if images are hidden, `false` otherwise.
 * @param button Button element.
 */
function toggleRackImagesButton(hidden: boolean, button: HTMLButtonElement): void {
  const text = hidden ? 'Show Images' : 'Hide Images';
  const selected = hidden ? '' : 'selected';
  button.setAttribute('selected', selected);
  button.innerHTML = `<i class="mdi mdi-file-image-outline"></i>&nbsp;${text}`;
}

/**
 * Show all rack images.
 */
function showRackImages(): void {
  for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
    const images = elevation.contentDocument?.querySelectorAll('image.device-image') ?? [];
    for (const image of images) {
      image.classList.remove('hidden');
    }
  }
}

/**
 * Hide all rack images.
 */
function hideRackImages(): void {
  for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
    const images = elevation.contentDocument?.querySelectorAll('image.device-image') ?? [];
    for (const image of images) {
      image.classList.add('hidden');
    }
  }
}

/**
 * Toggle the visibility of device images and update the toggle button style.
 */
function handleRackImageToggle(
  target: HTMLButtonElement,
  state: StateManager<RackToggleState>,
): void {
  const initiallyHidden = state.get('hidden');
  state.set('hidden', !initiallyHidden);
  const hidden = state.get('hidden');

  if (hidden) {
    hideRackImages();
  } else {
    showRackImages();
  }
  toggleRackImagesButton(hidden, target);
}

/**
 * Add onClick callback for toggling rack elevation images. Synchronize the image toggle button
 * text and display state of images with the local state.
 */
export function initRackElevation(): void {
  const initiallyHidden = rackImagesState.get('hidden');
  for (const button of getElements<HTMLButtonElement>('button.toggle-images')) {
    toggleRackImagesButton(initiallyHidden, button);

    button.addEventListener(
      'click',
      event => {
        handleRackImageToggle(event.currentTarget as HTMLButtonElement, rackImagesState);
      },
      false,
    );
  }
  for (const element of getElements<HTMLObjectElement>('.rack_elevation')) {
    element.addEventListener('load', () => {
      if (initiallyHidden) {
        hideRackImages();
      } else if (!initiallyHidden) {
        showRackImages();
      }
    });
  }
}
