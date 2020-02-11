// Toggle the display of IP addresses under interfaces
$('button.toggle-ips').click(function() {
    var selected = $(this).attr('selected');
    if (selected) {
        $('.ipaddresses').hide();
    } else {
        $('.ipaddresses').show();
    }
    $(this).attr('selected', !selected);
    $(this).children('span').toggleClass('glyphicon-check glyphicon-unchecked');
    return false;
});


//Toggle the display of VLANs
$('button.toggle-vlans').click(function(){
   var selected = $(this).attr('selected');
   if (selected) {
        $('.vlans').hide();
    } else {
        $('.vlans').show();
    }
    $(this).attr('selected', !selected);
    $(this).children('span').toggleClass('glyphicon-check glyphicon-unchecked');
    return false;
});

// Inteface filtering
$('input.interface-filter').on('input', function() {
    var filter = new RegExp(this.value);
    var interface;

    for (interface of $('#interfaces_table > tbody > tr.interface')) {
        // Slice off 'interface_' at the start of the ID
        if (filter.test(interface.id.slice(10))) {
            // Match the toggle in case the filter now matches the interface
            $(interface).find('input:checkbox[name=pk]').prop('checked', $('input.toggle').prop('checked'));
            $(interface).show();
            if ($('button.toggle-ips').attr('selected')) {
                $(interface).next('tr.ipaddresses').show();
            }
        } else {
            // Uncheck to prevent actions from including it when it doesn't match
            $(interface).find('input:checkbox[name=pk]').prop('checked', false);
            $(interface).hide();
            $(interface).next('tr.ipaddresses').hide();
        }
    }
});
