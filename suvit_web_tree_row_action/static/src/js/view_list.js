openerp.suvit_web_tree_row_action = function(instance, local) {

  var QWeb = instance.web.qweb;


  instance.web.ListView.include({

    do_activate_record: function (index, id, dataset, view) {
        var self = this;
        var model_obj = new instance.web.Model(dataset.model);
        model_obj.call('get_formview_action', [id]).then(function(action){
          self.do_action(action);
        });
    },

  });

  var do_action = function(view, id){
    var model_obj = new instance.web.Model(view.dataset.model);
    model_obj.call('get_formview_action', [id]).then(function(action){
      action['target'] = view.ViewManager.field.context.open_formview;
      view.do_action(action);
    });
  };

  instance.web.form.Many2ManyListView.include({

    do_activate_record: function (index, id) {
        var context = this.ViewManager.field.context;
        if (!context.open_formview)
          return this._super(index, id);

        do_action(this, id);
    }

  });

  instance.web.form.One2ManyListView.include({

    do_activate_record: function(index, id) {
      var context = this.ViewManager.field.context;
        if (!context.open_formview)
          return this._super(index, id);

        do_action(this, id);
    }

  });

};
