$(document).ready(function() {
    $('form.tableconfigform').submit(function(event) {
        event.preventDefault();
        let table_name = this.getAttribute('data-table-name');
        let data = {"tables": {}};
        data['tables'][table_name] = {};
        data['tables'][table_name]['columns'] = $('#id_columns').val();
        $.ajax({
            url: netbox_api_path + 'users/config/',
            async: true,
            contentType: 'application/json',
            dataType: 'json',
            type: 'PATCH',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", netbox_csrf_token);
            },
            data: JSON.stringify(data),
        }).done(function () {
            // Reload the page
            window.location.reload(true);
        }).fail(function (xhr, status, error) {
            alert("Failed: " + error);
        });
    });
});
