// Toggle the display of IP addresses under interfaces
$('button.toggle-ips').click(function() {
    var selected = $(this).attr('selected');
    if (selected) {
        $('#interfaces_table tr.ipaddresses').hide();
    } else {
        $('#interfaces_table tr.ipaddresses').show();
    }
    $(this).attr('selected', !selected);
    $(this).children('span').toggleClass('glyphicon-check glyphicon-unchecked');
    return false;
});

// Inteface filtering
$('input.interface-filter').on('input', function() {
    var filter = new RegExp(this.value);

    for (interface of $(this).closest('div.panel').find('tbody > tr')) {
        // Slice off 'interface_' at the start of the ID
        if (filter && filter.test(interface.id.slice(10))) {
            // Match the toggle in case the filter now matches the interface
            $(interface).find('input:checkbox[name=pk]').prop('checked', $('input.toggle').prop('checked'));
            $(interface).show();
        } else {
            // Uncheck to prevent actions from including it when it doesn't match
            $(interface).find('input:checkbox[name=pk]').prop('checked', false);
            $(interface).hide();
        }
    }
});
