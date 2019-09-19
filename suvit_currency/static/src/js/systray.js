odoo.define('format.web.systray', function (require) {
"use strict";

var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');


require('mail.systray');

var CurrencyRateMenu = Widget.extend({
    template:'CurrencyRateMenu',
    start: function () {
        this._getCurrencyRateData();
        return this._super();
    },
    _getCurrencyRateData: function(){
        var self = this;

        return self._rpc({
            model: 'res.currency.rate',
            method: 'search_read',
            context: session.user_context,
            fields: ['rub_currency_rate'],
            domain: [['currency_id.name', '=', 'EUR']],
            limit: 1,
        }).then(function (data) {
            var rate = data && data[0].rub_currency_rate;
            if (rate) {
                self.$('.o_currency_rate').text(rate.toFixed(2));
            } else {
                self.destroy();
            }

        });
    },

});

SystrayMenu.Items.push(CurrencyRateMenu);

return {
    CurrencyRateMenu: CurrencyRateMenu,
};
});
