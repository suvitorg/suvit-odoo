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

};
