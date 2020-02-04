$('.rendered-context-format').on('click', function() {
    if (!$(this).hasClass('active')) {
        // Update selection in the button group
        $('span.rendered-context-format').removeClass('active');
        $('span.rendered-context-format[data-format=' + $(this).data('format') + ']').addClass('active');

        // Hide all rendered contexts and only show the selected one
        $('div.rendered-context-data').hide();
        $('div.rendered-context-data[data-format=' + $(this).data('format') + ']').show();
    }
});
