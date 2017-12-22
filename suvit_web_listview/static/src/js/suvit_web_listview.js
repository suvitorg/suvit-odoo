openerp.suvit_web_listview = function(instance) {
  
  instance.web.ListView.include({
    is_inside_form: function() {
      return this.is_m2m() || this.is_o2m();
    },
    is_m2m: function() {
      return !!this.ViewManager.field_manager;
    },
    is_o2m: function() {
      return !!this.ViewManager.o2m;
    },
    get_id: function() {  //recently called 'get_hide_cols_id'
      var id;
      //ListView id, view_id
      if(!this.is_inside_form())
        id = this.fields_view.view_id;
      //FormView m2m field id, view_id + field name
      if(this.is_m2m())
        id = this.ViewManager.field_manager.fields_view.view_id + '_' + this.ViewManager.field_manager.fields_view.name;
      //FormView o2m field id, view_id + field name
      if(this.is_o2m())
        id = this.ViewManager.o2m.view.fields_view.view_id + '_' + this.ViewManager.o2m.name;
      //console.log('get_id', id);
      return id;
    },
  });
};
