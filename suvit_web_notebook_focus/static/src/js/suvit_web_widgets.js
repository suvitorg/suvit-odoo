openerp.suvit_web_notebook_focus = function(instance, local) {

  console.log('suvit_web_notebook_focus');

  instance.web.form.FormRenderingEngine.include({

    process_notebook: function($notebook) {

      var selected;
      var i = 0;

      $notebook.find('> page').each(function() {
        var $page = $(this);
        var page_attrs = $page.getAttributes();
        if (page_attrs.autofocus)
          selected = i;
        i = i + 1;
      });

      var note = this._super($notebook);

      if (selected !== undefined)
        note.tabs('select', selected);

      return note;

    }
  });

};
