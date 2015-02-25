alert(123);
openerp.suvit_web_widgets = function(instance, local) {

  /*** TREE IMAGE ***/
  instance.web.list.ImageField = instance.web.list.Column.extend({
    _format: function (row_data, options) {
      var value = row_data[this.id].value;
        if (value){
          var download_url = instance.session.url('/web/binary/saveas',
                                                  {model: options.model, field: this.id, id: options.id});
          console.log(download_url);
          return _.template('<image src="<%-src%>" height="20px" />', {
            src: download_url,
          });
        } else {
          return '';
        }
    }
  });

  instance.web.list.columns.add('field.tree_image','instance.web.list.ImageField');

};
