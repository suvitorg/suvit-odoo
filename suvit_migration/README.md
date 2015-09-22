suvit_migrations
===========

Создание миграций
-----------------------------------------

1. Расширяем модель suvit.migration и добавляем метод, который выполнит миграцию данных:

    class Migration(models.Model):
        _inherit = 'suvit.migration'

        @api.model
        def test_migration(self):
            # code of migration

2. Создаем экземляр миграции с указанием метода, который нужно запустить:

    <record model="suvit.migration" id="test_migration">
        <field name="name">Тест</field>
        <field name="description">Тест</field>
        <field name="method">test_migration</field>
    </record>

3. При создании миграция выполнится автоматически.

4. В пункте меню Миграции лежит весь список миграций. Чтобы запустить миграцию повторно, нужно снять галку "Выполнено".

5. При нажатии меню "Мигрировать" запускаются все "Не выполненные" миграции.
