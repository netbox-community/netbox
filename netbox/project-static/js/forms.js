$(document).ready(function() {

    // "Select all" checkbox in a table header
    $('th input:checkbox[name=_all]').click(function (event) {
        $(this).parents('table').find('td input:checkbox').prop('checked', $(this).prop('checked'));
    });
    // Uncheck the "select all" checkbox if an item is unchecked
    $('input:checkbox[name=pk]').click(function (event) {
        if (!$(this).attr('checked')) {
            $(this).parents('table').find('input:checkbox[name=_all]').prop('checked', false);
        }
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

    // API select widget
    $('select[filter-for]').change(function () {

        // Resolve child field by ID specified in parent
        var child_name = $(this).attr('filter-for');
        var child_field = $('#id_' + child_name);

        // Wipe out any existing options within the child field
        child_field.empty();
        child_field.append($("<option></option>").attr("value", "").text(""));

        if ($(this).val()) {

            var api_url = child_field.attr('api-url');
            var disabled_indicator = child_field.attr('disabled-indicator');
            var initial_value = child_field.attr('initial');
            var display_field = child_field.attr('display-field') || 'name';

            // Gather the values of all other filter fields for this child
            $("select[filter-for='" + child_name + "']").each(function() {
                var filter_field = $(this);
                if (filter_field.val()) {
                    api_url = api_url.replace('{{' + filter_field.attr('name') + '}}', filter_field.val());
                } else {
                    // Not all filters have been selected yet
                    return false;
                }

            });

            // If all URL variables have been replaced, make the API call
            if (api_url.search('{{') < 0) {
                $.ajax({
                    url: api_url,
                    dataType: 'json',
                    success: function (response, status) {
                        $.each(response, function (index, choice) {
                            var option = $("<option></option>").attr("value", choice.id).text(choice[display_field]);
                            if (disabled_indicator && choice[disabled_indicator] && choice.id != initial_value) {
                                option.attr("disabled", "disabled")
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
