openerp.suvit_web_diagram = function(instance, local) {
  var QWeb = instance.web.qweb;
  instance.web.DiagramView.include({
    init: function(parent, dataset, view_id, options) {
        var self = this;
        window.CuteNodeOrig = window.CuteNode;
        window.CuteNode = function (graph,pos_x, pos_y,label,type,color) {
            node = new CuteNodeOrig(graph,pos_x, pos_y,label,type,color);
            var fig = node.get_fig();
            fig.drag(null, null, function(){
                self.save_coords(node);
            });
            node_label = graph.r.getById(fig.id).next;
            node_label.drag(null, null, function(){
              self.save_coords(node);
            });
            return node;
        }

        this._super(parent, dataset, view_id, options);
    },

    save_coords: function(node_obj){
        var NodeModel = new instance.web.Model(this.node);
        var coords = node_obj.get_pos();
        coords['x'] = coords['x'] - 50;
        coords['y'] = coords['y'] - 50;
        // console.log(coords);
        NodeModel.call('write', [node_obj.id, coords]);
    },

    draw_diagram: function(result) {
        var self = this;
        this._super(result);
        CuteNodeOrig.double_click_callback = function(cutenode){
            self.edit_node(cutenode.id);
        };
        CuteNodeOrig.destruction_callback = function(cutenode){
            if(!confirm(_t("Deleting this node cannot be undone.\nIt will also delete all connected transitions.\n\nAre you sure ?"))){
                return $.Deferred().reject().promise();
            }
            return new instance.web.DataSet(self,self.node).unlink([cutenode.id]);
        };
    }
  });
};
