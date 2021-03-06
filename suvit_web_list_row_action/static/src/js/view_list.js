odoo.define('suvit.web.list.row.action', function (require) {
  var Model = require('web.DataModel');
  var ListView = require('web.ListView');
  var core = require('web.core');

  var One2ManyListView = core.one2many_view_registry.get('list');
  // TODO many2many
  //var FieldMany2Many = core.form_widget_registry.get('many2many');
  //var Many2ManyListView = new FieldMany2Many(field_manager, node).x2many_views.list;

  var do_action = function(view, id, context){
    var model_obj = new Model(view.dataset.model);
    model_obj.call('get_formview_action', [id], {'context': context}).then(function(action){
      action['target'] = context.open_formview;
      view.do_action(action);
    });
  };

  var x2m_do_activate_record = function(index, id) {
    var context = this.x2m.build_context().eval();
    if (!context || !context.open_formview)
      return this._super(index, id);
    do_action(this, id, context);
  };

  ListView.include({
    do_activate_record: function (index, id, dataset, view) {
        var action = this.ViewManager.action;
        if (!action || !action.context || !action.context.open_formview)
          return this._super(index, id, dataset, view);
        do_action(this, id, action.context);
    }
  });

  One2ManyListView.include({
    do_activate_record: x2m_do_activate_record,
  });

  /*Many2ManyListView.include({
    do_activate_record: x2m_do_activate_record,
  });*/

});
