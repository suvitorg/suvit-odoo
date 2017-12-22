{
    'name': 'Сувит. Открываемые группы',
    'category': 'Web',
    'summary': 'Расширение ListView позволяющее открывать/закрывать все группы',
    'website': 'https://suvit.ru',
    'version': '1.0',
    'description': """
Расширение ListView позволяющее открывать/закрывать все группы
================================================================

        """,
    'author': 'Suvit LLC',
    'depends': ['web',
                'suvit_web_listview',
                # 'format_web_list_group_fix' - Василий объясни зачем нужен
                ],
    'installable': True,
    'auto_install': False,
    'data': [
        'views/web/assets.xml',
    ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
}
