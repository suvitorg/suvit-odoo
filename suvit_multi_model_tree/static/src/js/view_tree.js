openerp.suvit_multi_model_tree_old = function(instance, local) {

  /* Ability
     1. to send all node`s parents to server, to can filter children depends on parent
     2. server may response with id with all parents, so extract only last id */
  instance.web.TreeView.include({
    getparents: function(id) {
      /* by default row id is integer server id,
         but we can modify id too support same tree node in different branches,
         so use last integer number in id(example 2-22-2222) */
      var parent_ids = [],
          $parent_row = this.$el.find('[data-id='+ id +']');
      while ($parent_row.length) {
        parent_ids.unshift($parent_row.data('id').toString().split('-').pop());
        $parent_row = this.$el.find('[data-id='+ $parent_row.data('row-parent-id') +']');
      }
      return parent_ids;
    },
    getdata: function (id, children_ids) {
      /********* Send perents in context ********/
      var self = this;
      if (!self.real_context)
        self.real_context = self.dataset._model._context;
      self.dataset._model._context = new instance.web.CompoundContext(self.real_context,
                                                                      {tree_parent_ids: self.getparents(id)});

      return this._super(id, children_ids);
    },
    activate: function(id){
      id = parseInt(id.toString().split('-').pop());
      return this._super(id);
    },
  });

};
