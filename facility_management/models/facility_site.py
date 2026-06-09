from odoo import api, fields, models


class FacilitySite(models.Model):
    _name = "facility.site"
    _description = "Facility Site"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one("res.partner", string="Address")
    country_id = fields.Many2one("res.country", string="Country")
    # Geographic coordinates of the site (for distance computations and maps).
    latitude = fields.Float(digits=(10, 7))
    longitude = fields.Float(digits=(10, 7))
    room_ids = fields.One2many("facility.room", "site_id", string="Rooms")
    room_count = fields.Integer(compute="_compute_room_count")

    @api.depends("room_ids")
    def _compute_room_count(self):
        for site in self:
            site.room_count = len(site.room_ids)
