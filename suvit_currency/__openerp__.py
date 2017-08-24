# -*- coding: utf-8 -*-
{
    'name': 'Сувит. Валюта',
    'version': '0.0.1',
    'category': 'Suvit',
    'complexity': 'easy',
    'description': """
* Установка рубля валютой по умолчанию
* Добавление ЦБ РФ к местам получения курсов валют
* Автообновление курсов валют с сайта ЦБ РФ
* Возможность получить все курсы с начала года
* Показ обратных курсов к рублю, например 76руб - 1 евро
* Уведомление админа, если курс не получался более 3 дней
    """,
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'currency_rate_update',  # github/OCA/account-financial-tools
    ],
    'init': [
    ],
    'data': [
        'data/cron.xml',

        'views/currency.xml',

        'views/fix_account_menu.xml',

        'migrations/data/0001_currency_rate_update.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': ['requests',
                   'xmltodict',
                   ],
    }
}
