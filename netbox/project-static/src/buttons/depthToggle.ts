import { objectDepthState } from '../stores';
import { getElements } from '../util';

import type { StateManager } from '../state';

type ObjectDepthState = { hidden: boolean };

/**
 * Change toggle button's text and attribute to reflect the current state.
 *
 * @param hidden `true` if the current state is hidden, `false` otherwise.
 * @param button Toggle element.
 */
function toggleDepthButton(hidden: boolean, button: HTMLButtonElement): void {
  button.setAttribute('data-depth-indicators', hidden ? 'hidden' : 'shown');
  button.innerText = hidden ? 'Show Depth Indicators' : 'Hide Depth Indicators';
}

/**
 * Show all depth indicators.
 */
function showDepthIndicators(): void {
  for (const element of getElements<HTMLDivElement>('.record-depth')) {
    element.style.display = '';
  }
}

/**
 * Hide all depth indicators.
 */
function hideDepthIndicators(): void {
  for (const element of getElements<HTMLDivElement>('.record-depth')) {
    element.style.display = 'none';
  }
}

/**
 * Update object depth local state and visualization when the button is clicked.
 *
 * @param state State instance.
 * @param button Toggle element.
 */
function handleDepthToggle(state: StateManager<ObjectDepthState>, button: HTMLButtonElement): void {
  const initiallyHidden = state.get('hidden');
  state.set('hidden', !initiallyHidden);
  const hidden = state.get('hidden');

  if (hidden) {
    hideDepthIndicators();
  } else {
    showDepthIndicators();
  }
  toggleDepthButton(hidden, button);
}

/**
 * Initialize object depth toggle buttons.
 */
export function initDepthToggle(): void {
  const initiallyHidden = objectDepthState.get('hidden');

  for (const button of getElements<HTMLButtonElement>('button.toggle-depth')) {
    toggleDepthButton(initiallyHidden, button);

    button.addEventListener(
      'click',
      event => {
        handleDepthToggle(objectDepthState, event.currentTarget as HTMLButtonElement);
      },
      false,
    );
  }
  // Synchronize local state with default DOM elements.
  if (initiallyHidden) {
    hideDepthIndicators();
  } else if (!initiallyHidden) {
    showDepthIndicators();
  }
}
