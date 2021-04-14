import { apiGetBase, getElements, isApiError } from './util';
/**
 * 
 * $('#generate_keypair').click(function() {
        $('#new_keypair_modal').modal('show');
        $.ajax({
            url: netbox_api_path + 'secrets/generate-rsa-key-pair/',
            type: 'GET',
            dataType: 'json',
            success: function (response, status) {
                var public_key = response.public_key;
                var private_key = response.private_key;
                $('#new_pubkey').val(public_key);
                $('#new_privkey').val(private_key);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert("There was an error generating a new key pair.");
            }
        });
    });
 */
export function initGenerateKeyPair() {
  const element = document.getElementById('new_keypair_modal') as HTMLDivElement;
  const accept = document.getElementById('use_new_pubkey') as HTMLButtonElement;
  const publicElem = element.querySelector<HTMLTextAreaElement>('textarea#new_pubkey');
  const privateElem = element.querySelector<HTMLTextAreaElement>('textarea#new_privkey');

  function handleOpen() {
    for (const elem of [publicElem, privateElem]) {
      if (elem !== null) {
        elem.setAttribute('readonly', '');
      }
    }

    apiGetBase<APIKeyPair>('/api/secrets/generate-rsa-key-pair').then(data => {
      if (!isApiError(data)) {
        const { private_key: priv, public_key: pub } = data;
        if (publicElem !== null && privateElem !== null) {
          publicElem.value = pub;
          privateElem.value = priv;
        }
      }
    });
  }
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

export function initLockUnlock() {
  for (const element of getElements<HTMLButtonElement>('button.unlock-secret')) {
    function handleClick() {
      const { secretId } = element.dataset;
    }
  }
}
