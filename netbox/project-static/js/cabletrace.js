$('#cabletrace_modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var obj = button.data('obj');
    var url = button.data('url');
    var modal_title = $(this).find('.modal-title');
    var modal_body = $(this).find('.modal-body');
    modal_title.text(obj);
    modal_body.empty();
    $.ajax({
        url: url,
        dataType: 'json',
        success: function(json) {
            $.each(json, function(i, segment) {
                modal_body.append(
                    '<div class="row">' +
                      '<div class="col-md-4 text-center">' + segment[0].device.name + '<br />' + segment[0].name + '</div>' +
                      '<div class="col-md-4 text-center">Cable #' + segment[1].id + '</div>' +
                      '<div class="col-md-4 text-center">' + segment[2].device.name + '<br />' + segment[2].name + '</div>' +
                    '</div><hr />'
                );
            })
        }
    });
});
