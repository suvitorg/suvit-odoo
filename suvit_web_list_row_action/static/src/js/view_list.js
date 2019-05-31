odoo.define('suvit.web.list.row.action', function (require) {

  var field_registry = require('web.field_registry');
  var FieldMany2Many = field_registry.get('many2many');
  var FieldOne2Many = field_registry.get('one2many');
  var framework = require('web.framework');

  var do_block = function () {
    if ($.blockUI) {
        $.blockUI.defaults.overlayCSS["opacity"] = 1;
    }
    framework.blockUI();
  }

  var do_unblock = function () {
    framework.unblockUI();
    if ($.blockUI) {
        $.blockUI.defaults.overlayCSS["opacity"] = 0.6;
    }
  }

  var do_action = function(field, ev, context){
    ev.stopPropagation();

    var controller = field.renderer.getParent().getParent().getParent();
    var act_manager = controller.getParent().action_manager;

    var id = ev.data.id;

    if (context.x2m_pager_disable) {
        if (typeof id == 'string' && controller.model) {
            var rec = controller.model.localData[id];
            var res_id = rec.data.id;
        }
        return field._rpc({model: field.field.relation,
                           method: 'get_formview_action',
                           args: [[res_id]],
                           context: context,
                           })
                           .then(function (action) {
                               console.log('DISABLE ACT', action)
                               field.trigger_up('do_action', {action: action});
                           });
    }

    var parent_rec;
    var res_id = id;
    var res_model = field.field.relation;
    var res_ids = [];

    if (typeof id == 'string' && controller.model) {
        var rec = controller.model.localData[id];
        res_id = rec.data.id;
        parent_rec = controller.model.localData[rec.parentID];
        if (context.open_formview_model && context.open_formview_field && parent_rec._cache) {
            var fname = context.open_formview_field;
            _.each(parent_rec.res_ids, function (res_rec_id) {
                var res_rec = controller.model.localData[parent_rec._cache[res_rec_id]];
                var res_id_val = res_rec.data[fname];
                var dom_res_id = res_id_val;
                if (typeof res_id_val == 'string') {
                    var f_rec = controller.model.localData[res_id_val];
                    dom_res_id = f_rec.data.id;
                }
                if (res_rec_id == res_id)
                    res_id = dom_res_id;
                res_ids.push(dom_res_id);
            });
            res_model = context.open_formview_model;
        } else {
            res_ids = parent_rec.res_ids;
        }
    }

    var act = {
        action_binding_ids:[],
        auto_search:true,
        binding_act_ids:[],
        binding_model_id:false,
        binding_type:"action",
        context:{},
        domain: res_ids ? [['id', 'in', res_ids]] : [],
        filter:false,
        flags:{views_switcher: true,
               search_view: true,
               action_buttons: true,
               sidebar: true,
               pager: true,
               search_disable_custom_filters: undefined,
               search_view: true,
               sidebar: true,
               views_switcher: true},
        groups_id:[],
        limit:80,
        menu_id:null,
        multi:false,
        name:"...",  // TODO maybe need to delete list breadcrumb
        res_id:res_id,
        res_model:res_model,
        search_view_id:false,
        src_model:false,
        target:"current",
        type:"ir.actions.act_window",
        usage:false,
        view_id:false,
        view_ids:[],
        view_mode:"list,form",
        views:[[false, 'list', field.view], [false, 'form']],
    }

    act_manager.do_action(act).then(function(res){
        var view_manager = act_manager.action_stack.slice(-1)[0].widget;
        _.last(view_manager.view_stack).multi_record = false;
        do_block();
        view_manager.switch_mode('form', {mode: controller.mode}).then(function(){
            do_unblock();
        });
    });

  };

  FieldOne2Many.include({
    _onOpenRecord: function (ev) {
        var context = this.record.getContext(this.recordParams);
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
