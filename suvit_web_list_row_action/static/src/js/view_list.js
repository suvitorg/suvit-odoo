openerp.suvit_web_list_row_action = function(instance, local) {

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

  instance.web.ListView.List.include({

    row_clicked: function (event, view) {
        var field = this.view.o2m || this.view.m2m_field;
        if (!field)
          return this._super.apply(this, arguments);

        var parent_view = this.dataset.parent_view;
        var actual_mode = (parent_view ? parent_view.get("actual_mode") : 'view');
        if (actual_mode != 'view')
          return this._super.apply(this, arguments);

        var context = field.build_context().eval();
        if (!context || !context.open_formview)
          return this._super.apply(this, arguments);

        $(this).trigger(
          'row_link',
          [this.dataset.ids[this.dataset.index],
           this.dataset, view]);
        },
    });

};
