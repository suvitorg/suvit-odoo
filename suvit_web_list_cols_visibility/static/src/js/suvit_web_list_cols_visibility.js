odoo.define('suvit_web_list_cols_visibility', function (require) {
  //TODO odoo10.0
  return;
"use strict";
  
  var localStorage = window['localStorage'] || {};
  var ListView = require('web.ListView');
  
  ListView.include({
    setup_columns: function (fields, grouped) {
        var self = this;
        this._super(fields, grouped);
        self.fields_addition_class = {};
        _.map(self.fields_view.arch.children, function(field){
            if (field.attrs.class) {
                self.fields_addition_class[field.attrs.name] = field.attrs.class;
            }
        });
        
    }
  });
  
  ListView.List.include({
    render_record: function (record) {
        self = this;
        var classes = self.view.fields_addition_class;
        r = this._super(record);
        d = $(r);
        for (field in classes) {
            d.find('.oe_list_field_cell[data-field="'+field+'"]').addClass(classes[field]);
        }
        return d;
    },
    render: function () {
        self = this;
        var classes = self.view.fields_addition_class;
        self._super();
        for (field in classes) {
            var ind = self.columns.findIndex(function(col, i){
                if (col.name == field)
                  return i;
            });
            if (!ind)
              continue;

            self.$current.find('tr').each(function(){
              $(this).children('td[data-field="'+field+'"]').addClass(classes[field]);
            });
            self.view.$el.find('th[data-id="'+field+'"], .oe_list_footer:eq('+ind+')').addClass(classes[field]);
        }
    },
  });

});