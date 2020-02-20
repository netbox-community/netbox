// Toggle the display of device images within an SVG rack elevation
$('button.toggle-images').click(function() {
    var selected = $(this).attr('selected');
    var rack_front = $("#rack_front");
    var rack_rear = $("#rack_rear");
    if (selected) {
        $('.device-image', rack_front.contents()).addClass('hidden');
        $('.device-image', rack_rear.contents()).addClass('hidden');
    } else {
        $('.device-image', rack_front.contents()).removeClass('hidden');
        $('.device-image', rack_rear.contents()).removeClass('hidden');
    }
    $(this).attr('selected', !selected);
    $(this).children('span').toggleClass('glyphicon-check glyphicon-unchecked');
    return false;
});
