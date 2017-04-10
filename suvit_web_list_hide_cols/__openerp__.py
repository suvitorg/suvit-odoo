{
    'name': 'Сувит. Скрываемые колонки',
    'category': 'Web',
    'summary': 'Расширение ListView позволяющие скрыть колонки',
    'websites': 'http://suvit.ru',
    'version': '1.0',
    'description': """
Расширение ListView позволяющие скрыть колонки
================================================

        """,
    'author': 'Suvit LLC',
    'depends': ['web'],
    'installable': True,
    'auto_install': False,
    'data': [
        'views/web/assets.xml',
    ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
}
