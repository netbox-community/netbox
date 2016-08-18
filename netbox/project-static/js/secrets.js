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
    private_key_field = $('#id_private_key');
    private_key_field.parents('form').submit(function(event) {
        console.log("form submitted");
        var private_key = sessionStorage.getItem('private_key');
        if (private_key) {
            private_key_field.val(private_key);
        } else if ($('form .requires-private-key:first').val()) {
            console.log("we need a key!");
            $('#privkey_modal').modal('show');
            return false;
        }
    });

    // Saving a private RSA key locally
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
                $('button.unlock-secret[secret-id=' + secret_id + ']').hide();
                $('button.lock-secret[secret-id=' + secret_id + ']').show();
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
