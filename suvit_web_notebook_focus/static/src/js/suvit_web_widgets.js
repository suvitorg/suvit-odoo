openerp.suvit_web_notebook_focus = function(instance, local) {
  //TODO odoo10.0
  return;

  instance.web.form.FormRenderingEngine.include({

    process_notebook: function($notebook) {

      var selected;
      var pages = $notebook.find('> page');
      var action = this.view.ViewManager.action;
      var af_name = action && action.context.autofocus;

      pages.each(function(i) {
          var $page = $(this);
          var page_attrs = $page.getAttributes();
          if (page_attrs.autofocus || (af_name && page_attrs.name == af_name))
            selected = i;
      });

      var note = this._super($notebook);

      if (selected)
        note.tabs('select', selected);

      return note;

    }
  });

};
