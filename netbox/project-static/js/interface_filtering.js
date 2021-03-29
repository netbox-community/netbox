// Inteface filtering
$('input.interface-filter').on('input', function() {
    let filter = new RegExp(this.value);
    let interface;

    for (interface of $('table > tbody > tr')) {
        if (filter.test(interface.getAttribute('data-name'))) {
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
