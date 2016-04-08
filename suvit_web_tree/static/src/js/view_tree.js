openerp.suvit_web_tree = function(instance, local) {
  var QWeb = instance.web.qweb;
  var _t = instance.web._t;
  var _lt = instance.web._lt;

  /********* Custom domain for List & Tree Views in same Action ********/
  instance.web.FormView.include({
      on_button_save: function(e) {
          var self = this;
          _.each(this.ViewManager.ActionManager.breadcrumbs, function(br){
            br.need_update = true;
          });

          return self._super(e).then(function(){
              if (self.ViewManager.views.tree)
                self.ViewManager.views.tree.controller.switch_mode()
          });
      },
      on_button_create: function() {
          var self = this;
          self._super();
          if (self.ViewManager.views.tree)
            self.ViewManager.views.tree.controller.switch_mode()
      }
  });

  instance.web.TreeView.include({
    init: function (parent, dataset, view_id, options) {
        if (parent.action && parent.action.context.tree_domain){
          var domain = new instance.web.CompoundDomain(dataset.domain, parent.action.context.tree_domain);
          dataset = new instance.web.DataSetSearch(this, parent.action.res_model, dataset.context, domain);
        }
        this._super(parent, dataset, view_id, options);
    },
    switch_mode: function () {
      this.$el.find(".oe-treeview-table > tbody").empty();
      _(this.fields_view.arch.children).each(function (field) {
          if (field.attrs.modifiers && typeof(field.attrs.modifiers) == 'object') {
              field.attrs.modifiers = JSON.stringify(field.attrs.modifiers);
          }
      });
      this.view_loading(this.fields_view);
    },
    hook_row_click: function () {
      this.$el.undelegate('.treeview-tr', 'click');
      this._super();
    },


    getdata: function (id, children_ids) {
        // do not getdata twice, this class stop loading
        this.$el.find('#treerow_' + id).addClass('oe_open');

        var self = this;

        self.dataset.read_ids(children_ids, this.fields_list()).done(function(records) {
            _(records).each(function (record) {
                self.records[record.id] = record;
            });
            var $curr_node = self.$el.find('#treerow_' + id);
            var children_rows = QWeb.render('TreeView.rows', {
                'records': records,
                'children_field': self.children_field,
                'fields_view': self.fields_view.arch.children,
                'fields': self.fields,
                'level': $curr_node.data('level') || 0,
                'render': instance.web.format_value,
                'color_for': self.color_for,
                'row_parent_id': id
            });
            if ($curr_node.length) {
                $curr_node.addClass('oe_open');
                $curr_node.after(children_rows);
            } else {
                self.$el.find('tbody').html(children_rows);
            }
        }).then(function(){
          if (self.ViewManager.action && self.ViewManager.action.id) {
            view_id = self.ViewManager.action.id;
            var open_trees = JSON.parse(localStorage.getItem('open_trees') || '{}');
                if (!open_trees[view_id]) {open_trees[view_id] = {};}
            open_trees[view_id][id] = true;
            localStorage["open_trees"] = JSON.stringify(open_trees);
            for(k in open_trees[view_id]){
              if (open_trees[view_id][k]) {
                $('#treerow_'+k+':not(.oe_open) .treeview-tr').click();
              }
            }
          }
        });
    },



    showcontent: function (curnode,record_id, show) {
      this._super(curnode,record_id, show);
      if (this.ViewManager && this.ViewManager.action) {
        view_id = this.ViewManager.action.id;
        var open_trees = JSON.parse(localStorage.getItem('open_trees') || '{}');
        if (!open_trees[view_id]) {open_trees[view_id] = {};}
        open_trees[view_id][record_id] = show;
        localStorage["open_trees"] = JSON.stringify(open_trees);
      }
    },
  });
  instance.web.ActionManager.include({
    select_breadcrumb: function(index, subindex) {
      var self = this;
      var item = this.breadcrumbs[index];
      if (item.widget.views.tree && item.need_update) {
        item.need_update=false;
        item.widget.views.tree.controller.switch_mode();
      }
      return this._super(index, subindex);
    },
  });

  /********* Many2Many Tree Field ********/
  local.Many2ManyTreeField = instance.web.form.FieldMany2Many.extend({
    initialize_content: function() {
        if (!(this.field.type == 'many2many' || this.field.type == 'one2many'))
            return this._super();
        this.list_view = new instance.web.TreeView(this, this.dataset, false, {
                    'addable': false,
                    'deletable': false,
                    'selectable': false,
                    'sortable': false,
                    'reorderable': false,
                    'import_enabled': false,
            });
        this.$el.empty();
        this.list_view.appendTo(this.$el);
    },
    render_value: function() {
      this.initialize_content();
      return this._super();
    }
  });

  instance.web.form.widgets.add('many2many_tree', 'instance.suvit_web_tree.Many2ManyTreeField');
};
