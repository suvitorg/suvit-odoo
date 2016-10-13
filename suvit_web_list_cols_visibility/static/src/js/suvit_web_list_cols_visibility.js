openerp.suvit_web_list_cols_visibility = function(instance, local) {
  var localStorage = window['localStorage'] || {},
      QWeb = instance.web.qweb;

  instance.web.ListView.include({
    setup_columns: function (fields, grouped) {
        var self = this;
        this.load_hide_cols();
        self.fields_addition_class = {};
        _.map(self.fields_view.arch.children, function(field){
            if (self.hide_cols[field.attrs.name] !== undefined ) {
                self.add_invisible(field, self.hide_cols[field.attrs.name]);
            }
            if (field.attrs.class) {
                self.fields_addition_class[field.attrs.name] = field.attrs.class;
            }
        });
        this._super(fields, grouped);
    }
  });
  instance.web.ListView.List.include({
    render_record: function (record) {
        self = this;
        classes = self.view.fields_addition_class;
        r = this._super(record);
        d = $(r);
        for (field in classes) {
            d.find('.oe_list_field_cell[data-field="'+field+'"]').addClass(classes[field]);
        }
        return d;
    },
    render: function () {
        self = this;
        classes = self.view.fields_addition_class;
        self._super();
        for (field in classes) {
            var ind = self.columns.findIndex(function(col, i){
                if (col.name == field)
                  return i;
            });
            if (!ind)
              continue;

            self.$current.find('tr').each(function(){
              var row_ind = ($(this).find('.oe_list_record_selector').length ? ind : ind - 1);
              $(this).children('td:eq('+row_ind+')').addClass(classes[field]);
            });
            self.view.$el.find('th[data-id="'+field+'"], .oe_list_footer:eq('+ind+')').addClass(classes[field]);
        }
    },
  });
};
