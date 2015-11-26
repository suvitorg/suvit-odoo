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
        NodeModel.call('write', [node_obj.id, coords]);
        // console.log(coords);
    },

//какой-то костыль, но я не нашел способа сделать лучше.
    find_label: function(r, el) {
        self = this;
        if (r == el) {
            if (el.next && el.next.type == 'text') {
                return el.next;
            }
            return false;
        } else if (r.next) {
            return self.find_label(r.next, el);
        }
        return false;
    },

    draw_diagram: function(result) {
        var self = this;
        this._super(result);
        if (self.graph) {
            _.each(self.graph.get_node_list(), function(n) {
                var fig = n.get_fig();
                fig.drag(null, null, function(){
                    self.save_coords(n);
                });
                node_label = self.find_label(self.graph.r.bottom, fig);
                node_label.drag(null, null, function(){
                  self.save_coords(n);
                });
            });
        }
    }
  });
};
