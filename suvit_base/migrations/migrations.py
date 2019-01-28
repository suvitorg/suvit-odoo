# -*- coding: utf-8 -*-
from odoo import models, api


class Migration(models.Model):
    _inherit = 'suvit.migration'

    @api.model
    def clear_bad_mail_followers(self):
        query = """SELECT DISTINCT res_model FROM mail_followers"""
        self.env.cr.execute(query)
        result = self.env.cr.fetchall()
        for vals in result:
            model = vals[0]
            if model not in self.env:
                query = """DELETE FROM mail_followers
                           WHERE res_model = '%s'"""
            else:
                query = """DELETE FROM mail_followers
                           WHERE res_model = '%s'
                           AND res_id NOT IN (SELECT i.id
                           FROM %s i)""" % (model, self.env[model]._table or model)
            self.env.cr.execute(query)

    @api.model
    def clear_bad_mail_messages(self):
        query = """SELECT DISTINCT model FROM mail_message"""
        self.env.cr.execute(query)
        result = self.env.cr.fetchall()
        for vals in result:
            model = vals[0]
            if model not in self.env:
                query = """DELETE FROM mail_message
                           WHERE model = '%s'"""
            else:
                query = """DELETE FROM mail_message
                           WHERE model = '%s'
                           AND res_id NOT IN (SELECT i.id
                           FROM %s i)""" % (model, self.env[model]._table or model)
            self.env.cr.execute(query)
