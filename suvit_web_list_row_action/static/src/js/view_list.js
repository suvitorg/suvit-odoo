odoo.define('suvit.web.list.row.action', function (require) {
  var rpc = require('web.rpc');
  var ListView = require('web.ListView');
  var core = require('web.core');
  var field_registry = require('web.field_registry');
  var FieldMany2Many = field_registry.get('many2many');
  var FieldOne2Many = field_registry.get('one2many');
  var FormController = require('web.FormController');

  var do_action = function(field, ev, context){
    var parent = field.renderer.getParent().getParent().getParent();
    var id = ev.data.id;
    ev.stopPropagation();
    if (typeof id == 'string' && parent.model)
        id = parent.model.localData[id].data.id;
    rpc.query({model: field.field.relation,
               method: 'get_formview_action',
               args: [id],
               context: context,
    }).then(function(action){
      action['target'] = context.open_formview;
      field.do_action(action);
    });
  };

  FieldOne2Many.include({
    _onOpenRecord: function (ev) {
        var context = ev.target.state.context;
        if (context && context.open_formview){
            return do_action(this, ev, context);
        }
        return this._super(ev);
    }
  });

  FieldMany2Many.include({
    _onOpenRecord: function (ev) {
        var context = this.record.getContext(this.recordParams);
        if (context && context.open_formview){
            return do_action(this, ev, context);
        }
        return this._super(ev);
    }
  });

});
