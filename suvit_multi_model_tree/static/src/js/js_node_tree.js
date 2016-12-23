openerp.suvit_multi_model_tree = function (instance, local) {
  openerp.suvit_multi_model_tree_old(instance, local)

  var QWeb = instance.web.qweb;
  var _t = instance.web._t;
  instance.web.views.add('js_node_tree', 'instance.web.JsNodeTreeView');

  var process_model = false;
  var document_model = false;
  var field_model = false;
  config_model = new instance.web.Model("ir.config_parameter");
  config_model.call("get_param", ['PROCESS_MODEL']).then(function(value) {
    process_model = value || "format.frontend.demo.process";
  });
  config_model.call("get_param", ['DOCUMENT_MODEL']).then(function(value) {
    document_model = value || "format.frontend.demo.process.document";
  });
  config_model.call("get_param", ['FIELD_MODEL']).then(function(value) {
    field_model = value || "format.frontend.demo.process.document.field";
  });

  instance.web.FormView.include({
    on_button_save: function(e) {
      var self = this;
      return self._super(e).then(function(){
          if (self.ViewManager.views.js_tree)
            self.ViewManager.views.js_tree.controller.switch_mode();
      });
    },
    on_button_create: function() {
      var self = this;
      self._super();
      if (self.ViewManager.views.js_tree)
        self.ViewManager.views.js_tree.controller.switch_mode();
    }
  });

  instance.web.ActionManager.include({
    select_breadcrumb: function(index, subindex) {
      var self = this;
      var item = this.breadcrumbs[index];
      if (item.widget.views.js_tree) {
        item.widget.views.js_tree.controller.switch_mode();
      }
      return this._super(index, subindex);
    }
  });

  instance.web.JsNodeTreeView = instance.web.View.extend({
    view_type: 'js_node_tree',
    destroy: function () {
      this.$jstree.jstree('destroy');
      this._super();
    },
    init: function (parent, dataset, view_id, options) {
      this._super(parent, dataset, view_id, options);

      if (parent.action && parent.action.context.tree_domain){
        var domain = new instance.web.CompoundDomain(dataset.domain,
                                                     parent.action.context.tree_domain);
        this.dataset.domain = domain;
        this.dataset._model._domain = domain;
      }
      // save init domain
      this.domain = this.dataset.domain;

      this.model = this.dataset.model;
      this.view_id = view_id;

      this.records = {};
      this.options = _.extend({}, this.defaults, options || {});
    },
    switch_mode: function(opt){
      this.reload_tree(opt);
    },
    view_loading: function (r) {
      this.reload_tree();
    },
    do_search: function(domain, context, group_by) {
      // console.log('JSTree.do_search', arguments);
      this.dataset.domain = new instance.web.CompoundDomain(this.domain,
                                                            domain);
      this.dataset._model._domain = this.dataset.domain;
      this.reload_tree();
    },
    reload_tree: function(opt){
      this.$el.empty();
      this.records = {};
      this.load_tree(opt);
      // if (!this.options.nodrag) this.$el.append(this.$dragging_option);
      $('.dragging_option').remove();
      if (!this.options.nodrag) this.ViewManager.$el.find('.oe_view_title').after(this.$dragging_option);
      this.$el.append(this.$jstree);
    },
    load_tree: function (dragging_on) {
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

      self.tree_config = {}
      if (this.fields_view.arch.attrs.tree_dynamic_config)
          self.dataset._model
             .call('get_tree_config', [], {'context': self.dataset.get_context()})
             .then(function(result){
                  _.extend(self.tree_config, result || {});
          })
      else {
        self.tree_config = this.fields_view.arch.attrs.tree_config ? instance.web.py_eval(this.fields_view.arch.attrs.tree_config) : {};

        _.each(self.tree_config, function(element, name){
          _.each(element.create, function(child){
            if (child.model)
              self.tree_config[name]['valid_children'].push(child.model);
          });
        });
      }

      this.fields_view.fields[self.tree_type_field] = {};
      this.fields_view.fields[self.tree_title_field] = {};
      this.fields_view.fields[self.field_parent] = {};
      if (self.tree_type_field) {
          this.fields_view.fields[self.tree_type_field] = {};
      }

      // console.log('JSTree.load', Object.keys(this.fields_view.fields));

      this.tree_fields_cols = [{'header': this.fields_view.arch.attrs.tree_title || 'Структура'}];
      /*_.each(_.difference(_.keys(this.fields_view.fields),
                          ["tree_name", "icon", "tree_child_ids", "tree_obj_real_id", "tree_type", self.field_parent, "row_empty"]), function(col){
        self.tree_fields_cols.push({
          'header': col,
          'value': function (node) {
            return node.original[col];
          }
        });
      });*/
      _.each(this.fields_view.arch.children, function(col){
        if (col.tag == 'field' && !col.attrs.invisible){
            self.tree_fields_cols.push({
              'header': self.fields_view.fields[col.attrs.name]['string'],
              'value': function (node) {
                return node.original[col.attrs.name];
              }
            });
        }
      });

      // XXX remove
      ids = _.uniq(_.filter(this.dataset.ids, function(i){
        if (!isNaN(i) && typeof i != "string") {
          return true;
        }
      }));
      this.dataset.alter_ids(ids);

      self.jstree_load();
    },
    load_records: function (records) {
      var self = this;
          // TODO check
          self.new_records = [];

      _(records).each(function (record) {
          //console.log('record', record);
          self.records[record.id] = record;
          self.new_records.push(record);

          icon_src = record[self.tree_icon_field] || 'STOCK_FILE';
          if (!/\//.test(icon_src)) {
              icon_src = '/web/static/src/img/icons/' + icon_src + '.png';
          } else {
              icon_src = icon_src;
          }

          record.text = record[self.tree_name_field];
          record.type = record[self.tree_type_field] || self.model;
          record.tree_type = record.type;
          record.icon = icon_src;
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
      var ctx = instance.web.pyeval.eval(
          'context', new instance.web.CompoundContext(
              self.dataset.get_context(), local_context));

      return self.rpc('/web/treeview/action', {
          id: id,
          model: self.dataset.model,
          context: ctx
      }).then(function (actions) {
          if (!actions.length) { return; }
          var action = actions[0][2];
          var c = new instance.web.CompoundContext(local_context).set_eval_context(ctx);
          if (action.context) {
              c.add(action.context);
          }
          action.context = c;
          return self.do_action(action);
      });
    },
    do_show: function (options) {
      this._super(options);
    },
    build_context: function () {
      return self.dataset.get_context();
    },
    do_create_record: function (form_view, element, context) {
      var self = this;
      var pop = new instance.web.form.SelectCreatePopup(this);
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
          new instance.web.CompoundDomain(domain),
          new instance.web.CompoundContext(form_view.dataset.context, context)
      );
      pop.on('closed', self, function(){
        self.reload_tree(self.$dragging.is(':checked'));
      });
    },
    do_add_record: function (listView, $node, element, domen) {
        var self = this;
        var pop = new instance.web.form.SelectCreatePopup(listView);
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
            new instance.web.CompoundDomain(result_domain),
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
            new instance.web.Model($node.type).call('write', [
                [parseInt($node.original.tree_obj_real_id)],
                vals
            ]).then(function(){
              self.reload_tree(self.$dragging.is(':checked'));
            });
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

      var dataset = new instance.web.form.One2ManyDataSet(self, self.dataset.model);
      dataset.o2m = self;
      var One2ManyFormView = new instance.web.form.One2ManyFormView(self, dataset, false, {});

      self.do_create_record(One2ManyFormView, element, context);
    },
    jstree_contextmenu_join: function(data){
      var self = this;
      var element = data.item.config;
      var my_model = self.dataset.model;
      var dataset = new instance.web.form.Many2ManyDataSet(self, my_model);
      dataset.m2m = self;
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

      var ctx = new instance.web.CompoundContext(self.dataset.get_context(),
                                                 {'new_parent': self.get_id(obj.parent)}
                                                 );

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
        submenu = {};
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
            var ctx = new instance.web.CompoundContext(self.dataset.get_context(), local_context);

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
            var ctx = new instance.web.CompoundContext(self.dataset.get_context(), local_context);

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
        var ctx = new instance.web.CompoundContext(self.dataset.get_context(), local_context);
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
        this.dataset.read_slice(this.fields_view.fields).done(function(records) {
          self.load_records(records);
          cb.call(this, self.new_records);
        });
      } else {
        var childs = self.records[obj.id][self.field_parent];
        var parents = obj.id.toString().split('-');
        // console.log('check parents', obj.id, parents);
        self.dataset.read_ids(childs,
                              Object.keys(self.fields_view.fields),
                              {context: {"tree_parent_ids": parents}}
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
      console.log('change_parent', this, data);
      var local_context = {
        'old_parent': data.old_parent,
        'old_parent_id': self.get_id(data.old_parent),
        'old_position': data.old_position,
        'new_parent': data.parent,
        'new_parent_id': self.get_id(data.parent),
        'new_position': data.position,
      };
      var ctx = new instance.web.CompoundContext(self.dataset.get_context(), local_context);
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
    }
  });

  local.JsNodeTreeViewField = instance.web.form.FieldMany2Many.extend({
    render_value: function() {
      tmp_opt = this.node.attrs;
      tmp_opt.nodrag = true;
      this.jstree = new instance.web.JsNodeTreeView(this, this.dataset, false, tmp_opt);
      this.$el.empty();
      this.jstree.appendTo(this.$el);
      return this._super();
    }
  });

  instance.web.form.widgets.add('js_node_tree', 'instance.suvit_multi_model_tree.JsNodeTreeViewField');
};
