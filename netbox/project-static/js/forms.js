$(document).ready(function() {

    // Pagination
    $('select#per_page').change(function() {
        this.form.submit();
    });

    // "Toggle" checkbox for object lists (PK column)
    $('input:checkbox.toggle').click(function() {
        $(this).closest('table').find('input:checkbox[name=pk]:visible').prop('checked', $(this).prop('checked'));

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
    if (slug_field) {
        var slug_source = $('#id_' + slug_field.attr('slug-source'));
        var slug_length = slug_field.attr('maxlength');
        if (slug_field.val()) {
            slug_field.attr('_changed', true);
        }
        slug_field.change(function() {
            $(this).attr('_changed', true);
        });
        slug_source.on('keyup change', function() {
            if (slug_field && !slug_field.attr('_changed')) {
                slug_field.val(slugify($(this).val(), (slug_length ? slug_length : 50)));
            }
        });
        $('button.reslugify').click(function() {
            slug_field.val(slugify(slug_source.val(), (slug_length ? slug_length : 50)));
        });
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

    // Parse URLs which may contain variable references to other field values
    function parseURL(url) {
        var filter_regex = /\{\{([a-z_]+)\}\}/g;
        var match;
        var rendered_url = url;
        var filter_field;
        while (match = filter_regex.exec(url)) {
            filter_field = $('#id_' + match[1]);
            var custom_attr = $('option:selected', filter_field).attr('api-value');
            if (custom_attr) {
                rendered_url = rendered_url.replace(match[0], custom_attr);
            } else if (filter_field.val()) {
                rendered_url = rendered_url.replace(match[0], filter_field.val());
            } else if (filter_field.attr('data-null-option')) {
                rendered_url = rendered_url.replace(match[0], 'null');
            }
        }
        return rendered_url
    }

    // Assign color picker selection classes
    function colorPickerClassCopy(data, container) {
        if (data.element) {
            // Swap the style
            $(container).attr('style', $(data.element).attr("style"));
        }
        return data.text;
    }

    // Speed selector
    $("a.set_speed").click(function(e) {
        e.preventDefault();
        $("#id_" + $(this).attr("target")).val($(this).attr("data"));
    });

    // Color Picker
    $('.netbox-select2-color-picker').select2({
        allowClear: true,
        placeholder: "---------",
        theme: "bootstrap",
        templateResult: colorPickerClassCopy,
        templateSelection: colorPickerClassCopy,
        width: "off"
    });

    // Static choice selection
    $('.netbox-select2-static').select2({
        allowClear: true,
        placeholder: "---------",
        theme: "bootstrap",
        width: "off"
    });

    // API backed selection
    // Includes live search and chained fields
    // The `multiple` setting may be controlled via a data-* attribute
    $('.netbox-select2-api').select2({
        allowClear: true,
        placeholder: "---------",
        theme: "bootstrap",
        width: "off",
        ajax: {
            delay: 500,

            url: function(params) {
                var element = this[0];
                var url = parseURL(element.getAttribute("data-url"));

                if (url.includes("{{")) {
                    // URL is not fully rendered yet, abort the request
                    return false;
                }
                return url;
            },

            data: function(params) {
                var element = this[0];
                // Paging. Note that `params.page` indexes at 1
                var offset = (params.page - 1) * 50 || 0;
                // Base query params
                var parameters = {
                    q: params.term,
                    limit: 50,
                    offset: offset,
                };

                // Attach any extra query parameters
                $.each(element.attributes, function(index, attr){
                    if (attr.name.includes("data-query-param-")){
                        var param_name = attr.name.split("data-query-param-")[1];

                        $.each($.parseJSON(attr.value), function(index, value) {
                            // Referencing the value of another form field
                            if (value.startsWith('$')) {
                                let ref_field = $('#id_' + value.slice(1));
                                if (ref_field.val() && ref_field.is(":visible")) {
                                    value = ref_field.val();
                                } else if (ref_field.attr("required") && ref_field.attr("data-null-option")) {
                                    value = "null";
                                } else {
                                    return true;  // Skip if ref_field has no value
                                }
                            }
                            if (param_name in parameters) {
                                if (Array.isArray(parameters[param_name])) {
                                    parameters[param_name].push(value);
                                } else {
                                    parameters[param_name] = [parameters[param_name], value];
                                }
                            } else {
                                parameters[param_name] = value;
                            }
                        });
                    }
                });

                // This will handle params with multiple values (i.e. for list filter forms)
                return $.param(parameters, true);
            },

            processResults: function (data) {
                var element = this.$element[0];
                $(element).children('option').attr('disabled', false);
                var results = data.results;

                results = results.reduce((results,record,idx) => {
                    record.text = record[element.getAttribute('display-field')] || record.name;
                    if (record._depth) {
                        // Annotate hierarchical depth for MPTT objects
                        record.text = '--'.repeat(record._depth) + ' ' + record.text;
                    }
                    record.id = record[element.getAttribute('value-field')] || record.id;
                    if(element.getAttribute('disabled-indicator') && record[element.getAttribute('disabled-indicator')]) {
                        // The disabled-indicator equated to true, so we disable this option
                        record.disabled = true;
                    }

                    if( record.group !== undefined && record.group !== null && record.site !== undefined && record.site !== null ) {
                        results[record.site.name + ":" + record.group.name] = results[record.site.name + ":" + record.group.name] || { text: record.site.name + " / " + record.group.name, children: [] };
                        results[record.site.name + ":" + record.group.name].children.push(record);
                    }
                    else if( record.group !== undefined && record.group !== null ) {
                        results[record.group.name] = results[record.group.name] || { text: record.group.name, children: [] };
                        results[record.group.name].children.push(record);
                    }
                    else if( record.site !== undefined && record.site !== null ) {
                        results[record.site.name] = results[record.site.name] || { text: record.site.name, children: [] };
                        results[record.site.name].children.push(record);
                    }
                    else if ( (record.group !== undefined || record.group == null) && (record.site !== undefined || record.site === null) ) {
                        results['global'] = results['global'] || { text: 'Global', children: [] };
                        results['global'].children.push(record);
                    }
                    else {
                        results[idx] = record
                    }

                    return results;
                },Object.create(null));

                results = Object.values(results);

                // Handle the null option, but only add it once
                if (element.getAttribute('data-null-option') && data.previous === null) {
                    results.unshift({
                        id: 'null',
                        text: element.getAttribute('data-null-option')
                    });
                }

                // Check if there are more results to page
                var page = data.next !== null;
                return {
                    results: results,
                    pagination: {
                        more: page
                    }
                };
            }
        }
    });

    // Flatpickr selectors
    $('.date-picker').flatpickr({
        allowInput: true
    });
    $('.datetime-picker').flatpickr({
        allowInput: true,
        enableSeconds: true,
        enableTime: true,
        time_24hr: true
    });
    $('.time-picker').flatpickr({
        allowInput: true,
        enableSeconds: true,
        enableTime: true,
        noCalendar: true,
        time_24hr: true
    });

    // API backed tags
    var tags = $('#id_tags.tagfield');
    if (tags.length > 0 && tags.val().length > 0){
        tags = $('#id_tags.tagfield').val().split(/,\s*/);
    } else {
        tags = [];
    }
    tag_objs = $.map(tags, function (tag) {
        return {
            id: tag,
            text: tag,
            selected: true
        }
    });
    // Replace the django issued text input with a select element
    $('#id_tags.tagfield').replaceWith('<select name="tags" id="id_tags" class="form-control tagfield"></select>');
    $('#id_tags.tagfield').select2({
        tags: true,
        data: tag_objs,
        multiple: true,
        allowClear: true,
        placeholder: "Tags",
        theme: "bootstrap",
        width: "off",
        ajax: {
            delay: 250,
            url: netbox_api_path + "extras/tags/",

            data: function(params) {
                // Paging. Note that `params.page` indexes at 1
                var offset = (params.page - 1) * 50 || 0;
                var parameters = {
                    q: params.term,
                    brief: 1,
                    limit: 50,
                    offset: offset,
                };
                return parameters;
            },

            processResults: function (data) {
                var results = $.map(data.results, function (obj) {
                    // If tag contains space add double quotes
                    if (/\s/.test(obj.name))
                        obj.name = '"' + obj.name + '"'

                    return {
                        id: obj.name,
                        text: obj.name
                    }
                });

                // Check if there are more results to page
                var page = data.next !== null;
                return {
                    results: results,
                    pagination: {
                        more: page
                    }
                };
            }
        }
    });
    $('#id_tags.tagfield').closest('form').submit(function(event){
        // django-taggit can only accept a single comma seperated string value
        var value = $('#id_tags.tagfield').val();
        if (value.length > 0){
            var final_tags = value.join(', ');
            $('#id_tags.tagfield').val(null).trigger('change');
            var option = new Option(final_tags, final_tags, true, true);
            $('#id_tags.tagfield').append(option).trigger('change');
        }
    });

    if( $('select#id_mode').length > 0 ) {
        $('select#id_mode').on('change', function () {
            if ($(this).val() == '') {
                $('select#id_untagged_vlan').val();
                $('select#id_untagged_vlan').trigger('change');
                $('select#id_tagged_vlans').val([]);
                $('select#id_tagged_vlans').trigger('change');
                $('select#id_untagged_vlan').parent().parent().hide();
                $('select#id_tagged_vlans').parent().parent().hide();
            }
            else if ($(this).val() == 'access') {
                $('select#id_tagged_vlans').val([]);
                $('select#id_tagged_vlans').trigger('change');
                $('select#id_untagged_vlan').parent().parent().show();
                $('select#id_tagged_vlans').parent().parent().hide();
            }
            else if ($(this).val() == 'tagged') {
                $('select#id_untagged_vlan').parent().parent().show();
                $('select#id_tagged_vlans').parent().parent().show();
            }
            else if ($(this).val() == 'tagged-all') {
                $('select#id_tagged_vlans').val([]);
                $('select#id_tagged_vlans').trigger('change');
                $('select#id_untagged_vlan').parent().parent().show();
                $('select#id_tagged_vlans').parent().parent().hide();
            }
        });
        $('select#id_mode').trigger('change');
    }

    // Scroll up an offset equal to the first nav element if a hash is present
    // Cannot use '#navbar' because it is not always visible, like in small windows
    function headerOffsetScroll() {
        if (window.location.hash) {
            // Short wait needed to allow the page to scroll to the element
            setTimeout(function() {
                window.scrollBy(0, -$('nav').height())
            }, 10);
        }
    }

    // Account for the header height when hash-scrolling
    window.addEventListener('load', headerOffsetScroll);
    window.addEventListener('hashchange', headerOffsetScroll);

    // Offset between the preview window and the window edges
    const IMAGE_PREVIEW_OFFSET_X = 20;
    const IMAGE_PREVIEW_OFFSET_Y = 10;

    // Preview an image attachment when the link is hovered over
    $('a.image-preview').on('mouseover', function(e) {
        // Twice the offset to account for all sides of the picture
        var maxWidth = window.innerWidth - (e.clientX + (IMAGE_PREVIEW_OFFSET_X * 2));
        var maxHeight = window.innerHeight - (e.clientY + (IMAGE_PREVIEW_OFFSET_Y * 2));
        var img = $('<img>').attr('id', 'image-preview-window').css({
            display: 'none',
            position: 'absolute',
            maxWidth: maxWidth + 'px',
            maxHeight: maxHeight + 'px',
            left: e.pageX + IMAGE_PREVIEW_OFFSET_X + 'px',
            top: e.pageY + IMAGE_PREVIEW_OFFSET_Y + 'px',
            boxShadow: '0 0px 12px 3px rgba(0, 0, 0, 0.4)',
        });

        // Remove any existing preview windows and add the current one
        $('#image-preview-window').remove();
        $('body').append(img);

        // Once loaded, show the preview if the image is indeed an image
        img.on('load', function(e) {
            if (e.target.complete && e.target.naturalWidth) {
                $('#image-preview-window').fadeIn('fast');
            }
        });

        // Begin loading
        img.attr('src', e.target.href);
    });

    // Fade the image out; it will be deleted when another one is previewed
    $('a.image-preview').on('mouseout', function() {
        $('#image-preview-window').fadeOut('fast');
    });

    // Rearrange options within a <select> list
    $('#move-option-up').bind('click', function() {
        var select_id = '#' + $(this).attr('data-target');
        $(select_id + ' option:selected').each(function () {
            var newPos = $(select_id + ' option').index(this) - 1;
            if (newPos > -1) {
                $(select_id + ' option').eq(newPos).before("<option value='" + $(this).val() + "' selected='selected'>" + $(this).text() + "</option>");
                $(this).remove();
            }
        });
    });
    $('#move-option-down').bind('click', function() {
        var select_id = '#' + $(this).attr('data-target');
        var countOptions = $(select_id + ' option').length;
        var countSelectedOptions = $(select_id + ' option:selected').length;
        $(select_id + ' option:selected').each(function () {
            var newPos = $(select_id + ' option').index(this) + countSelectedOptions;
            if (newPos < countOptions) {
                $(select_id + ' option').eq(newPos).after("<option value='" + $(this).val() + "' selected='selected'>" + $(this).text() + "</option>");
                $(this).remove();
            }
        });
    });
    $('#select-all-options').bind('click', function() {
        var select_id = '#' + $(this).attr('data-target');
        $(select_id + ' option').prop('selected',true);
    });

});
