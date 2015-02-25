openerp.suvit_web_widgets = function(instance, local) {

  /*** TREE IMAGE ***/
  instance.web.list.ImageField = instance.web.list.Column.extend({
    _format: function (row_data, options) {
      var value = row_data[this.id].value;
        if (value){
          var download_url = instance.session.url('/web/binary/saveas',
                                                  {model: options.model, field: this.id, id: options.id});

          return _.template('<image src="<%-src%>" height="<%-height%>px" />', {
            src: download_url,
            height: this.height || '30'
          });
        } else {
          return '';
        }
    }
  });

  instance.web.list.columns.add('field.tree_image','instance.web.list.ImageField');

};
