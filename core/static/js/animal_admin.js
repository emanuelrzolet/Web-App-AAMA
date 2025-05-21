// Version: 2.0 - Cache buster
(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('Document ready');
        
        var $tipoField = $('#id_tipo');
        var $form = $tipoField.closest('form');
        
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

        // When tipo changes, reload the page with the new type
        $tipoField.on('change', function() {
            var selectedType = $(this).val();
            console.log('Type changed to:', selectedType);
            
            // Get current URL
            var url = new URL(window.location.href);
            
            // Update or add the tipo parameter
            url.searchParams.set('tipo', selectedType);
            
            // Redirect to the new URL
            window.location.href = url.toString();
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