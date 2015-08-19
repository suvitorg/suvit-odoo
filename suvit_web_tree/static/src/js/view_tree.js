openerp.suvit_web_tree = function(instance, local) {

  /********* Custom domain for List & Tree Views in same Action ********/
  instance.web.TreeView.include({

    init: function (parent, dataset, view_id, options) {

        if (parent.action && parent.action.context.tree_domain){
          var domain = new instance.web.CompoundDomain(dataset.domain, parent.action.context.tree_domain);
          dataset = new instance.web.DataSetSearch(this, parent.action.res_model, dataset.context, domain);
        }

        this._super(parent, dataset, view_id, options);
    }

  });

  /********* Many2Many Tree Field ********/
  local.Many2ManyTreeField = instance.web.form.FieldMany2Many.extend({

    initialize_content: function() {

        if (this.field.type != 'many2many')
            return this._super();

        this.list_view = new instance.web.TreeView(this, this.dataset, false, {
                    'addable': false,
                    'deletable': false,
                    'selectable': false,
                    'sortable': false,
                    'reorderable': false,
                    'import_enabled': false,
            });
        this.list_view.appendTo(this.$el);
    },
  });

  instance.web.form.widgets.add('many2many_tree', 'instance.format_core.Many2ManyTreeField');

};
