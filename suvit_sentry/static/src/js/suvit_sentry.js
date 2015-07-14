openerp.Listee = function(instance, local) {

  $('.show_details').live('click', (function() {
    $('.hide_details').show();
    $('.error_details').show();
    $(this).hide();
  })
  )

  $('.hide_details').live('click', (function() {
    $('.show_details').show();
    $('.error_details').hide();
    $(this).hide();
  })
  )
};