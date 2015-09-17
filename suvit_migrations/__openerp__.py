{
    'name': 'Сувит. Миграции',
    'category': 'Website',
    'summary': 'Миграции',
    'version': '1.0',
    'description': """
Миграции
===========================

        """,
    'author': 'Suvit LLC',
    'depends': [
        'base',
    ],
    'data': [
        'views/migration.xml',

        'migrations/data/0000_test.xml',
    ],
    'installable': True,
    'auto_install': False,
}
