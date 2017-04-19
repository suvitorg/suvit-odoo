{
    'name': 'Сувит. TreeView. Расширения',
    'category': 'Website',
    'summary': 'TreeView. Расширения',
    'version': '1.0',
    'description': """
TreeView. Расширения
===========================

* Позволяет использовать TreeView и ListView у одного ViewManager
* Добавляет в context всех родителей при открытии узла дерева

        """,
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'web',
    ],
    'data': [
        'static/data/static_data.xml',
    ],
    'js': [
        "static/src/js/view_tree.js",
    ],
    'installable': False,
    'auto_install': False,
}
