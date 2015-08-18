openerp.suvit_web_tree = function(instance, local) {

  instance.web.TreeView.include({

    init: function (parent, dataset, view_id, options) {

        if (parent.action && parent.action.context.tree_domain){
          var domain = new instance.web.CompoundDomain(dataset.domain, parent.action.context.tree_domain);
          dataset = new instance.web.DataSetSearch(this, parent.action.res_model, dataset.context, domain);
        }

        this._super(parent, dataset, view_id, options);
    }

  });

};
