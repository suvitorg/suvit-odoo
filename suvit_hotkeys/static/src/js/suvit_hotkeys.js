openerp.suvit_hotkeys = function(instance, local) {

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
  //Alt + Shift + E
  $.alt_shift('69', function() {
    $('.oe_form_button_edit').each(function() {
      if($(this).parents('div:hidden').length == 0){
        $(this).trigger('click');
      }
    });
  });

  //Save the current object
  //Alt + Shift + S
  $.alt_shift('83', function() {
    $('.oe_form_button_save').each(function() {
      if($(this).parents('div:hidden').length == 0){
        $(this).trigger('click');
      }
    });
  });

  //Delete the current object
  //Alt + Shift + Q
  $.alt_shift('81', function() {
    $('.oe_dropdown_menu li a[data-section=other]').each(function() {
      if($(this).parents('div:hidden').length == 0 && this.text.trim() === 'Удалить'){
        $(this).trigger('click');
      }
    });
  });

  //Create new object
  //Alt + Shift + C
  $.alt_shift('67', function() {
    $('.oe_form_button_create').each(function() {
      if($(this).parents('div:hidden').length == 0){
        $(this).trigger('click');
      }
    });
  });

  //Cancel
  //Alt + Shift + D
  $.alt_shift('68', function() {
    $('.oe_form_button_cancel').each(function() {
      if($(this).parents('div:hidden').length == 0){
        $(this).trigger('click');
      }
    });
  });
  
  instance.web.Menu.include({
    on_menu_click: function(ev) {  
      //Ctrl + left button mouseClick on menu (top or secondary menu) => opens the clicked menu in a new window
      if (!ev.ctrlKey || !ev.currentTarget.dataset || !ev.currentTarget.dataset.menu || !ev.currentTarget.dataset.actionId)
        return this._super(ev);
      
      ev.preventDefault();
      ev.stopPropagation();

      localStorage.setItem('last_menu_id', ev.currentTarget.dataset.menu);
      var url = ev.currentTarget.hash;
      window.open(url, '_blank');
    },
  });
  
  instance.web.ListView.List.include({
    row_clicked: function (e, view) {
      //Ctrl + left button mouseClick on ListView item => opens the clicked item in a new window
      if(!e.ctrlKey)
        return this._super(e, view)
      
      e.preventDefault();
      e.stopPropagation();

      var view = view || this.dataset.index === null || this.dataset.index === undefined ? 'form' : 'form';
      var state = {
        'id': this.dataset.ids[this.dataset.index],
        'view_type': view,
        'model': this.dataset.model,
      };

      var menu_id = this.view.ViewManager.action && this.view.ViewManager.action.menu_id ? this.view.ViewManager.action.menu_id : false;
      if (menu_id)
        state['menu_id'] = menu_id;
      var action_id = this.view.ViewManager.action && this.view.ViewManager.action.id ? this.view.ViewManager.action.id : false;
      if (action_id)
        state['action'] = action_id;

      localStorage.setItem('force_ctrl_click_open', 'force_open');
      var url = '#' + $.param(state);
      window.open(url, '_blank');
    },
  });
  
  instance.web.form.FieldMany2One.include({
    get_search_result: function(search_val) {
      var self = this;
      res = this._super(search_val);
      //If 'autoFocus' set to true the first item will automatically be focused when the menu is shown
      //It allows to focus on the first item in dropdown menu and press ENTER to choose it
      var autoFocus = $(".ui-autocomplete-input").autocomplete("option", "autoFocus", true);
      return res;
    },
  });
  
};