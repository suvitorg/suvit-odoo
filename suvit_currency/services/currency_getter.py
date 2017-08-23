# -*- coding: utf-8 -*-
from openerp.addons.currency_rate_update.services.currency_getter import Currency_getter_factory, UnknowClassError

from openerp.addons.currency_rate_update.model import currency_rate_update


class Currency_getter_factory_new(Currency_getter_factory):
    def register(self, class_name):
        print(class_name)
        try:
            return Currency_getter_factory.register(self, class_name)
        except UnknowClassError:
            if class_name == 'RU_CBRF_getter':
                from .update_service_RU_CBRF import RU_CBRF_getter
                return RU_CBRF_getter()
            else:
                raise UnknowClassError


currency_rate_update.Currency_getter_factory = Currency_getter_factory_new

RU_CBRF_supported_currency_array = [
    "AUD", "AZN", "GBP", "AMD", "BYR", "BGN", "BRL", "HUF", "DKK", "USD",
    "EUR", "INR", "KZT", "CAD", "KGS", "CNY", "LTL", "MDL", "NOK", "PLN",
    "RON", "XDR", "SGD", "TJS", "TRY", "TMT", "UZS", "UAH", "CZK", "SEK",
    "CHF", "ZAR", "KRW", "JPY"]

currency_rate_update.supported_currecies.update(
    {'RU_CBRF_getter': RU_CBRF_supported_currency_array}
)
