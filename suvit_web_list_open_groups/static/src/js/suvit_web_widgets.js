openerp.suvit_web_list_open_groups = function(instance, local) {

  var QWeb = instance.web.qweb;

  instance.web.ListView.include({

    open_group: function(group, close){
      if (group.$row) {
        if (close) {
          var open_groups = JSON.parse(localStorage.getItem('open_groups') || '{}');
          delete open_groups[this.view_id];
          localStorage["open_groups"] = JSON.stringify(open_groups);
          if (group.$row.data('open'))
            group.$row.trigger('click', [false, true]);
        } else {
          if (!group.$row.data('open'))
            group.$row.trigger('click', [true, false]);
        }
      }
    },

    open_children: function(group, close){
      if (_.isEmpty(group.children))
        return;

      for (var i in group.children) {
        var child = group.children[i];
        this.full_open_group(child, close);
      };
    },

    full_open_group: function(group, close){
      this.open_group(group, close);
      this.open_children(group, close);
    },

    reload_content: function() {
        var tmp = this._super();
        var self = this;

        var $menu = self.$pager.find('.oe_view_open_groups_menu');

        if (!$menu.size() && self.grouped) {
          self.$pager.prepend(QWeb.render("ListView.open_groups", self));

          self.$pager.find('.oe_view_open_groups_menu').click(function(){
            $('i.fa', this).toggleClass('fa-plus').toggleClass('fa-minus');
            $('i.fa', this).hasClass('fa-plus') ? close = true : close = false;
            self.full_open_group(self.groups, close);
          });
        } else if ($menu.size() && !self.grouped) {
          $menu.remove();
        }
        return tmp;
    }
  });

};
