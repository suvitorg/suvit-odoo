odoo.define('web.autofocus', function (require) {
"use strict";

  var FormRenderer = require('web.FormRenderer');

  FormRenderer.include({

    _renderTagNotebook: function($notebook) {
      var af_name = this.state.context.autofocus;
      if (!af_name)
        return this._super($notebook);

      var pages = $notebook.find('> page');
      pages.each(function(i) {
          var $page = $(this);
          var page_attrs = $page.getAttributes();
          if (page_attrs.autofocus && page_attrs.name != af_name){
            $page.removeAttr('autofocus');
          } else if (page_attrs.name == af_name && !page_attrs.autofocus){
            $page.attr('autofocus', true);
          }
      });

      return this._super($notebook);

    }
  });

});
