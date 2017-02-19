$(document).ready(function() {

    // "Toggle all" checkbox (table header)
    $('#toggle_all').click(function (event) {
        $('td input:checkbox[name=pk]').prop('checked', $(this).prop('checked'));
        if ($(this).is(':checked')) {
            $('#select_all_box').removeClass('hidden');
        } else {
            $('#select_all').prop('checked', false);
        }
    });
    // Enable hidden buttons when "select all" is checked
    $('#select_all').click(function (event) {
        if ($(this).is(':checked')) {
            $('#select_all_box').find('button').prop('disabled', '');
        } else {
            $('#select_all_box').find('button').prop('disabled', 'disabled');
        }
    });
    // Uncheck the "toggle all" checkbox if an item is unchecked
    $('input:checkbox[name=pk]').click(function (event) {
        if (!$(this).attr('checked')) {
            $('#select_all, #toggle_all').prop('checked', false);
        }
    });

    // Simple "Toggle all" button (panel)
    $('button.toggle').click(function (event) {
        var selected = $(this).attr('selected');
        $(this).closest('form').find('input:checkbox[name=pk]').prop('checked', !selected);
        $(this).attr('selected', !selected);
        $(this).children('span').toggleClass('glyphicon-unchecked glyphicon-check');
        return false;
    });

    // Slugify
    function slugify(s, num_chars) {
        s = s.replace(/[^\-\.\w\s]/g, '');          // Remove unneeded chars
        s = s.replace(/^[\s\.]+|[\s\.]+$/g, '');    // Trim leading/trailing spaces
        s = s.replace(/[\-\.\s]+/g, '-');           // Convert spaces and decimals to hyphens
        s = s.toLowerCase();                        // Convert to lowercase
        return s.substring(0, num_chars);           // Trim to first num_chars chars
    }
    var slug_field = $('#id_slug');
    slug_field.change(function() {
        $(this).attr('_changed', true);
    });
    if (slug_field) {
        var slug_source = $('#id_' + slug_field.attr('slug-source'));
        slug_source.on('keyup change', function() {
            if (slug_field && !slug_field.attr('_changed')) {
                slug_field.val(slugify($(this).val(), 50));
            }
        })
    }

    // Bulk edit nullification
    $('input:checkbox[name=_nullify]').click(function (event) {
        $('#id_' + this.value).toggle('disabled');
    });

    // Set formaction and submit using a link
    $('a.formaction').click(function (event) {
        event.preventDefault();
        var form = $(this).closest('form');
        form.attr('action', $(this).attr('href'));
        form.submit();
    });

    // API select widget
    $('select[filter-for]').change(function() {

        // Resolve child field by ID specified in parent
        var child_name = $(this).attr('filter-for');
        var child_field = $('#id_' + child_name);
        var child_selected = child_field.val();

        // Wipe out any existing options within the child field and create a default option
        child_field.empty();
        child_field.append($("<option></option>").attr("value", "").text("---------"));

        if ($(this).val() || $(this).attr('nullable') == 'true') {
            var api_url = child_field.attr('api-url');
            var disabled_indicator = child_field.attr('disabled-indicator');
            var initial_value = child_field.attr('initial');
            var display_field = child_field.attr('display-field') || 'name';

            // Determine the filter fields needed to make an API call
            var filter_regex = /\{\{([a-z_]+)\}\}/g;
            var match;
            while (match = filter_regex.exec(api_url)) {
                var filter_field = $('#id_' + match[1]);
                if (filter_field.val()) {
                    api_url = api_url.replace(match[0], filter_field.val());
                } else if ($(this).attr('nullable') == 'true') {
                    api_url = api_url.replace(match[0], '0');
                }
            }

            // If all URL variables have been replaced, make the API call
            if (api_url.search('{{') < 0) {
                console.log(child_name + ": Fetching " + api_url);
                $.ajax({
                    url: api_url,
                    dataType: 'json',
                    success: function (response, status) {
                        $.each(response, function (index, choice) {
                            var option = $("<option></option>").attr("value", choice.id).text(choice[display_field]);
                            if (disabled_indicator && choice[disabled_indicator] && choice.id != initial_value) {
                                option.attr("disabled", "disabled");
                            } else if (choice.id == child_selected) {
                                option.attr("selected", "selected");
                            }
                            child_field.append(option);
                        });
                    }
                });
            }

        }

        // Trigger change event in case the child field is the parent of another field
        child_field.change();

    });
});
