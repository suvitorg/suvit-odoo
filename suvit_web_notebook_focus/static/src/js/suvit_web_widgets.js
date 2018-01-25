openerp.suvit_web_notebook_focus = function(instance, local) {

  instance.web.form.FormRenderingEngine.include({
    get_key: function() {
      var id = this.view ? this.view.view_id || this.view.fields_view.view_id : false;
      if (id) {
        var key = "selected_tabs_"+id+'_'+openerp.session.uid;
        return key;
      }
    },
    save_tab_id: function(tab_id) {
      var key = this.get_key();
      if (!key) return;
      localStorage[key] = tab_id;
    },
    restore_tab_id: function() {
      var key = this.get_key();
      if (!key) return;
      return localStorage.getItem(key);
    },
    process_notebook: function($notebook) {
      var selected;
      var pages = $notebook.find('> page');
      var action = this.view.ViewManager.action;
      var af_name = (action && action.context.autofocus) || this.restore_tab_id();

      pages.each(function(i) {
          var $page = $(this);
          var page_attrs = $page.getAttributes();
          if (page_attrs.autofocus || (page_attrs.name == af_name) || (page_attrs.string == af_name))
            selected = i;
      });
      var self = this;
      var note = this._super($notebook);
      
      note.mousedown(function(ev){
        //tab name - ev.toElement.attributes.name && ev.toElement.attributes.name.value;
        //tab string - ev.toElement.attributes.string && ev.toElement.attributes.string.value
        var tab_name = ev.toElement.attributes.name && ev.toElement.attributes.name.value;
        if(tab_name) {
          self.save_tab_id(tab_name);
        }
      });
      
      if (!selected)
        return note;
      self.selected_name = note;
      note.tabs('select', selected);
      return note;
    },
    process_form: function($form) {
      var self = this;
      var res = this._super($form);
      if(!this.selected_name)
        return res;
      var ggg = this.selected_name;
      var parents = ggg.parents('div.oe_notebook_page');
      parents.each(function(i, val) {
        var tab_id = $("a[href=#"+val.id+"]", self.$form);
        if(tab_id && tab_id.length) {
          var parent_tab = tab_id.parent().parent().parent();
          parent_tab.tabs('select', val.id);
        }
      });
    },
  });

};
