openerp.suvit_web_list_hide_cols = function(instance, local) {
  var localStorage = window['localStorage'] || {},
      QWeb = instance.web.qweb;

  instance.web.ListView.include({
    is_inside_form: function() {
      if(this.is_m2m() || this.is_o2m()) {
        return true;
      }
    },
    is_m2m: function() {
      if(this.ViewManager.field_manager)
        return true;
    },
    is_o2m: function() {
      if(this.ViewManager.o2m)
        return true;
    },
    get_hide_cols_id: function() {
      var id = this.fields_view.view_id;
      if(this.is_m2m()){
        id = this.ViewManager.field_manager.fields_view.view_id + '_' + this.ViewManager.field_manager.fields_view.name;
      }
      if(this.is_o2m()){
        id = this.ViewManager.o2m.view.fields_view.view_id + '_' + this.ViewManager.o2m.name;
      }
      return id;
    },
    load_hide_cols: function() {
      var data = localStorage[this.get_hide_cols_id()] || '{}';
      this.hide_cols = JSON.parse(data);
    },
    save_hide_cols: function(data) {
      var ddd = this.get_hide_cols_id();
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
    load_list: function(data) {
      var self = this;
      this._super(data);
      var list_sidebar = false;
      if(this.is_inside_form() && this.$el.find('.oe_field_editable')) {
        this.$el.find('.oe_list_header_columns').before('<div class="preheader_wrap"></div>');
        list_sidebar = this.$el.find('.oe_list_sidebar');
      }
      list_sidebar = list_sidebar.length ? list_sidebar : this.$el.find('.preheader_wrap');        
      
      var $sidebar = this.is_inside_form() ? list_sidebar : $('.oe_sidebar');
      var $menu = $sidebar.find('.oe_view_hide_cols_menu');
      
      if (!$menu.size()) {
        $sidebar.append(QWeb.render("ListView.hide_cols", this));
        $menu = $sidebar.find('.oe_view_hide_cols_menu');
      }

      if ( $('.oe_view_hide_cols_menu li input:checked').length <= 1 ) {
        $('.oe_view_hide_cols_menu li input:checked').prop('disabled', true);
      } else {
        $('.oe_view_hide_cols_menu li input').prop('disabled', false);
      }
      $('.oe_view_hide_cols_menu li input[data-swichable = "0"]').prop('disabled', true);
      var selector = this.is_inside_form() ? this.$el.find('.oe_view_hide_cols_menu li input') : $('.oe_view_hide_cols_menu li input');
      selector.off('click').on('click',function(event){
        $checkbox = $(this);
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
        if(self.is_inside_form())
          self.$pager = null;
        self.load_list(self.fields_view);
        self.reload();
      });

      if(this.is_inside_form())
        $menu.addClass('oe_left')
      else
        $menu.css({"text-align": "center", "vertical-align": "top", "margin-top": "1px"});

      if(this.is_inside_form()){
        this.$el.find('button.btn_hide_cols').on('click', function (event) {
          $menu.toggleClass('open');
        });
      }
    }
  });
};
