from odoo import fields, models


class FacilityRoom(models.Model):
    _name = "facility.room"
    _description = "Facility Room"
    _order = "site_id, name"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    site_id = fields.Many2one(
        "facility.site", string="Site", required=True, ondelete="restrict")
    capacity = fields.Integer(default=0)
    equipment_ids = fields.Many2many("facility.equipment", string="Equipment")
    description = fields.Text()
    booking_ids = fields.One2many(
        "facility.booking", "room_id", string="Bookings")
