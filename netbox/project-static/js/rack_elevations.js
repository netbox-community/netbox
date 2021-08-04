// Toggle the display of device images within an SVG rack elevation
$('button.toggle-images').click(function() {
    var selected = $(this).attr('selected');
    var rack_elevation = $(".rack_elevation");
    if (selected) {
        $('.device-image', rack_elevation.contents()).addClass('hidden');
    } else {
        $('.device-image', rack_elevation.contents()).removeClass('hidden');
    }
    $(this).attr('selected', !selected);
    $(this).children('span').toggleClass('mdi-checkbox-marked-circle-outline mdi-checkbox-blank-circle-outline');
    return false;
});
// Toggle the display of device labels within an SVG rack elevation
$('button.toggle-labels').click(function() {
    var selected = $(this).attr('selected');
    var rack_elevation = $(".rack_elevation");
    if (selected) {
        $('.device-label', rack_elevation.contents()).addClass('hidden');
    } else {
        $('.device-label', rack_elevation.contents()).removeClass('hidden');
    }
    $(this).attr('selected', !selected);
    $(this).children('span').toggleClass('mdi-checkbox-marked-circle-outline mdi-checkbox-blank-circle-outline');
    return false;
});
