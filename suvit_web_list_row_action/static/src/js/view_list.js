openerp.suvit_web_list_row_action = function(instance, local) {
  //TODO odoo10.0
  return;

  var QWeb = instance.web.qweb;


  var do_action = function(view, id, context){
    var model_obj = new instance.web.Model(view.dataset.model);
    model_obj.call('get_formview_action', [id], {'context':context}).then(function(action){
      action['target'] = context.open_formview_target || 'current';
      view.do_action(action);
    });
  };

  instance.web.ListView.include({

    do_activate_record: function (index, id, dataset, view) {
        var action = this.ViewManager.action;
        if (!action)
          return this._super(index, id, dataset, view);

        var context = action.context;
        if (!context || !context.open_formview)
          return this._super(index, id, dataset, view);

        do_action(this, id, context);
    }

  });

  instance.web.form.Many2ManyListView.include({

    do_activate_record: function (index, id) {
        var context = this.m2m_field.build_context().eval();
        if (!context || !context.open_formview)
          return this._super(index, id);

        do_action(this, id, context);
    }

  });

  instance.web.form.One2ManyListView.include({

    do_activate_record: function(index, id) {
        var context = this.o2m.build_context().eval();
        if (!context || !context.open_formview)
          return this._super(index, id);

        do_action(this, id, context);
    }

  });

};
