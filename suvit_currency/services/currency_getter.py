# -*- coding: utf-8 -*-
# some parts getter from https://github.com/barachka/account-financial-tools
from openerp.addons.currency_rate_update.services.currency_getter import Currency_getter_factory, UnknowClassError
from openerp.addons.currency_rate_update.model import currency_rate_update


def register(self, class_name):
    try:
        return Currency_getter_factory.old_register(self, class_name)
    except UnknowClassError:
        if class_name != 'RU_CBRF_getter':
            raise

        from .update_service_RU_CBRF import RU_CBRF_getter
        return RU_CBRF_getter()

Currency_getter_factory.old_register = Currency_getter_factory.register
Currency_getter_factory.register = register

RU_CBRF_supported_currency_array = [
    "AUD", "AZN", "GBP", "AMD", "BYR", "BGN", "BRL", "HUF", "DKK", "USD",
    "EUR", "INR", "KZT", "CAD", "KGS", "CNY", "LTL", "MDL", "NOK", "PLN",
    "RON", "XDR", "SGD", "TJS", "TRY", "TMT", "UZS", "UAH", "CZK", "SEK",
    "CHF", "ZAR", "KRW", "JPY"]

currency_rate_update.supported_currecies.update(
    {'RU_CBRF_getter': RU_CBRF_supported_currency_array}
)
