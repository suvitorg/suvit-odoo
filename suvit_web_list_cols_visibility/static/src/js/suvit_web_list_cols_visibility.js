odoo.define('suvit_web_list_cols_visibility', function (require) {
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
        var res = this._super(record);
        this.set_additional_classes();
        return res;
    },
    render: function () {
        this._super();
        this.set_additional_classes();
    },
    set_additional_classes: function () {
        if (!this.view.fields_addition_class)
          return;

        var self = this;
        _.each(_.pairs(this.view.fields_addition_class), function(field){
            self.$current.find("td[data-field='" + field[0] + "']").addClass(field[1]);
        });
    }
  });

});