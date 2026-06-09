from odoo import fields, models


class FacilityEquipment(models.Model):
    _name = "facility.equipment"
    _description = "Facility Equipment"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    description = fields.Text()
