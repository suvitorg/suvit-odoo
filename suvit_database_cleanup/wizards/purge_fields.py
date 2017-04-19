# -*- coding: utf-8 -*-
from openerp import models, fields, api
# from openerp.tools.translate import _
from openerp.addons.base.ir.ir_model import MODULE_UNINSTALL_FLAG


class IrModelField(models.Model):
    _inherit = 'ir.model.fields'

    @api.multi
    def _drop_column(self):
        # Allow to skip this step during field unlink
        # The super method crashes if the field.model cannot be instantiated
        if self.env.context.get('no_drop_column'):
            return True
        return super(IrModelField, self)._drop_column()


class CleanupPurgeLineField(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.field'
    _order = 'model,name'

    wizard_id = fields.Many2one(string=u"Purge Wizard",
                                comodel_name='cleanup.purge.wizard.field',
                                readonly=True)
    model = fields.Char(string=u"Модель")

    @api.multi
    def purge(self):
        Model = self.env['ir.model']
        Field = self.env['ir.model.fields']
        Attachment = self.env['ir.attachment']
        Constraint = self.env['ir.model.constraint']

        for line in self:
            field = Field.search([('model', '=', line.model),
                                  ('name', '=', line.name)],
                                 limit=1)
            if field:
                self.logger.info('Purging field %s', field.id)
                """attachments = Attachment.search([('res_model', '=', line.model),
                                                 ('name', '=', line.name)])\
                                           .unlink()"""
                field.with_context({MODULE_UNINSTALL_FLAG: True,
                                    'no_drop_column': True}).unlink()
                line.write({'purged': True})
        return True


class CleanupPurgeWizardField(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.field'

    name = fields.Char(default=u"Мастер очистки Полей")
    purge_line_ids = fields.One2many(string=u"Поля для удаления",
                                     comodel_name='cleanup.purge.line.field',
                                     inverse_name='wizard_id')

    @api.model
    def find(self):
        """
        Search for fields that cannot be instantiated.
        """
        res = []
        cr = self.env.cr
        cr.execute("SELECT model, name from ir_model_fields")
        for model, name in cr.fetchall():
            Model = self.pool.get(model)
            if not Model or name not in Model._fields:
                res.append((0, 0, {'name': name,
                                   'model': model}))
        if not res:
            raise api.Warning(u"Не найдены Поля для удаления")
        return res
