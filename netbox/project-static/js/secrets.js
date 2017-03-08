$(document).ready(function() {

    // Unlocking a secret
    $('button.unlock-secret').click(function (event) {
        var secret_id = $(this).attr('secret-id');

        // If we have an active cookie containing a session key, send the API request.
        if (document.cookie.indexOf('session_key') > 0) {
            console.log("Retrieving secret...");
            unlock_secret(secret_id);
        // Otherwise, prompt the user for a private key so we can request a session key.
        } else {
            console.log("No session key found. Prompt user for private key.");
            $('#privkey_modal').modal('show');
        }

    });

    // Locking a secret
    $('button.lock-secret').click(function (event) {
        var secret_id = $(this).attr('secret-id');
        var secret_div = $('#secret_' + secret_id);

        // Delete the plaintext from the DOM element.
        secret_div.html('********');
        $(this).hide();
        $(this).siblings('button.unlock-secret').show();
    });

    // Retrieve a session key
    $('#request_session_key').click(function() {
        var private_key = $('#user_privkey').val();

        // POST the user's private key to request a temporary session key.
        console.log("Requesting a session key...");
        get_session_key(private_key);
    });

    // Retrieve a secret via the API
    function unlock_secret(secret_id) {
        $.ajax({
            url: netbox_api_path + 'secrets/secrets/' + secret_id + '/',
            type: 'GET',
            dataType: 'json',
            success: function (response, status) {
                console.log("Secret retrieved successfully");
                $('#secret_' + secret_id).html(response.plaintext);
                $('button.unlock-secret[secret-id=' + secret_id + ']').hide();
                $('button.lock-secret[secret-id=' + secret_id + ']').show();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log("Error: " + xhr.responseText);
                if (xhr.status == 403) {
                    alert("Permission denied");
                } else {
                    var json = jQuery.parseJSON(xhr.responseText);
                    alert("Secret retrieval failed: " + json['error']);
                }
            }
        });
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
                console.log("Received a new session key; valid until " + response.expiration_time);
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
