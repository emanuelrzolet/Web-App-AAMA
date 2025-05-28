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

        // Initialize color field
        var $colorField = $('#id_cor');
        var currentValue = $colorField.val();
        
        // If there's a custom color value, add it to the options
        if (currentValue && !$colorField.find('option[value="' + currentValue + '"]').length) {
            $colorField.append(new Option(currentValue, currentValue, true, true));
        }
        
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
                .field-add_cor,
                .field-add_raca_cachorro,
                .field-add_raca_gato {
                    padding-top: 25px !important;
                }
            </style>
        `);

        // Global function for the color dialog
        window.showColorDialog = function() {
            var newColor = prompt('Digite a nova cor:');
            if (newColor) {
                newColor = newColor.toUpperCase();
                // Add the new color as an option if it doesn't exist
                if (!$colorField.find('option[value="' + newColor + '"]').length) {
                    $colorField.append(new Option(newColor, newColor));
                }
                $colorField.val(newColor);
            }
            return false;
        };

        // Global function for the breed dialog
        window.showBreedDialog = function(tipo) {
            var newBreed = prompt('Digite a nova raça:');
            if (newBreed) {
                // Create the breed via AJAX
                $.ajax({
                    url: '/add_raca_' + tipo + '/',
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    data: {
                        'nome': newBreed
                    },
                    success: function(response) {
                        if (response.success) {
                            var $breedField = $('#id_raca_' + tipo);
                            // Check if option already exists
                            if (!$breedField.find('option[value="' + response.id + '"]').length) {
                                var option = new Option(response.nome, response.id);
                                $breedField.append(option);
                            }
                            $breedField.val(response.id).trigger('change');
                        } else {
                            alert('Erro ao adicionar raça: ' + response.error);
                        }
                    },
                    error: function(xhr, status, error) {
                        var errorMessage;
                        try {
                            errorMessage = JSON.parse(xhr.responseText).error;
                        } catch (e) {
                            errorMessage = error;
                        }
                        alert('Erro ao adicionar raça: ' + errorMessage);
                    }
                });
            }
            return false;
        };

        // Handle breed popup windows
        function handlePopupResponse(win, newId, newRepr) {
            if (newId !== null) {
                var name = win.name;
                if (name.startsWith('add_raca_')) {
                    var selectField = $('#id_' + name.substring(4));
                    var option = new Option(newRepr, newId);
                    selectField.append(option);
                    selectField.val(newId);
                }
            }
        }

        // Add the popup callback to the window
        window.dismissAddAnotherPopup = function(win, newId, newRepr) {
            handlePopupResponse(win, newId, newRepr);
            win.close();
        };

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
            var url = new URL(window.location.href);
            url.searchParams.set('tipo', selectedType);
            window.location.href = url.toString(); // Recarrega a página com o tipo selecionado
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