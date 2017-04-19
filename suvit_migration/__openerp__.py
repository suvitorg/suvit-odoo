{
    'name': 'Сувит. Миграции',
    'category': 'Website',
    'summary': 'Миграции',
    'version': '1.0',
    'description': """
Миграции
===========================

* Сохраняемые миграции в базу (аля South)

        """,
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/migrations.xml',
    ],
    'installable': False,
    'auto_install': False,
}
