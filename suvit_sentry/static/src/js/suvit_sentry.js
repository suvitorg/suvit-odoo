odoo.define('suvit.sentry', function (require) {

  var core = require('web.core');
  var _t = core._t;

  var Client = require('web.AbstractWebClient')
  var WebClient = require('web.WebClient');
  var CrashManager = require('web.CrashManager');
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');

  Dialog.include({
    open: function() {
      var self = this;
      this._super();
      self.$modal.on('click', '.show_details', function() {
        self.$modal.find('.hide_details').show();
        self.$modal.find('.error_details').show();
        $(this).hide();
      });
      self.$modal.on('click', '.hide_details', function() {
        self.$modal.find('.show_details').show();
        self.$modal.find('.error_details').hide();
        $(this).hide();
      });
      return self;
    }
  });

  Client.include({
    init: function(parent) {
      this._super(parent);
      var self = this;
      rpc.query({
          model: "ir.config_parameter",
          method: 'get_param',
          args: ['SENTRY_CLIENT_JS_DSN'],
      }).then(function(value) {
        if (value) {
          Raven.setUserContext({
            name: self.session.username,
            context: self.session.user_context,
            id: self.session.uid
          });
          Raven.config(value).install();
        }
      });
    }
  });

  WebClient.include({
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
