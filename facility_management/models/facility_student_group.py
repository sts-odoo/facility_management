from odoo import api, fields, models


class FacilityStudentGroup(models.Model):
    """A student group (cohort), e.g. "EPL11".

    Bookings target one or more groups; the group is the unit the scheduling
    and conflict-detection layers reason about.
    """

    _name = "facility.student.group"
    _description = "Student Group"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    member_ids = fields.Many2many("res.partner", string="Members")
    member_count = fields.Integer(compute="_compute_member_count")

    @api.depends("member_ids")
    def _compute_member_count(self):
        for group in self:
            group.member_count = len(group.member_ids)
