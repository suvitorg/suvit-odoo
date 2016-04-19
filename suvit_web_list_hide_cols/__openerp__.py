{
    'name': 'Сувит. Скрываемые колонки',
    'category': 'Web',
    'summary': 'Расширение ListView позволяющие скрыть колонки',
    'website': 'http://suvit.ru',
    'version': '1.0',
    'description': """
Расширение ListView позволяющие скрыть колонки
================================================

        """,
    'author': 'Suvit LLC',
    'depends': ['web',
                'web_tree_dynamic_colored_field'],
    'installable': True,
    'auto_install': False,
    'data': [
        'views/web/assets.xml',
    ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
}
