openerp.suvit_web_diagram = function(instance, local) {
  var QWeb = instance.web.qweb;
  instance.web.DiagramView.include({
    init: function(parent, dataset, view_id, options) {
        var self = this;
        window.CuteGraphOrig = window.CuteGraph;
        window.CuteGraph = function (r,style,parentNode) {
            self.graph = new CuteGraphOrig(r,style,parentNode);
            return self.graph;
        }
        window.CuteGraph.wordwrap = window.CuteGraphOrig.wordwrap;
        this._super(parent, dataset, view_id, options);
    },

    save_coords: function(node_obj){
        var NodeModel = new instance.web.Model(this.node);
        var coords = node_obj.get_pos();
        coords['x'] = coords['x'] - 50;
        coords['y'] = coords['y'] - 50;
        // NodeModel.call('write', [node_obj.id, coords]);
        console.log(coords);
    },

    draw_diagram: function(result) {
        var self = this;
        this._super(result);
        _.each(self.graph.get_node_list(), function(n) {
            var fig = n.get_fig();
            fig.drag(null, null, function(){
                self.save_coords(n);
            });
            node_label = self.graph.r.getById(fig.id).next;
            node_label.drag(null, null, function(){
              self.save_coords(n);
            });
        });
    }
  });
};
