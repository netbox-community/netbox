function toggleConnection(elem) {
    var url = netbox_api_path + "dcim/cables/" + elem.attr('data') + "/";
    if (elem.hasClass('connected')) {
        $.ajax({
            url: url,
            method: 'PATCH',
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", netbox_csrf_token);
            },
            data: {
                'status': 'planned'
            },
            context: this,
            success: function() {
                elem.parents('tr').removeClass('success').addClass('info');
                elem.removeClass('connected btn-warning').addClass('btn-success');
                elem.attr('title', 'Mark installed');
                elem.children('i').removeClass('mdi mdi-lan-disconnect').addClass('mdi mdi-lan-connect')
            }
        });
    } else {
        $.ajax({
            url: url,
            method: 'PATCH',
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", netbox_csrf_token);
            },
            data: {
                'status': 'connected'
            },
            context: this,
            success: function() {
                elem.parents('tr').removeClass('info').addClass('success');
                elem.removeClass('btn-success').addClass('connected btn-warning');
                elem.attr('title', 'Mark planned');
                elem.children('i').removeClass('mdi mdi-lan-connect').addClass('mdi mdi-lan-disconnect')
            }
        });
    }
    return false;
}
$(".cable-toggle").click(function() {
    return toggleConnection($(this));
});
