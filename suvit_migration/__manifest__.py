{
    'name': 'Сувит. Миграции',
    'category': 'Website',
    'summary': 'Миграции',
    'version': '1.0.2',
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
    'installable': True,
    'auto_install': False,
}
