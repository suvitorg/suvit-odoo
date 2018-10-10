odoo.define('suvit.sentry', function (require) {

  var core = require('web.core');
  var _t = core._t;

  var Client = require('web.AbstractWebClient')
  var WebClient = require('web.WebClient');
  var CrashManager = require('web.CrashManager');
  var Model = require('web.Model');
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
      new Model("ir.config_parameter").call("get_param", ['SENTRY_CLIENT_JS_DSN']).then(function(value) {
        if (value) {
          Raven.config(value).install();
        }
      });
    }
  });

  WebClient.include({
    show_common: function() {
      var self = this;
      this._super();
      window.onerror = function (message, file, line) {
          self.crashmanager.show_error({
              type: _t("Client Error"),
              message: message,
              data: {debug: file + ':' + line},
              client: true
          });
      };
    },
  });

  CrashManager.include({
    show_error: function(error) {
      if (error.client) {
        try {
          Raven.setUserContext({
            name: instance.session.username,
            context: instance.session.user_context,
            id: instance.session.uid
          });
          Raven.captureException(error.message, {extra: error});
          error.last_code = Raven.lastEventId();
        } catch (e) {}
      }
      if (error.message.indexOf('XmlHttpRequestError') === 0) {
        error.lost_network = true;
        error.message = 'Связь с сервером потеряна, попробуйте зайти позже';
      }
      return this._super(error);
    },
  });

});
