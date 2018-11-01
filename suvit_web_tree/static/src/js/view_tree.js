odoo.define('suvit.web.tree', function(require) {

    var core = require('web.core');
    var ActionManager = require('web.ActionManager');
    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;
    var FormView = require('web.FormView');
    var TreeView = require('web.TreeView');
    var FieldMany2Many = core.form_widget_registry.get('many2many');
    var data = require('web.data');
    var formats = require ("web.formats");

    FormView.include({
      init1: function(parent, dataset, view_id, options) {
        var self = this;
        this._super(parent, dataset, view_id, options);
        //if (self.dataset.context && self.dataset.context.tree_ids && self.dataset.context.tree_ids.length) {
        //    self.dataset.ids = self.dataset.context.tree_ids;
        //    self.dataset.index = self.dataset.ids.indexOf(self.dataset.context.active_id);
        //}
      },
      // TODO support odoo10
      DONT_WORK_on_button_save: function(e) {
          var self = this;
          _.each(this.ViewManager.ActionManager.breadcrumbs, function(br){
            br.need_update = true;
          });

          return self._super(e).then(function(){
              if (self.ViewManager.views.tree)
                self.ViewManager.views.tree.controller.switch_mode()
          });
      },
      DONT_WORK_on_button_create1: function() {
          var self = this;
          self._super();
          if (self.ViewManager.views.tree)
            self.ViewManager.views.tree.controller.switch_mode()
      }
    });

    TreeView.include({
        init: function (parent, dataset, fields_view, options) {
            if (parent.action && parent.action.context.tree_domain){
              var domain = new data.CompoundDomain(dataset.domain, parent.action.context.tree_domain);
              dataset = new data.DataSetSearch(this, parent.action.res_model, dataset.context, domain);
            }
            this._super(parent, dataset, fields_view, options);
        },
        switch_mode: function () {
          this.$el.find(".oe-treeview-table > tbody").empty();
          _(this.fields_view.arch.children).each(function (field) {
              if (field.attrs.modifiers && typeof(field.attrs.modifiers) == 'object') {
                  field.attrs.modifiers = JSON.stringify(field.attrs.modifiers);
              }
          });
          this.reload_content();
        },
        hook_row_click: function () {
          this.$el.undelegate('.treeview-tr', 'click');
          this._super();
        },
        getdata: function (id, children_ids) {
            // do not getdata twice, this class stop loading
            this.$el.find('#treerow_' + id).addClass('oe_open');

            var self = this;

            // copied from multi_model_tree module because here not called _super
            if (!self.real_context)
              self.real_context = self.dataset._model._context;
            self.dataset._model._context = new data.CompoundContext(self.real_context,
                                                                            {tree_parent_ids: self.getparents(id)});
            //

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
                    'render': formats.format_value,
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
        activate: function(id) {
          if (this.ViewManager.ActionManager) {
            parent = false;
            for (i in this.records) {
              if (_.indexOf(this.records[i].child_ids, id)+1) {
                parent = i;
                break;
              }
            }
            if (parent) {
              our_ids = this.records[parent].child_ids
            } else {
              our_ids = this.dataset.ids
            }
            this.ViewManager.ActionManager.tree_context = {
              tree_ids: our_ids
            };
          }
          this._super(id);
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

    ActionManager = ActionManager.include({
        select_breadcrumb: function(index, subindex) {
          var self = this;
          var item = this.breadcrumbs[index];
          if (item.widget.views.tree && item.need_update) {
            item.need_update=false;
            item.widget.views.tree.controller.switch_mode();
          }
          return this._super(index, subindex);
        },
        do_action: function(action, options) {
          if (this.tree_context) {
            options = _.defaults(options || {}, {
                additional_context: {},
            });
            options.additional_context.tree_ids = this.tree_context.tree_ids;
          }
          return this._super(action, options);
        }
    });

    var Many2ManyTreeField = FieldMany2Many.extend({
        initialize_content: function() {
            if (!(this.field.type == 'many2many' || this.field.type == 'one2many'))
                return this._super();
            this.list_view = new TreeView(this, this.dataset, false, {
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

    core.form_widget_registry.add('many2many_tree', Many2ManyTreeField);

});
