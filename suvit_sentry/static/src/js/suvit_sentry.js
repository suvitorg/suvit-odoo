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
          Sentry.init({
            dsn: value,
            beforeSend: function(event, hint) {
              // Нужно тестирование
              return;

              if (event.exception) {
                Sentry.showReportDialog({eventId: event.event_id,
                                         user: {
                                           name: session.name,
                                           email: session.username
                                         },
                                         lang: 'ru',
                                         title: 'Произошла ошибка',
                                         subtitle: 'Мы уже работаем над ее исправлением.',
                                         subtitle2: 'Опишите Ваши действия, эта информация поможет нам.',
                                         labelName: 'ФИО',
                                         labelComments: 'Опишите ошибку',
                                         labelClose: 'Закрыть',
                                         labelSubmit: 'Отправить',
                                         successMessage: 'Ваш отчет отправлен. Спасибо!',
                                         });
              }
              return event;
            },
          });
          Sentry.setUser({username: session.username,
                          name: session.name,
                          id: session.uid,
                          context: session.user_context,
                          });
        }
      });
    },
    bind_events: function() {
        this._super();
        var onerror_func = window.onerror
        window.onerror = function (message, file, line, col, error) {
          if (!window.onOriginError)
            Sentry.captureException(error);
          onerror_func(message, file, line, col, error);
        };
    }
  });

});
