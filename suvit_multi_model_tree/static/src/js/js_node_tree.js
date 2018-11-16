odoo.define('suvit.multi.model.tree', function (require) {
"use strict";

  var core = require('web.core');
  var TreeView = require('web.TreeView');
  var ListView = require('web.ListView');
  var View = require('web.View');
  var FormView = require('web.FormView');
  var FieldMany2Many = core.form_widget_registry.get('many2many');
  var QWeb = core.qweb;
  var _t = core._t;
  var Model = require('web.Model');
  var pyeval = require('web.pyeval');
  var data = require('web.data');
  var common = require('web.form_common');
  var formats = require('web.formats');
  var One2ManyListView = core.one2many_view_registry.get('list');
  var ActionManager = require('web.ActionManager');

  var process_model = false;
  var document_model = false;
  var field_model = false;
  var config_model = new Model("ir.config_parameter");
  config_model.call("get_param", ['PROCESS_MODEL']).then(function(value) {
    process_model = value || "format.frontend.demo.process";
  });
  config_model.call("get_param", ['DOCUMENT_MODEL']).then(function(value) {
    document_model = value || "format.frontend.demo.process.document";
  });
  config_model.call("get_param", ['FIELD_MODEL']).then(function(value) {
    field_model = value || "format.frontend.demo.process.document.field";
  });

  FormView.include({
    on_button_save: function(e) {
      var self = this;
      return self._super(e).then(function(){
          if (self.ViewManager.views.js_node_tree)
            self.ViewManager.views.js_node_tree.controller.switch_mode();
      });
    },
    on_button_create: function() {
      var self = this;
      self._super();
      if (self.ViewManager.views.js_node_tree)
        self.ViewManager.views.js_node_tree.controller.switch_mode();
    }
  });


  var JsNodeTreeView = View.extend({
    view_type: 'js_node_tree',
    destroy: function () {
      if (this.$jstree)
        this.$jstree.jstree('destroy');
      this._super();
    },
    init: function (parent, dataset, fields_view, options) {
      this._super(parent, dataset, fields_view, options);
      this.records = {};
      var attrs = parent.x2m ? parent.x2m.node.attrs : fields_view.arch.attrs
      this.field_parent = attrs.field_parent;
      this.nodrag = attrs.nodrag;
    },
    switch_mode: function(opt){
      this.reload_tree(opt);
    },
    start: function(){
      this.reload_tree();
    },
    reload_tree: function(opt){
      this.$el.empty();
      this.load_tree(opt);
      // if (!this.options.nodrag) this.$el.append(this.$dragging_option);
      this.$el.append(this.$jstree);
      $('.dragging_option').remove();
      if (!this.nodrag){
        this.$el.before(this.$dragging_option);
      }
    },
    load_records: function (records) {
      var self = this;
          // TODO check
          self.new_records = [];

      _(records).each(function (record) {
          //console.log('record', record);
          self.records[record.id] = record;
          self.new_records.push(record);

          record.text = record[self.tree_name_field];
          record.type = record[self.tree_type_field] || self.model;
          record.tree_type = record.type;
          record.icon = null; // TODO fix old icons
          record.children = !!(record[self.field_parent] && record[self.field_parent].length);
      });
    },
    // get_process_child_field: function(tree_inst, process) {
    //   // console.log(process);
    //   _.each(process.children_d, function(n){
    //     node = tree_inst.get_node(n);
    //     if (node.type == document_model) {
    //       self.dataset._model.call('search_read',
    //     }
    //   });
    // },
    get_id: function(full_id) {
      return parseInt(full_id.toString().split('-').pop());
    },
    activate: function (full_id, our_ids, parent_id, context) {
      // console.log('JSTree.activate', arguments);
      var self = this;
      var id = self.get_id(full_id);

      if (this.options.row_action)
        return this.options.row_action(id, self.$jstree.jstree(true).get_node(full_id).original.tree_type);

      var local_context = _.extend({active_model: self.model,
                                    active_id: id,
                                    tree_ids: our_ids
                                    }, context);
      if (parent_id) {
        local_context.default_parent_id = self.get_id(parent_id);
      }
      var ctx = pyeval.eval(
          'context', new data.CompoundContext(
              self.dataset.get_context(), local_context));

      return self.rpc('/web/treeview/action', {
          id: id,
          model: self.dataset.model,
          context: ctx
      }).then(function (actions) {
          if (!actions.length) { return; }
          var action = actions[0][2];
          var c = new data.CompoundContext(local_context).set_eval_context(ctx);
          if (action.context) {
              c.add(action.context);
          }
          action.context = c;
          return self.do_action(action);
      });
    },
    do_create_record: function (form_view, element, context) {
      var self = this;
      var pop = new common.SelectCreateDialog(this);
      var domain = {};
      pop.select_element(
          form_view.model,
          {
              title: _t("Create: ") + element.name,
              initial_view: "form",
              form_view_options: {'not_interactible_on_create':true},
              create_function: function(data, options) {
                // console.log('CreatePopup create callback');
                return form_view.dataset._model.call('create', [data]);
              }
          },
          new data.CompoundDomain(domain),
          new data.CompoundContext(form_view.dataset.context, context)
      );
      pop.on('closed', self, function(){
        self.reload_tree(self.$dragging.is(':checked'));
      });
    },
    do_add_record: function (listView, $node, element, domen) {
        var self = this;
        var pop = new common.SelectCreateDialog(listView);
        var tmp_childs = [];
        _.each($node.children, function(num){
          var tmp_node = self.$jstree.jstree(true).get_node(num);
          if (tmp_node.original.tree_type == listView.model) {
            tmp_childs.push(tmp_node.original.tree_obj_real_id);
          }
        });
        result_domain = ["!", ["id", "in", tmp_childs]];
        if (domen && domen.length) {
          result_domain.push(domen);
        }
        pop.select_element(
            listView.model,
            {
                title: _t("Add: ") + element.name,
                no_create: false,
            },
            new data.CompoundDomain(result_domain),
            // {},
            listView.dataset.context
        );
        pop.on("elements_selected", listView, function(element_ids) {
            var vals = {};
            // element_ids = _.union(tmp_childs, element_ids)
            // vals[element.field] = [[6, false, element_ids]]; //[4]
            vals[element.field] = [];
            _.each(element_ids, function(i){
              vals[element.field].push([4, i]);
            });
            new Model($node.type).call('write', [
                [parseInt($node.original.tree_obj_real_id)],
                vals
            ]).then(function(){
              self.reload_tree(self.$dragging.is(':checked'));
            });
        });
    },
    load_tree: function (dragging_on) {
      if (!this.field_parent)
        this.field_parent = this.fields_view.field_parent || this.options.field_parent;
      if (!this.field_parent)
        return;

      var self = this;

      self.$jstree = $(QWeb.render("JsNodeTreeView", this));

      self.$dragging_option = $('<label/>', {text: 'Перемещение в дереве', class: 'dragging_option'});
      self.$dragging = $('<input/>', {type: 'checkbox', class: 'dragging_button'}).prop('checked', dragging_on);
      self.$dragging_option.append(self.$dragging);

      self.tree_name_field = self.fields_view.arch.children[0].attrs.name;
      self.tree_icon_field = this.fields_view.arch.attrs.icon_field || self.options.icon_field;
      self.tree_type_field = this.fields_view.arch.attrs.tree_type || self.options.tree_type;
      self.tree_title_field = this.fields_view.arch.attrs.tree_title_field || self.options.tree_title_field || 'title';

      self.field_parent = this.fields_view.field_parent || this.options.field_parent;

      self.tree_config = {};
      var config_loaded = $.Deferred();
      if (this.fields_view.arch.attrs.tree_dynamic_config) {
          config_loaded = self.dataset._model
                              .call('get_tree_config', [],
                                    {'context': self.dataset.get_context()});
          config_loaded.then(function(result){
              _.extend(self.tree_config, result || {});
          })
      } else {
          self.tree_config = this.fields_view.arch.attrs.tree_config ? pyeval.py_eval(this.fields_view.arch.attrs.tree_config) : {};

          _.each(self.tree_config, function(element, name){
              _.each(element.create, function(child){
                  if (child.model)
                     _.defaults(self.tree_config[name], {'valid_children': []})
                     self.tree_config[name]['valid_children'].push(child.model);
              });
          });
          config_loaded.resolve();
      }

      this.fields_view.fields[self.tree_type_field] = {};
      this.fields_view.fields[self.tree_title_field] = {};
      this.fields_view.fields[self.field_parent] = {};
      if (self.tree_type_field) {
          this.fields_view.fields[self.tree_type_field] = {};
      }

      // console.log('JSTree.load', Object.keys(this.fields_view.fields));

      this.tree_fields_cols = [{'header': this.fields_view.arch.attrs.tree_title || 'Структура'}];
      _.each(this.fields_view.arch.children, function(col){
        if (col.tag == 'field' && !col.attrs.invisible){
            self.tree_fields_cols.push({
              'header': self.fields_view.fields[col.attrs.name]['string'],
              'value': function (node) {
                return formats.format_value(node.original[col.attrs.name],
                                                 self.fields_view.fields[col.attrs.name]);
              }
            });
        }
      });
      var ids = _.uniq(_.filter(this.dataset.ids, function(i){
        if (!isNaN(i) && typeof i != "string") {
          return true;
        }
      }));
      this.dataset.alter_ids(ids);

      return config_loaded.done(function() {
        self.jstree_load();
      });
    },



    jstree_contextmenu_create: function(data) {
      var self = this,
          inst = $.jstree.reference(data.reference),
          obj = inst.get_node(data.reference);
          element = data.item.config;

      //console.log('contextmenu.create', data, inst, obj, inst.get_node(obj.parent));
      if (data.item.level == 'Уровень') {
        var parent = inst.get_node(obj.parent);
      } else {
        var parent = obj
      }

      // debugger;
      var context = {};
      context['default_' + (element.parent_field || 'parent_id')] = self.get_id(parent.original && (parent.original.tree_obj_real_id || parent.original.id) || false);
      if (element.model && element.model != self.dataset.model)
        context['default_object_id_selection'] = element.model + ',';
      // console.log('contextmenu.create parent', element, context)
      // TODO use X2ManyDataSet
      var dataset = new data.BufferedDataSet(self, self.dataset.model);
      dataset.x2m = self;
      var One2ManyFormView = new One2ManyListView(self, dataset, false, {});

      self.do_create_record(One2ManyFormView, element, context);
    },
    jstree_contextmenu_join: function(data){
      var self = this;
      var element = data.item.config;
      var my_model = self.dataset.model;
      // TODO use X2ManyDataSet
      var dataset = new data.BufferedDataSet(self, my_model);
      dataset.x2m = self;
      // TODO use Many2ManyListView
      var Many2ManyListView = new instance.web.form.Many2ManyListView(self, dataset, false, {});

      var inst = $.jstree.reference(data.reference);
      obj = inst.get_node(data.reference);

      var domen = [];
      if (model == process_model && my_model == field_model) {
        tree_ids = _.filter(obj.children, function(child){
          return inst.get_node(child).original.type == document_model;
        });
        documents = _.map(tree_ids, function(id){
          return self.get_id(inst.get_node(id).original.tree_obj_real_id);
        });
        domen = ['document_ids' , 'in', documents];
      }
      self.do_add_record(Many2ManyListView, $node, element, domen);
    },
    jstree_contextmenu_copy: function(data){
      var self = this,
          inst = $.jstree.reference(data.reference),
          obj = inst.get_node(data.reference);

      var ctx = new data.CompoundContext(self.dataset.get_context(), {'new_parent': self.get_id(obj.parent)});

      self.dataset._model
        .call('action_duplicate',
              [self.get_id(obj.id)],
              {'context': ctx})
        .then(function(){
           self.reload_tree(self.$dragging.is(':checked'));
        });
    },
    jstree_contextmenu_paste: function (data) {
      var inst = $.jstree.reference(data.reference),
          obj = inst.get_node(data.reference),
          copied = inst.get_buffer().node[0].id;

      self.dataset._model
        .call('add',
              [self.get_id(obj.id), self.get_id(copied)],
              {'context': self.dataset.get_context()})
        .then(function(){
           inst.paste(obj);
           inst.clear_buffer();
        });
    },
    jstree_config_contextmenu: function($node) {
      var self = this,
          tree = self.$jstree.jstree(true),
          parent = tree.get_node($node.parent),
          model_config = self.tree_config[$node.type];

      // console.log('contextmenu $node', $node, '$parent', parent);

      if (parent) {
        var parent_create_type = self.tree_config[parent.type] || {'create': false};
      } else {
        var parent_create_type = model_config;
      }

      model_config = _.extend({create: false,
                               copy: false,
                               edit: false,
                               delete: false,
                               settings: true}, model_config);
      // console.log('context config',
      //             'parent', parent.type, parent_create_type,
      //             'model', $node.type, model_config);
      var menu_items = {};

      if (model_config.create) {
        var create_menu = {}
        _.each(['Уровень', 'Подуровень'], function(level){
          var submenu = {},
              create_type_list = (level == 'Уровень' ? parent_create_type : model_config).valid_children;
          if (!create_type_list)
            return;

          _.each(create_type_list, function(key){
            var config = self.tree_config[key];
            config.model = key;
            submenu['create_'+key] = {
              "label": config.name,
              "action": self.proxy(self.jstree_contextmenu_create),
              "config": config,
              "level": level,
            };
          });
          create_menu[level] = {
            "label": level,
            "submenu": submenu
          };

        });
        menu_items['create'] = {
          "label": "Создать",
          "submenu": create_menu
        };

        if (1 || model_config.copy) {
          menu_items.clone = {
            "label": "Дублировать",
            "action": self.proxy(self.jstree_contextmenu_copy),
          };
          menu_items.copy = {
            "label": "Копировать",
            "action": function (data) {
              var inst = $.jstree.reference(data.reference);
              obj = inst.get_node(data.reference);

              self.dataset._model.call('action_copy',
                                       [self.get_id(obj.id)],
                                       {'context': self.dataset.get_context()}).then(function(){
                self.reload_tree(self.$dragging.is(':checked'));
                inst.copy(obj);
              });
            }
          };
          /* menu_items.paste = {
            "label": "Вставить",
            "_disabled": function (data) {
              return !$.jstree.reference(data.reference).can_paste();
            },
            "action": self.proxy(self.jstree_contextmenu_paste),
          }; */
        }
      }
      if (model_config.delete) {
        var submenu = {};
        submenu.unlink = {
          "label": "Удалить узел",
          "action": function (data) {
            var inst = $.jstree.reference(data.reference),
                obj = inst.get_node(data.reference);

            // console.log('JSTree.unlink', inst, obj);
            if (!confirm('Вы действительно хотите удалить узел "' + obj.text + '"?'))
              return;

            self.dataset._model.call('unlink', [self.get_id(obj.id)], {'context': self.dataset.get_context()}).then(function(){
              self.reload_tree(self.$dragging.is(':checked'));
            });
          }
        };
        submenu.remove = {
          "label": "Отцепить узел",
          "action": function (data) {
            var inst = $.jstree.reference(data.reference),
                obj = inst.get_node(data.reference);

            // console.log('JSTree.unlink', data, inst, obj);
            if (!confirm('Вы действительно хотите отцепить узел "' + obj.text + '"?'))
              return;

            var local_context = {
              'new_parent': self.get_id(obj.parent)
            };
            var ctx = new data.CompoundContext(self.dataset.get_context(), local_context);

            self.dataset._model.call('action_remove', [self.get_id(obj.id)], {'context': ctx}).then(function(){
              self.reload_tree(self.$dragging.is(':checked'));
              // inst.delete_node(obj);
            });
          }
        };
        submenu.exclude = {
          "label": "Исключить узел",
          "action": function (data) {
            var inst = $.jstree.reference(data.reference),
                obj = inst.get_node(data.reference);

            // console.log('JSTree.unlink', inst, obj);
            if (!confirm('Вы действительно хотите исключить узел "' + obj.text + '"?'))
              return;

            var local_context = {
              'new_parent': self.get_id(obj.parent)
            };
            var ctx = new data.CompoundContext(self.dataset.get_context(), local_context);

            self.dataset._model.call('action_exclude', [self.get_id(obj.id)], {'context': ctx}).then(function(){
              self.reload_tree(self.$dragging.is(':checked'));
              //inst.delete_node(obj);
            });
          }
        };
        menu_items['delete'] = {
          "label": "Удалить",
          "submenu": submenu
        };
      };
      if (model_config.edit) {
        menu_items.rename = {
          "label": "Переименовать",
          "action": function(data){
            var inst = $.jstree.reference(data.reference),
                obj = inst.get_node(data.reference);
            inst.edit(obj);
          }
        };
      }
      if (model_config.settings) {
        menu_items.settings = {
          "label": "Настроить",
          "action": function(data){
            var inst = $.jstree.reference(data.reference),
                obj = inst.get_node(data.reference);
            // console.log('Tree.contexmenu.settings', data, obj);
            self.activate(obj.id, null, null, {'node_settings_form': true});
          }
        }
      }
      //console.log('jstree contextmenu', menu_items);
      return menu_items;
    },
    jstree_config_check: function (op, node, par, pos, more) {
      /*if(op === "move_node" && more && more.core) {
        console.log('11111111', node, par);
        var local_context = {
          // 'old_parent': data.old_parent,
          // 'old_parent_id': self.get_id(data.old_parent),
          // 'old_position': data.old_position,
          // 'new_position': data.position,
        };
        var ctx = new data.CompoundContext(self.dataset.get_context(), local_context);
        prom = self.dataset._model.call('change_parent',
           [self.get_id(node.id), self.get_id(par.id)],
           {'context': ctx}).fail(function(){
            // self.tree_el.jstree(true).move_node(data.node, data.old_parent);
            // return false;
           });

          console.log(prom.isResolved(), prom.isRejected());
      }*/
      return true;
    },
    jstree_config_data: function (obj, cb) {
      var self = this;

      // console.log('config_data', self, obj, self.records);

      if (obj.id == "#") {
        this.dataset.read_slice(this.fields_view.fields,
                               {context: {bin_size: true}}).done(function(records) {
          self.load_records(records);
          cb.call(this, self.new_records);
        });
      } else {
        var childs = self.records[obj.id][self.field_parent];
        var parents = obj.id.toString().split('-');
        // console.log('check parents', obj.id, parents);
        self.dataset.read_ids(childs,
                              Object.keys(self.fields_view.fields),
                              {context: {"tree_parent_ids": parents,
                                         "bin_size": true}}
        ).done(function(records) {
          self.load_records(records);
          cb.call(this, self.new_records);
        });
      }
    },
    jstree_config: function () {
      var self = this,
          state_key = "jstree_" + (self.ViewManager.action ? self.ViewManager.action.id : 'field');

      return {
        "plugins": [
           "core", "ui", "contextmenu", "wholerow", "state", "dnd", "types", "grid"
        ],
        "core": {
          "animation": 0,
          "check_callback": self.proxy(self.jstree_config_check),
          "themes": {"stripes": true},
          "data": self.proxy(self.jstree_config_data)
        },
        "contextmenu":{
          "select_node": false,
          "show_at_node": false,
          "items": self.proxy(self.jstree_config_contextmenu),
        },
        "state":{
          "key": state_key,
          "filter" : function (k) { delete k.core.selected; return k; }
        },
        "dnd": {
          "is_draggable" : function(node) {return !!self.$dragging.is(':checked');}
        },
        "types": self.tree_config,
        'grid': {
          'columns': self.tree_fields_cols
        }
      }
    },
    jstree_rename_node: function(event, data) {
      // console.log("rename");
      var self = this;
      upd_item = {};
      upd_item[self.tree_name_field] = data.text;
      this.dataset._model.call('write', [self.get_id(data.node.id), upd_item]);
    },
    jstree_delete_node: function(event, data) {
      // console.log("delete_node");
    },
    jstree_select_node: function(event, data) {
      var self = this;
      var our_ids = _.map(self.$jstree.jstree(true).get_node(data.node.parent).children, function(id){
        return self.get_id(id);
      });
      self.activate(data.node.id, our_ids);
    },
    jstree_create_node: function(event, data) {
      // console.log("create");
    },
    jstree_move_node: function(event, data) {
      var self = this;
      // console.log('change_parent', this, data);
      var local_context = {
        'old_parent': data.old_parent,
        'old_parent_id': self.get_id(data.old_parent),
        'old_position': data.old_position,
        'new_parent': data.parent,
        'new_parent_id': self.get_id(data.parent),
        'new_position': data.position,
      };
      var ctx = new data.CompoundContext(self.dataset.get_context(), local_context);
      self.dataset._model.call('action_change_parent',
                               [self.get_id(data.node.id)],
                               {'context': ctx}).fail(function(){
                                self.reload_tree(self.$dragging.is(':checked'));
                               });
    },
    jstree_load: function () {
      var self = this;

      self.$jstree.jstree('destroy');
      self.$jstree.jstree(this.jstree_config());

      self.$jstree
        .on("rename_node.jstree", self.proxy(self.jstree_rename_node))
        .on("delete_node.jstree", self.proxy(self.jstree_delete_node))
        .on("select_node.jstree", self.proxy(self.jstree_select_node))
        .on("create_node.jstree", self.proxy(self.jstree_create_node))
        .on('move_node.jstree', self.proxy(self.jstree_move_node))
        .on('hover_node.jstree',function(e, data){
          // console.log('JSTree.hover', data);
          $("#" + data.node.id).prop('title', data.node.original[self.tree_title_field]);
        });
    },
    reload_content: function () {
        this.records = {};
        this.reload_tree();
        return $.when();
    },
    is_valid: function(){
      return true;
    }
  });

  ActionManager.include({
    select_breadcrumb: function(index, subindex) {
      var self = this;
      var item = this.breadcrumbs[index];
      if (item.widget.views.js_node_tree) {
        item.widget.views.js_node_tree.controller.switch_mode();
      }
      return this._super(index, subindex);
    }
  });

  var JsNodeTreeViewField = FieldMany2Many.extend({
    default_view: 'list',
    init: function() {
        this._super.apply(this, arguments);
        this.x2many_views.list = JsNodeTreeView;
    },
  });

  core.form_widget_registry.add('js_node_tree', JsNodeTreeViewField);
  core.view_registry.add('js_node_tree', JsNodeTreeView);

return {
    JsNodeTreeView: JsNodeTreeView,
    JsNodeTreeViewField: JsNodeTreeViewField,
}

});
