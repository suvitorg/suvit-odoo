[![Build Status](https://travis-ci.org/suvitorg/suvit-odoo.svg?branch=master)](https://travis-ci.org/suvitorg/suvit-odoo)

odoo-модули SUVIT
--------------------------

## Backend

* suvit_base - Базовая часть
    * Удаление регистрации в odoo.com
    * Улучшение mail.thread чтобы мог работать с полями с русскими названиями
* suvit_currency - Модуль для скачивания курса валют с сайта ЦБ + обратные курсы
* suvit_sentry - Интеграция odoo и sentry
* suvit_migration - базовая модель Миграции данных.
* suvit_multi_model_tree - Составления дерева из нескольких разных моделей, соединенных M2O-ключем

## Frontend

* suvit_hotkeys - Горячие клавиши в русской раскладке. Аналоги английских
* suvit_web_diagram - Сохранение позиций вершин в диаграмме
* suvit_web_list_hide_cols - Cкрытие/Показ колонок в списке
* suvit_web_list_open_groups - Быстрое открытие/закрытие всех групп
* suvit_web_list_row_action - Выполнение произвольного действия при клике на строку списка
* suvit_web_notebook_focus - Активация нужного таба во время открытия карточки
* suvit_web_tree - Показ дерева в карточке. Показ вместе Дерева и Списка
* suvit_web_tree_row_action - Удалить. см. suvit_web_list_row_action
* suvit_web_widgets - Виджеты. Показ картинки в списке

Планы
---------------
* suvit_datetime - TODO Модуль для нормальной работы с датами и временем

Переводы
------------------
* suvit_website - TODO перевод модуля website
