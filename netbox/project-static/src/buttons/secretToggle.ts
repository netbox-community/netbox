import { secretState } from '../stores';
import { getElement, getElements, isTruthy } from '../util';

import type { StateManager } from '../state';

type SecretState = { hidden: boolean };

/**
 * Change toggle button's text and attribute to reflect the current state.
 *
 * @param hidden `true` if the current state is hidden, `false` otherwise.
 * @param button Toggle element.
 */
function toggleSecretButton(hidden: boolean, button: HTMLButtonElement): void {
  button.setAttribute('data-secret-visibility', hidden ? 'hidden' : 'shown');
  button.innerText = hidden ? 'Show Secret' : 'Hide Secret';
}

/**
 * Show secret.
 */
function showSecret(): void {
  const secret = getElement('secret');
  if (isTruthy(secret)) {
    const value = secret.getAttribute('data-secret');
    if (isTruthy(value)) {
      secret.innerText = value;
    }
  }
}

/**
 * Hide secret.
 */
function hideSecret(): void {
  const secret = getElement('secret');
  if (isTruthy(secret)) {
    const value = secret.getAttribute('data-secret');
    if (isTruthy(value)) {
      secret.innerText = '••••••••';
    }
  }
}

/**
 * Update secret state and visualization when the button is clicked.
 *
 * @param state State instance.
 * @param button Toggle element.
 */
function handleSecretToggle(state: StateManager<SecretState>, button: HTMLButtonElement): void {
  state.set('hidden', !state.get('hidden'));
  const hidden = state.get('hidden');

  if (hidden) {
    hideSecret();
  } else {
    showSecret();
  }
  toggleSecretButton(hidden, button);
}

/**
 * Initialize secret toggle button.
 */
export function initSecretToggle(): void {
  hideSecret();
  for (const button of getElements<HTMLButtonElement>('button.toggle-secret')) {
    button.addEventListener(
      'click',
      event => {
        handleSecretToggle(secretState, event.currentTarget as HTMLButtonElement);
      },
      false,
    );
  }
}
