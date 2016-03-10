{
    'name': 'Сувит. Клик на строку Списка',
    'category': 'Website',
    'summary': 'Клик на строку Списка',
    'version': '1.0',
    'description': """
Клик на строку Списка
===========================

        """,
    'author': 'Suvit LLC',
    'website': 'http://suvit.ru',
    'depends': [
        'web',
        'suvit_web_list_row_action',
    ],
    'data': [
        'static/data/static_data.xml',
    ],
    'js': [
        "static/src/js/view_list.js",
    ],
    'installable': True,
    'auto_install': False,
}
