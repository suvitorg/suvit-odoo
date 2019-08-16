# -*- coding: utf-8 -*-
import datetime
import requests
from requests import Session

from xmltodict import parse

from odoo.addons.currency_rate_update import CurrencyGetterInterface
# from odoo.addons.currency_rate_update.model import currency_rate_update


class RU_CBRF_getter(CurrencyGetterInterface):

    code = "RU_CBRF"
    name = "RU CBRF Currency Rates"

    supported_currency_array = [
        "AUD", "AZN", "GBP", "AMD", "BYR", "BGN", "BRL", "HUF", "DKK", "USD",
        "EUR", "INR", "KZT", "CAD", "KGS", "CNY", "LTL", "MDL", "NOK", "PLN",
        "RON", "XDR", "SGD", "TJS", "TRY", "TMT", "UZS", "UAH", "CZK", "SEK",
        "CHF", "ZAR", "KRW", "JPY"]

    session = Session()
    # Не использовать родной UserAgent, потому что cbr.ru не отдает данные для python-requests
    session.headers.update({'user-agent': 'odoo-crb.ru-get/0.0.1'})

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days, date_req=None):
        """implementation of abstract method of Currency_getter_interface"""

        params = {}
        if date_req:
            params['date_req'] = date_req
        else:
            # always set day, CB set rate from yesterday to tommorow
            params['date_req'] = datetime.date.today().strftime('%d/%m/%Y')
        # print('GET cbr', params)
        response = self.session.get('http://www.cbr.ru/scripts/XML_daily.asp',
                                    params=params,
                                    timeout=10)
        response.encoding = 'cp1251'
        # print('after GET cbr')

        rates = {}
        text = response.text.replace('windows-1251', 'utf-8')
        cbr = parse(text)
        for valute in cbr['ValCurs']['Valute']:
            valute['Value'] = float(valute['Value'].replace(',', '.'))
            rates[valute['CharCode']] = valute['Value']

        if main_currency in currency_array:
            currency_array.remove(main_currency)
        main_currency_data = 1
        if main_currency != 'RUB' and main_currency:
            main_currency_data = rates[main_currency]
            rates['RUB'] = 1

        for curr in currency_array:
            self.validate_cur(curr)
            self.updated_currency[curr] = main_currency_data / rates[curr]

        return self.updated_currency, self.log_info