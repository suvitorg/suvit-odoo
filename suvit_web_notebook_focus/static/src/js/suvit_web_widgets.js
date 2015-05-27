openerp.suvit_web_notebook_focus = function(instance, local) {

  instance.web.form.FormRenderingEngine.include({

    process_notebook: function($notebook) {

      var selected;

      $notebook.find('> page').each(function(i) {
        var $page = $(this);
        var page_attrs = $page.getAttributes();
        if (page_attrs.autofocus)
          selected = i;
      });

      var note = this._super($notebook);

      if (selected !== undefined)
        note.tabs('select', selected);

      return note;

    }
  });

};
