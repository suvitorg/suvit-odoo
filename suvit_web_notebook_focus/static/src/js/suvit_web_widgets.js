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
          if (page_attrs.autofocus || (af_name && page_attrs.name == af_name) || (af_name && page_attrs.string == af_name))
            selected = i;
      });
      var self = this;
      var note = this._super($notebook);
      
      note.mousedown(function(ev){
        var tab_name = $.trim(ev.toElement.text);
        self.save_tab_id(tab_name);
      });
      
      var tab_id;
      if(self.parent_tab_id)
        tab_id = $("a[href=#"+self.parent_tab_id+"]", this.$form);
      if(tab_id && tab_id.length) {
        var fff = tab_id.parent().parent();
        selected = self.parent_tab_id;
      }
      
      if (!selected)
        return note;
      
      var parents = note.parents('div.oe_notebook_page');
      if(parents.length) {
        parents.each(function() {
          if($(this).context && $(this).context.id) {
            self.parent_tab_id = $(this).context.id;
          }
        });
      }
      note.tabs('select', selected);

      return note;

    }
  });

};
