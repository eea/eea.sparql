$(document).ready(function() {

    function setDataGridWidgetTRLabels() {
    $('#datagridwidget-tbody-arg_spec')
        .find('.eea-sparql-datagridwidget-tr-label').remove();
    $.each(
        $('#datagridwidget-tbody-arg_spec').find('tr'),
        function(idx, tr) {
            var tr_label = $('<td>')
                            .addClass('eea-sparql-datagridwidget-tr-label')
                            .text('Argument #' + (idx + 1).toString());
            $(tr).prepend(tr_label);
        }
    );
  }

  function setColumnClasses() {
    $('[name="arg_spec.name:records"]')
        .closest('td').addClass('datagridwidget-column-1');
    $('[name="arg_spec.query:records"]')
        .closest('td').addClass('datagridwidget-column-2');
    setDataGridWidgetTRLabels();
    $(document).trigger('eea-wizard-changed');

  }

  $('#archetypes-fieldname-arg_spec .datagridwidget-add-button').text('Add new argument');
  $('#archetypes-fieldname-arg_spec .datagridwidget-add-button').addClass('datagridwidget-sparql-add-button');
  $('#archetypes-fieldname-arg_spec .datagridwidget-sparql-add-button').removeClass('datagridwidget-add-button');

  $("#archetypes-fieldname-arg_spec")
    .delegate('.datagridwidget-manipulator img', 'click', setColumnClasses);
  $("#archetypes-fieldname-arg_spec")
    .delegate('.datagridwidget-sparql-add-button', 'click', setColumnClasses);
  setDataGridWidgetTRLabels();

});

if (window.Browser) {
    window.Browser.onUploadComplete = function(){
        // don't reload the page after uploading file
    };
}

