odoo.define('suvit.web.list.open.groups', function (require) {
  "use strict";
  return;
  // TODO remove, moved to format-frontend module format_web_list_group_fix

  var ListView = require('web.ListView');
  var core = require('web.core');
  var QWeb = core.qweb;

  ListView.include({
    open_group: function(group, close){
      if (group.$row) {
        group.$row.click()
      }
    },
    open_children: function(group, close){
      var self = this;
      _.each(group.children, function(child) {
        self.full_open_group(child, close);
      });
    },
    full_open_group: function(group, close){
      this.open_group(group, close);
      this.open_children(group, close);
    },
    render_sidebar: function($node) {
        var self = this;
        this._super($node);
        if (!self.sidebar)
          return;

        var parent = self.sidebar.$el.parent();
        var tmpl = QWeb.render("ListView.open_groups", self);
        parent.append(tmpl);

        var btn = parent.find('> .oe_view_open_groups_menu');
        btn.click(function(){
          var icon = $(this).find('i.fa');
          icon.toggleClass('fa-plus').toggleClass('fa-minus');
          var close = icon.hasClass('fa-plus');
          self.full_open_group(self.groups, close);

          var open_groups = JSON.parse(localStorage.getItem('open_groups_all') || '{}');
          open_groups[this.view_id] = !close;
          localStorage['open_groups_all'] = JSON.stringify(open_groups);
        });
    },
    reload_content: function () {
      var self = this;
      var res = this._super();
      $.when(res).then(function() {
        if (JSON.parse(localStorage.getItem('open_groups_all') || '{}')[this.view_id]){
            setTimeout(function() {
              self.sidebar.$el.parent().find('> .oe_view_open_groups_menu i.fa').click();
            }, 1);
        }
      });
    },
  });

});
