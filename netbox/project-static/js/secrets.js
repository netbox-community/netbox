$(document).ready(function() {

    // Unlocking a secret
    $('button.unlock-secret').click(function (event) {
        var secret_id = $(this).attr('secret-id');

        // Retrieve from storage or prompt for private key
        var private_key = sessionStorage.getItem('private_key');
        if (!private_key) {
            $('#privkey_modal').modal('show');
        } else {
            unlock_secret(secret_id, private_key);
        }
    });

    // Locking a secret
    $('button.lock-secret').click(function (event) {
        var secret_id = $(this).attr('secret-id');
        var secret_div = $('#secret_' + secret_id);

        // Delete the plaintext
        secret_div.html('********');
        $(this).hide();
        $(this).siblings('button.unlock-secret').show();
    });

    // Adding/editing a secret
    $('form.requires-private-key').submit(function(event) {
        var private_key = sessionStorage.getItem('private_key');
        if (private_key) {
            $('#id_private_key').val(private_key);
        } else {
            $('#privkey_modal').modal('show');
            return false;
        }
    });

    // Prompt the user to enter a private RSA key for decryption
    $('#submit_privkey').click(function() {
        var private_key = $('#user_privkey').val();
        sessionStorage.setItem('private_key', private_key);
    });

    // Generate a new public/private key pair via the API
    $('#generate_keypair').click(function() {
        $('#new_keypair_modal').modal('show');
        $.ajax({
            url: '/api/secrets/generate-keys/',
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

    // Enter a newly generated public key
    $('#use_new_pubkey').click(function() {
        var new_pubkey = $('#new_pubkey');
        if (new_pubkey.val()) {
            $('#id_public_key').val(new_pubkey.val());
        }
    });

    // Retrieve a secret via the API
    function unlock_secret(secret_id, private_key) {
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: '/api/secrets/secrets/' + secret_id + '/',
            type: 'POST',
            data: {
                private_key: private_key
            },
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            success: function (response, status) {
                $('#secret_' + secret_id).html(response.plaintext);
                $('button.unlock-secret').hide();
                $('button.lock-secret').show();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                if (xhr.status == 403) {
                    alert("Permission denied");
                } else {
                    var json = jQuery.parseJSON(xhr.responseText);
                    alert("Decryption failed: " + json['error']);
                }
            }
        });
    }

});
