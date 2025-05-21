// Version: 2.0 - Cache buster
(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('Document ready');
        
        var $tipoField = $('#id_tipo');
        var $form = $tipoField.closest('form');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // Debug element finding
        console.log('Form found:', $form.length > 0);
        console.log('All fieldsets:', $('fieldset').length);
        
        // Log the complete HTML structure
        console.log('Complete form HTML:', $form.html());
        
        // Log each fieldset and its classes
        $('fieldset').each(function(index) {
            console.log('Fieldset ' + index + ':');
            console.log('- Classes:', $(this).attr('class'));
            console.log('- Legend:', $(this).find('legend').text());
            console.log('- Fields:', $(this).find('.form-row').length);
            console.log('- HTML:', $(this).html());
        });

        // Add explicit CSS to ensure visibility changes work
        $('head').append(`
            <style>
                fieldset.animal-type-fields { 
                    display: none !important; 
                    visibility: hidden !important;
                }
                fieldset.animal-type-fields.show { 
                    display: block !important;
                    visibility: visible !important;
                }
            </style>
        `);

        function showHideFields() {
            console.log('showHideFields called');
            var selectedType = $tipoField.val();
            console.log('Selected type:', selectedType);
            
            // Find all type-specific fieldsets
            var $cachorroFields = $('fieldset:contains("Informações do Cachorro")');
            var $gatoFields = $('fieldset:contains("Informações do Gato")');
            
            console.log('Found cachorro fieldset:', $cachorroFields.length);
            console.log('Found gato fieldset:', $gatoFields.length);
            
            // Add the animal-type-fields class if not already present
            $cachorroFields.addClass('animal-type-fields');
            $gatoFields.addClass('animal-type-fields');
            
            // Remove show class from all
            $('.animal-type-fields').removeClass('show');
            
            if (selectedType) {
                // Add management fields for photos regardless of type
                addManagementFields('fotoanimal');
                
                // Show relevant fields based on type
                if (selectedType === 'CACHORRO') {
                    console.log('Showing cachorro fields');
                    $cachorroFields.addClass('show');
                    addManagementFields('cachorro');
                } else if (selectedType === 'GATO') {
                    console.log('Showing gato fields');
                    $gatoFields.addClass('show');
                    addManagementFields('gato');
                }
            }
        }

        function addManagementFields(prefix) {
            if (!$('input[name="' + prefix + '-TOTAL_FORMS"]').length) {
                $form.append('<input type="hidden" name="' + prefix + '-TOTAL_FORMS" value="1">');
                $form.append('<input type="hidden" name="' + prefix + '-INITIAL_FORMS" value="0">');
                $form.append('<input type="hidden" name="' + prefix + '-MIN_NUM_FORMS" value="0">');
                $form.append('<input type="hidden" name="' + prefix + '-MAX_NUM_FORMS" value="1">');
            }
        }

        // When tipo changes, load the specific fields via AJAX
        $tipoField.on('change', function() {
            var selectedType = $(this).val();
            console.log('Type changed to:', selectedType);
            
            // Save current form values
            var formData = new FormData($form[0]);
            
            // Add the tipo parameter to the current URL without reloading
            var url = new URL(window.location.href);
            url.searchParams.set('tipo', selectedType);
            window.history.pushState({}, '', url.toString());
            
            // Make AJAX request to get the new form
            $.ajax({
                url: window.location.href,
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function(response) {
                    // Create a temporary div to hold the response
                    var $temp = $('<div>').html(response);
                    
                    // Find the fieldsets in the response
                    var $newFieldsets = $temp.find('fieldset');
                    
                    // Replace only the type-specific fieldset
                    var typeFieldsetIndex = selectedType === 'CACHORRO' ? 1 : 1;
                    var $currentFieldsets = $form.find('fieldset');
                    
                    if ($currentFieldsets.length > typeFieldsetIndex) {
                        // If the type-specific fieldset exists, replace it
                        $currentFieldsets.eq(typeFieldsetIndex).replaceWith(
                            $newFieldsets.eq(typeFieldsetIndex)
                        );
                    } else {
                        // If it doesn't exist, insert it after the first fieldset
                        $currentFieldsets.eq(0).after($newFieldsets.eq(typeFieldsetIndex));
                    }
                    
                    // Restore form values
                    var $inputs = $form.find('input, select, textarea').not('[type="hidden"]');
                    $inputs.each(function() {
                        var name = $(this).attr('name');
                        if (name && formData.has(name)) {
                            $(this).val(formData.get(name));
                        }
                    });
                    
                    // Reinitialize Django admin widgets if needed
                    if (typeof initializeWidgets === 'function') {
                        initializeWidgets();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error loading fields:', error);
                }
            });
        });

        // Initial setup when page loads
        console.log('Initial setup');
        showHideFields();

        // If editing an existing animal, disable the tipo field
        if ($form.data('object-id')) {
            $tipoField.prop('disabled', true);
        }
    });
})(window.django.jQuery); 