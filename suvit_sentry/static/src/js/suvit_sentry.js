openerp.suvit_sentry = function(instance, local) {
  $('.show_details').live('click', (function() {
    $('.hide_details').show();
    $('.error_details').show();
    $(this).hide();
  })
  )

  $('.hide_details').live('click', (function() {
    $('.show_details').show();
    $('.error_details').hide();
    $(this).hide();
  })
  )

  var _t = instance.web._t;
  instance.web.Client.include({
    init: function(parent, origin) {
      this._super(parent, origin);
      new instance.web.Model("ir.config_parameter").call("get_param", ['SENTRY_CLIENT_JS_DSN']).then(function(value) {
        if (value) {
          Raven.config(value).install();
        }
      });
    }
  });
  instance.web.CrashManager.include({
    show_error: function(error) {
      if (error.client) {
        try {
          Raven.setUserContext({
            name: instance.session.username,
            context: instance.session.user_context,
            id: instance.session.uid
          });
          Raven.captureException(error.message, {extra: error});
        } catch (e) {}
      }
      if (error.message.indexOf('XmlHttpRequestError') === 0) {
        error.message = 'Связь с сервером потеряна, попробуйте зайти позже';
      }
      return this._super(error);
    },
  });
  instance.web.WebClient.include({
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
    }
  });
};