{
    'name': 'Сувит. Открываемые группы',
    'category': 'Web',
    'summary': 'Расширение ListView позволяющее открывать/закрывать все группы',
    'website': 'http://suvit.ru',
    'version': '1.0',
    'description': """
Расширение ListView позволяющее открывать/закрывать все группы
================================================================

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
