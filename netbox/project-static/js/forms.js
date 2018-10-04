$(document).ready(function() {

    // "Toggle" checkbox for object lists (PK column)
    $('input:checkbox.toggle').click(function() {
        $(this).closest('table').find('input:checkbox[name=pk]').prop('checked', $(this).prop('checked'));

        // Show the "select all" box if present
        if ($(this).is(':checked')) {
            $('#select_all_box').removeClass('hidden');
        } else {
            $('#select_all').prop('checked', false);
        }
    });

    // Uncheck the "toggle" and "select all" checkboxes if an item is unchecked
    $('input:checkbox[name=pk]').click(function (event) {
        if (!$(this).attr('checked')) {
            $('input:checkbox.toggle, #select_all').prop('checked', false);
        }
    });

    // Enable hidden buttons when "select all" is checked
    $('#select_all').click(function() {
        if ($(this).is(':checked')) {
            $('#select_all_box').find('button').prop('disabled', '');
        } else {
            $('#select_all_box').find('button').prop('disabled', 'disabled');
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

    // Bulk edit nullification
    $('input:checkbox[name=_nullify]').click(function() {
        $('#id_' + this.value).toggle('disabled');
    });

    // Set formaction and submit using a link
    $('a.formaction').click(function(event) {
        event.preventDefault();
        var form = $(this).closest('form');
        form.attr('action', $(this).attr('href'));
        form.submit();
    });

    // API select widget
    $('select[filter-for]').change(function() {

        // Resolve child field by ID specified in parent
        var child_names = $(this).attr('filter-for');
        var parent = this;

        // allow more than one child
        $.each(child_names.split(" "), function(_, child_name){

            var child_field = $('#id_' + child_name);
            var child_selected = child_field.val();

            // Wipe out any existing options within the child field and create a default option
            child_field.empty();
            if (!child_field.attr('multiple')) {
                child_field.append($("<option></option>").attr("value", "").text("---------"));
            }

            if ($(parent).val() || $(parent).attr('nullable') == 'true') {
                var api_url = child_field.attr('api-url') + '&limit=0&brief=1';
                var disabled_indicator = child_field.attr('disabled-indicator');
                var initial_value = child_field.attr('initial');
                var display_field = child_field.attr('display-field') || 'name';

                // Determine the filter fields needed to make an API call
                var filter_regex = /\{\{([a-z_]+)\}\}/g;
                var match;
                var rendered_url = api_url;
                while (match = filter_regex.exec(api_url)) {
                    var filter_field = $('#id_' + match[1]);
                    if (filter_field.val()) {
                        rendered_url = rendered_url.replace(match[0], filter_field.val());
                    } else if (filter_field.attr('nullable') == 'true') {
                        rendered_url = rendered_url.replace(match[0], '0');
                    }
                }

                // If all URL variables have been replaced, make the API call
                if (rendered_url.search('{{') < 0) {
                    console.log(child_name + ": Fetching " + rendered_url);
                    $.ajax({
                        url: rendered_url,
                        dataType: 'json',
                        success: function(response, status) {
                            $.each(response.results, function(index, choice) {
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

    // Auto-complete tags
    function split_tags(val) {
      return val.split(/,\s*/);
    }
    $("#id_tags")
      .on("keydown", function(event) {
        if (event.keyCode === $.ui.keyCode.TAB &&
            $(this).autocomplete("instance").menu.active) {
          event.preventDefault();
        }
      })
      .autocomplete({
        source: function(request, response) {
            $.ajax({
                type: 'GET',
                url: netbox_api_path + 'extras/tags/',
                data: 'q=' + split_tags(request.term).pop(),
                success: function(data) {
                    var choices = [];
                    $.each(data.results, function (index, choice) {
                        choices.push(choice.name);
                    });
                    response(choices);
                }
            });
        },
        search: function() {
          // Need 3 or more characters to begin searching
          var term = split_tags(this.value).pop();
          if (term.length < 3) {
            return false;
          }
        },
        focus: function() {
          // prevent value inserted on focus
          return false;
        },
        select: function(event, ui) {
          var terms = split_tags(this.value);
          // remove the current input
          terms.pop();
          // add the selected item
          terms.push(ui.item.value);
          // add placeholder to get the comma-and-space at the end
          terms.push("");
          this.value = terms.join(", ");
          return false;
        }
      });
});
