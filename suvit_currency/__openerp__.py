# -*- coding: utf-8 -*-
{
    'name': 'Сувит. Валюта',
    'version': '0.0.1',
    'category': 'Suvit',
    'complexity': 'easy',
    'description': """

* Установка рубля валютой по умолчанию
* Автообновление курсов валют с сайта ЦБ РФ
* Показ обратных курсов к рублю, например 76руб - 1 евро

    """,
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'currency_rate_update',  # from barachka with RusCB support
    ],
    'init': [
    ],
    'data': [
        'views/currency.xml',

        'views/fix_account_menu.xml',

        'migrations/data/0001_currency_rate_update.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': False,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': ['xmltodict'],
    }
}
