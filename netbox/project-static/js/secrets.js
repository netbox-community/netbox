$(document).ready(function() {

    // Unlocking a secret
    $('button.unlock-secret').click(function(event) {
        var secret_id = $(this).attr('secret-id');
        unlock_secret(secret_id);
        event.preventDefault();
    });

    // Locking a secret
    $('button.lock-secret').click(function(event) {
        var secret_id = $(this).attr('secret-id');
        lock_secret(secret_id);
        event.preventDefault();
    });

    // Adding/editing a secret
    $('form').submit(function(event) {
        $(this).find('.requires-session-key').each(function() {
            if (this.value && document.cookie.indexOf('session_key') == -1) {
                console.log('Field ' + this.name + ' requires a session key');
                $('#privkey_modal').modal('show');
                event.preventDefault();
                return false;
            }
        });
    });

    // Retrieve a session key
    $('#request_session_key').click(function() {
        var private_key_field = $('#user_privkey');
        var private_key = private_key_field.val();
        get_session_key(private_key);
        private_key_field.val("");
    });

    // Retrieve a secret via the API
    function unlock_secret(secret_id) {
        $.ajax({
            url: netbox_api_path + 'secrets/secrets/' + secret_id + '/',
            type: 'GET',
            dataType: 'json',
            success: function (response, status) {
                if (response.plaintext) {
                    console.log("Secret retrieved successfully");
                    $('#secret_' + secret_id).text(response.plaintext);
                    $('button.unlock-secret[secret-id=' + secret_id + ']').hide();
                    $('button.lock-secret[secret-id=' + secret_id + ']').show();
                } else {
                    console.log("Secret was not decrypted. Prompt user for private key.");
                    $('#privkey_modal').modal('show');
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log("Error: " + xhr.responseText);
                if (xhr.status == 403) {
                    alert("Permission denied");
                } else {
                    alert(xhr.responseText);
                }
            }
        });
    }

    // Remove secret data from the DOM
    function lock_secret(secret_id) {
        var secret_div = $('#secret_' + secret_id);
        secret_div.html('********');
        $('button.lock-secret[secret-id=' + secret_id + ']').hide();
        $('button.unlock-secret[secret-id=' + secret_id + ']').show();
    }

    // Request a session key via the API
    function get_session_key(private_key) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: netbox_api_path + 'secrets/get-session-key/',
            type: 'POST',
            data: {
                private_key: private_key
            },
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            success: function (response, status) {
                console.log("Received a new session key");
                alert('Session key received! You may now unlock secrets.');
            },
            error: function (xhr, ajaxOptions, thrownError) {
                if (xhr.status == 403) {
                    alert("Permission denied");
                } else {
                    var json = jQuery.parseJSON(xhr.responseText);
                    alert("Failed to retrieve a session key: " + json['error']);
                }
            }
        });
    }

    // Generate a new public/private key pair via the API
    $('#generate_keypair').click(function() {
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

    // Accept a new RSA key pair generated via the API
    $('#use_new_pubkey').click(function() {
        var new_pubkey = $('#new_pubkey');

        if (new_pubkey.val()) {
            $('#id_public_key').val(new_pubkey.val());
        }
    });

});
