$.alt_shift = function(key, callback, args) {
    $(document).keydown(function(e) {
        if(!args) args=[]; // IE barks when args is null
        if((e.keyCode == key.charCodeAt(0) || e.keyCode == key) && e.altKey && e.shiftKey) {
            callback.apply(this, args);
            return false;
        }
    });
};

//Edit the current object
$.alt_shift('69', function() {
  $('.oe_form_button_edit').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});


//Save the current object
$.alt_shift('83', function() {
  $('.oe_form_button_save').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});

//Create new object
$.alt_shift('67', function() {
  $('.oe_form_button_create').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});

//Cancel
$.alt_shift('68', function() {
  $('.oe_form_button_cancel').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});


