// Inteface filtering
$('input.interface-filter').on('input', function() {
    var filter = new RegExp(this.value);
    var interface;

    for (interface of $('table > tbody > tr')) {
        // Slice off 'interface_' at the start of the ID
        if (filter.test(interface.id.slice(10))) {
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
