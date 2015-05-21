openerp.suvit_web_widgets = function(instance, local) {

instance.web.ListView.include({
    load_list: function(data) {
        var self = this;
        this._super(data);

        this.$el.find('.oe_view_list_menu li input').click(function(){
            checkbox = $(this);
            _.map(self.fields_view.arch.children, function(field){
                if (field.attrs.name == checkbox.data('field')) {
                    var modifiers = JSON.parse(field.attrs.modifiers);
                    modifiers['tree_invisible'] = !checkbox.prop('checked')? '1': null;
                    field.attrs.modifiers = JSON.stringify(modifiers);
                }
            });
            self.load_list(self.fields_view);
            self.reload();
        });
    }
});
};
