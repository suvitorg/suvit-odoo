odoo.define('suvit_web_list_hide_cols', function (require) {
"use strict";

  var localStorage = window['localStorage'] || {};
  var core = require('web.core');
  var QWeb = core.qweb;
  var ListView = require('web.ListView');

  ListView.include({
    is_inside_form: function() {
      return !!this.x2m;
    },
    get_hide_cols_id: function() {
      var id = this.fields_view.view_id;
      if(this.is_inside_form()){
        id = this.x2m.field_manager.fields_view.view_id + '_' + this.x2m.name;
      }
      return id;
    },
    load_hide_cols: function() {
      var data = localStorage[this.get_hide_cols_id()] || '{}';
      this.hide_cols = JSON.parse(data);
    },
    save_hide_cols: function(data) {
      localStorage[this.get_hide_cols_id()] = JSON.stringify(data || this.hide_cols);
    },
    add_invisible: function(field, is_invisible, save) {
      var modifiers = JSON.parse(field.attrs.modifiers);
      modifiers['tree_invisible'] = is_invisible ? '1' : null;
      field.attrs.modifiers = JSON.stringify(modifiers);
      if (!this.hide_cols) this.hide_cols = [];
      this.hide_cols[field.attrs.name] = is_invisible;
      if (save)
        this.save_hide_cols();
    },
    setup_columns: function (fields, grouped) {
      var self = this;
      this.load_hide_cols();
      _.map(self.fields_view.arch.children, function(field){
          if (self.hide_cols[field.attrs.name] !== undefined ) {
              self.add_invisible(field, self.hide_cols[field.attrs.name]);
          }
      });
      this._super(fields, grouped);
    },
    reload_content: function () {
      var self = this;
      var res = this._super();
      $.when(res).then(function() {

        var $sidebar;
        if(self.is_inside_form() && self.$el.find('.o_list_view')){
          $sidebar = self.ViewManager.$el.find('.o_x2m_control_panel');
        } else {
          if(self.ViewManager && self.ViewManager.action_manager && self.ViewManager.action_manager.main_control_panel)
            $sidebar = self.ViewManager.action_manager.main_control_panel.nodes.$sidebar;
        }

        // TODO 10.0
        // not work when m2m modal popup
        if (!$sidebar){
          return;
        }

        var empty_th = self.$el.find('th[data-id=_empty_col]');
        empty_th.css({'overflow': 'unset'});
        empty_th.append(QWeb.render("ListView.hide_cols", self));

        /*var $menu = $sidebar.find('.oe_view_hide_cols_menu');
        if (!$menu.size()) {
          self.is_inside_form() ? $sidebar.prepend(QWeb.render("ListView.hide_cols", self)) : $sidebar.append(QWeb.render("ListView.hide_cols", self));
        }*/

        if ( $('.oe_view_hide_cols_menu li input:checked').length <= 1 ) {
          $('.oe_view_hide_cols_menu li input:checked').prop('disabled', true);
        } else {
          $('.oe_view_hide_cols_menu li input').prop('disabled', false);
        }
        $('.oe_view_hide_cols_menu li input[data-swichable = "0"]').prop('disabled', true);
        $sidebar.find('.oe_view_hide_cols_menu li input').off('click').on('click',function(event){
          var $checkbox = $(this);
          if ($checkbox.data('swichable') === 0) {
            event.preventDefault();
            return false;
          }
          _.map(self.fields_view.arch.children, function(field){
            if (field.attrs.name == $checkbox.data('field')) {
              self.add_invisible(field, !$checkbox.prop('checked'), true);
            }
          });
          if ($checkbox.data('field') == '_row_no') {
            self.hide_cols['_row_no'] = !$checkbox.prop('checked');
            self.save_hide_cols();
          };
          //To be checked, in Odoo 8 it was necessary to null $pager, otherwise page navigation arrows were not rendered after list reload in form 
          //if(self.is_inside_form())
            //self.$pager = null;
          self.load_list(self.fields_view);
          self.reload();
        });

        if(self.is_inside_form()){
          self.$el.find('button.btn_hide_cols').on('click', function (event) {
            $(event.target).toggleClass('open');
          });
        }
      });
    },
  });
});