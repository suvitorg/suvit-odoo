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
    var rec;
    var parent_rec;

    if (typeof id == 'string' && controller.model) {
        rec = controller.model.localData[id];
        parent_rec = controller.model.localData[rec.parentID];
        id = rec.data.id;
    }

    var act = {
        action_binding_ids:[],
        auto_search:true,
        binding_act_ids:[],
        binding_model_id:false,
        binding_type:"action",
        context:context,
        domain: parent_rec ? [['id', 'in', parent_rec.res_ids]] : [],
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
        res_id:id,
        res_model:field.field.relation,
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
