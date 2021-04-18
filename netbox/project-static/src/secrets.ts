import { Modal } from 'bootstrap';
import { apiGetBase, apiPostForm, getElements, isApiError, hasError } from './util';
import { createToast } from './toast';

/**
 * Initialize Generate Private Key Pair Elements.
 */
export function initGenerateKeyPair() {
  const element = document.getElementById('new_keypair_modal') as HTMLDivElement;
  const accept = document.getElementById('use_new_pubkey') as HTMLButtonElement;
  // If the elements are not loaded, stop.
  if (element === null || accept === null) {
    return;
  }
  const publicElem = element.querySelector<HTMLTextAreaElement>('textarea#new_pubkey');
  const privateElem = element.querySelector<HTMLTextAreaElement>('textarea#new_privkey');

  /**
   * Handle Generate Private Key Pair Modal opening.
   */
  function handleOpen() {
    // When the modal opens, set the `readonly` attribute on the textarea elements.
    for (const elem of [publicElem, privateElem]) {
      if (elem !== null) {
        elem.setAttribute('readonly', '');
      }
    }
    // Fetch the key pair from the API.
    apiGetBase<APIKeyPair>('/api/secrets/generate-rsa-key-pair').then(data => {
      if (!hasError(data)) {
        // If key pair generation was successful, set the textarea elements' value to the generated
        // values.
        const { private_key: priv, public_key: pub } = data;
        if (publicElem !== null && privateElem !== null) {
          publicElem.value = pub;
          privateElem.value = priv;
        }
      } else {
        // Otherwise, show an error.
        const toast = createToast('danger', 'Error', data.error);
        toast.show();
      }
    });
  }
  /**
   * Set the public key form field's value to the generated public key.
   */
  function handleAccept() {
    const publicKeyField = document.getElementById('id_public_key') as HTMLTextAreaElement;
    if (publicElem !== null) {
      publicKeyField.value = publicElem.value;
      publicKeyField.innerText = publicElem.value;
    }
  }
  element.addEventListener('shown.bs.modal', handleOpen);
  accept.addEventListener('click', handleAccept);
}

/**
 * Toggle copy/lock/unlock button visibility based on the action occurring.
 * @param id Secret ID.
 * @param action Lock or Unlock, so we know which buttons to display.
 */
function toggleSecretButtons(id: string, action: 'lock' | 'unlock') {
  const unlockButton = document.querySelector(`button.unlock-secret[secret-id='${id}']`);
  const lockButton = document.querySelector(`button.lock-secret[secret-id='${id}']`);
  const copyButton = document.querySelector(`button.copy-secret[secret-id='${id}']`);

  // If we're unlocking, hide the unlock button. Otherwise, show it.
  if (unlockButton !== null) {
    if (action === 'unlock') unlockButton.classList.add('d-none');
    if (action === 'lock') unlockButton.classList.remove('d-none');
  }
  // If we're unlocking, show the lock button. Otherwise, hide it.
  if (lockButton !== null) {
    if (action === 'unlock') lockButton.classList.remove('d-none');
    if (action === 'lock') lockButton.classList.add('d-none');
  }
  // If we're unlocking, show the copy button. Otherwise, hide it.
  if (copyButton !== null) {
    if (action === 'unlock') copyButton.classList.remove('d-none');
    if (action === 'lock') copyButton.classList.add('d-none');
  }
}

/**
 * Initialize Lock & Unlock button event listeners & callbacks.
 */
export function initLockUnlock() {
  const privateKeyModalElem = document.getElementById('privkey_modal');
  if (privateKeyModalElem === null) {
    return;
  }
  const privateKeyModal = new Modal(privateKeyModalElem);

  /**
   * Unlock a secret, or prompt the user for their private key, if a session key is not available.
   *
   * @param id Secret ID
   */
  function unlock(id: string | null) {
    const target = document.getElementById(`secret_${id}`);
    if (typeof id === 'string' && id !== '') {
      apiGetBase<APISecret>(`/api/secrets/secrets/${id}`).then(data => {
        if (!hasError(data)) {
          const { plaintext } = data;
          // `plaintext` is the plain text value of the secret. If it is null, it has not been
          // decrypted, likely due to a mission session key.

          if (target !== null && plaintext !== null) {
            // If `plaintext` is not null, we have the decrypted value. Set the target element's
            // inner text to the decrypted value and toggle copy/lock button visibility.
            target.innerText = plaintext;
            toggleSecretButtons(id, 'unlock');
          } else {
            // Otherwise, we do _not_ have the decrypted value and need to prompt the user for
            // their private RSA key, in order to get a session key. The session key is then sent
            // as a cookie in future requests.
            privateKeyModal.show();
          }
        } else {
          if (data.error.toLowerCase().includes('invalid session key')) {
            // If, for some reason, a request was made but resulted in an API error that complains
            // of a missing session key, prompt the user for their session key.
            privateKeyModal.show();
          } else {
            // If we received an API error but it doesn't contain 'invalid session key', show the
            // user an error message.
            const toast = createToast('danger', 'Error', data.error);
            toast.show();
          }
        }
      });
    }
  }
  /**
   * Lock a secret and toggle visibility of the unlock button.
   * @param id Secret ID
   */
  function lock(id: string | null) {
    if (typeof id === 'string' && id !== '') {
      const target = document.getElementById(`secret_${id}`);
      if (target !== null) {
        // Obscure the inner text of the secret element.
        target.innerText = '********';
      }
      // Toggle visibility of the copy/lock/unlock buttons.
      toggleSecretButtons(id, 'lock');
    }
  }

  for (const element of getElements<HTMLButtonElement>('button.unlock-secret')) {
    element.addEventListener('click', () => unlock(element.getAttribute('secret-id')));
  }
  for (const element of getElements<HTMLButtonElement>('button.lock-secret')) {
    element.addEventListener('click', () => lock(element.getAttribute('secret-id')));
  }
}

/**
 * Request a session key from the API.
 * @param privateKey RSA Private Key (valid JSON string)
 */
function requestSessionKey(privateKey: string) {
  apiPostForm('/api/secrets/get-session-key/', { private_key: privateKey }).then(res => {
    if (!hasError(res)) {
      // If the response received was not an error, show the user a success message.
      const toast = createToast('success', 'Session Key Received', 'You may now unlock secrets.');
      toast.show();
    } else {
      // Otherwise, show the user an error message.
      let message = res.error;
      if (isApiError(res)) {
        // If the error received was a standard API error containing a Python exception message,
        // append it to the error.
        message += `\n${res.exception}`;
      }
      const toast = createToast('danger', 'Failed to Retrieve Session Key', message);
      toast.show();
    }
  });
}

/**
 * Initialize Request Session Key Elements.
 */
export function initGetSessionKey() {
  for (const element of getElements<HTMLButtonElement>('#request_session_key')) {
    /**
     * Send the user's input private key to the API to get a session key, which will be stored as
     * a cookie for future requests.
     */
    function handleClick() {
      for (const pk of getElements<HTMLTextAreaElement>('#user_privkey')) {
        requestSessionKey(pk.value);
        // Clear the private key form field value.
        pk.value = '';
      }
    }
    element.addEventListener('click', handleClick);
  }
}
