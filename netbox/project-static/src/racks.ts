import { rackImagesState, RackViewSelection } from './stores';
import { getElements } from './util';

import type { StateManager } from './state';

export type RackViewState = { view: RackViewSelection };

/**
 * Show or hide images and labels to build the desired rack view.
 */
function setRackView(
  view: RackViewSelection,
  elevation: HTMLObjectElement,
): void {
  switch(view) {
    case 'images-and-labels': {
      showRackElements('image.device-image', elevation);
      showRackElements('text.device-image-label', elevation);
      break;
    }
    case 'images-only': {
      showRackElements('image.device-image', elevation);
      hideRackElements('text.device-image-label', elevation);
      break;
    }
    case 'labels-only': {
      hideRackElements('image.device-image', elevation);
      hideRackElements('text.device-image-label', elevation);
      break;
    }
  }
}

function showRackElements(
  selector: string,
  elevation: HTMLObjectElement,
): void {
  const elements = elevation.contentDocument?.querySelectorAll(selector) ?? [];
  for (const element of elements) {
    element.classList.remove('hidden');
  }
}

function hideRackElements(
  selector: string,
  elevation: HTMLObjectElement,
): void {
  const elements = elevation.contentDocument?.querySelectorAll(selector) ?? [];
  for (const element of elements) {
    element.classList.add('hidden');
  }
}

/**
 * Change the visibility of all racks in response to selection.
 */
function handleRackViewSelect(
  newView: RackViewSelection,
  state: StateManager<RackViewState>,
): void {
  state.set('view', newView);
  for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
    setRackView(newView, elevation);
  }
}

/**
 * Add change callback for selecting rack elevation images, and set
 * initial state of select and the images themselves
 */
export function initRackElevation(): void {
  const initialView = rackImagesState.get('view');

  for (const control of getElements<HTMLSelectElement>('select.rack-view')) {
    control.selectedIndex = [...control.options].findIndex(o => o.value == initialView);
    control.addEventListener(
      'change',
      event => {
        handleRackViewSelect((event.currentTarget as any).value as RackViewSelection, rackImagesState);
      },
      false,
    );
  }

  for (const element of getElements<HTMLObjectElement>('.rack_elevation')) {
    element.addEventListener('load', () => {
      setRackView(initialView, element);
    });
  }
}
