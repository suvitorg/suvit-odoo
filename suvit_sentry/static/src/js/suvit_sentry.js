odoo.define('suvit.sentry', function (require) {

  var core = require('web.core');
  var _t = core._t;

  var AbstractWebClient = require('web.AbstractWebClient')
  var WebClient = require('web.WebClient');
  var CrashManager = require('web.CrashManager');
  var rpc = require('web.rpc');
  var session = require('web.session');

  AbstractWebClient.include({
    init: function(parent) {
      this._super(parent);
      var self = this;
      rpc.query({
          model: "ir.config_parameter",
          method: 'get_param_sentry_client_js_dsn',
      }).then(function(value) {
        if (value) {
          Raven.setUserContext({
            name: session.username,
            context: session.user_context,
            id: session.uid
          });
          Raven.config(value).install();
        }
      });
    },
    bind_events: function() {
        this._super();
        var onerror_func = window.onerror
        window.onerror = function (message, file, line, col, error) {
          if (!window.onOriginError)
            Raven.captureException(error);
          onerror_func(message, file, line, col, error);
        };
    }
  });

});
