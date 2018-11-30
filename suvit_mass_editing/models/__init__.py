from . import mass_object

# Patch
from odoo.addons.mass_editing.models import ir_model_fields


def fixed_list(ids_str):
    return any(id_str.isdigit() for id_str in ids_str.split(','))

# XXX fixed ugly error in mass_editing field.search method
ir_model_fields.list = fixed_list


