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
// alt + shift + e
$.alt_shift('69', function() {
  $('.oe_form_button_edit').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});

//Save the current object
// alt + shift + s
$.alt_shift('83', function() {
  $('.oe_form_button_save').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});

//Delete the current object
$.alt_shift('81', function() {
  $('.oe_dropdown_menu li a').each(function() {
    if($(this).parents('div:hidden').length == 0 && ($(this).attr('data-index') === '4' && this.text.trim() === 'Удалить')){
      $(this).trigger('click');
    }
  });
});

//Create new object
// alt + shift + c
$.alt_shift('67', function() {
  $('.oe_form_button_create').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});

//Cancel
// alt + shift + d
$.alt_shift('68', function() {
  $('.oe_form_button_cancel').each(function() {
    if($(this).parents('div:hidden').length == 0){
      $(this).trigger('click');
    }
  });
});

  //If 'autoFocus' set to true the first item will automatically be focused when the menu is shown
  //It allows to focus on the first item in dropdown menu and press ENTER to choose it  
  openerp.suvit_hotkeys = function(instance, local) {
    instance.web.form.FieldMany2One.include({
      get_search_result: function(search_val) {
        var self = this;
        res = this._super(search_val);
        var autoFocus = $(".ui-autocomplete-input").autocomplete("option", "autoFocus", true);
        return res;
      },
    });
  };