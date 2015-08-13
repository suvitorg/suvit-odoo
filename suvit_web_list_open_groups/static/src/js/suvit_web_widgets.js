openerp.suvit_web_list_open_groups = function(instance, local) {

  var QWeb = instance.web.qweb;

  instance.web.ListView.include({

    open_group: function(group){
      if (group.$row)
        group.$row.click();
    },

    open_children: function(group){
      if (_.isEmpty(group.children))
        return;

      for (var i in group.children) {
        var child = group.children[i];
        this.full_open_group(child);
      };
    },

    full_open_group: function(group){
      this.open_group(group);
      this.open_children(group);
    },

    reload_content: function() {

        this._super();
        var self = this;

        var $menu = self.$pager.find('.oe_view_open_groups_menu');

        if (!$menu.size() && self.grouped) {
          self.$pager.prepend(QWeb.render("ListView.open_groups", self));

          self.$pager.find('.oe_view_open_groups_menu').click(function(){
            self.full_open_group(self.groups);
            $('i.fa', this).toggleClass('fa-plus').toggleClass('fa-minus');
          });
        } else if ($menu.size() && !self.grouped) {
          $menu.remove();
        }

    }
  });

};
