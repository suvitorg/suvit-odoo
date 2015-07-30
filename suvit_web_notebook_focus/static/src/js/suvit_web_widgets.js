openerp.suvit_web_notebook_focus = function(instance, local) {

  instance.web.form.FormRenderingEngine.include({

    process_notebook: function($notebook) {

      var selected;
      var pages = $notebook.find('> page');
      var autofocus_page_name = this.view.ViewManager.action.context.autofocus;

      if (autofocus_page_name){
        pages.each(function(i) {
          var $page = $(this);
          var page_attrs = $page.getAttributes();
          if (page_attrs.name == autofocus_page_name)
            selected = i;
        });
      } else {
        pages.each(function(i) {
          var $page = $(this);
          var page_attrs = $page.getAttributes();
          if (page_attrs.autofocus)
            selected = i;
        });
      }

      var note = this._super($notebook);

      if (selected)
        note.tabs('select', selected);

      return note;

    }
  });

};
