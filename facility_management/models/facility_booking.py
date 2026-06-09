import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FacilityBooking(models.Model):
    _name = "facility.booking"
    _description = "Facility Booking"
    _order = "start_datetime desc, id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False, readonly=True,
        default="New")
    room_id = fields.Many2one(
        "facility.room", string="Room", required=True, ondelete="restrict")
    site_id = fields.Many2one(
        related="room_id.site_id", store=True, readonly=True)
    organizer_id = fields.Many2one(
        "res.users", string="Organizer", required=True,
        default=lambda self: self.env.user)
    student_group_ids = fields.Many2many(
        "facility.student.group", string="Student Groups",
        help="Groups attending this booking.")
    start_datetime = fields.Datetime(required=True)
    stop_datetime = fields.Datetime(required=True)
    description = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"),
         ("cancelled", "Cancelled")],
        default="draft", required=True, copy=False)
    conflict_ids = fields.One2many(
        "facility.booking.conflict", "booking_id", string="Conflicts",
        readonly=True)
    has_blocking_conflict = fields.Boolean(
        compute="_compute_has_blocking_conflict", store=True)

    @api.depends("conflict_ids.severity")
    def _compute_has_blocking_conflict(self):
        for booking in self:
            booking.has_blocking_conflict = any(
                c.severity == "hard" for c in booking.conflict_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "facility.booking") or "New"
        return super().create(vals_list)

    @api.constrains("start_datetime", "stop_datetime")
    def _check_datetime_order(self):
        for booking in self:
            if (booking.start_datetime and booking.stop_datetime
                    and booking.stop_datetime <= booking.start_datetime):
                raise ValidationError(
                    _("The end date must be after the start date."))

    # ------------------------------------------------------------------
    # Generic constraint engine
    #
    # This engine contains NO business rule. It loops over every active
    # facility.constraint, dispatches to the method named in its
    # ``check_method``, and stores each returned message as a
    # facility.booking.conflict. New constraints are added simply by creating
    # a facility.constraint record and implementing its ``check_method`` here
    # or — preferably — from a dedicated bridge module via ``_inherit``.
    # ------------------------------------------------------------------
    def _collect_conflicts(self):
        """Pure constraint evaluation.

        Returns a list of ``(constraint, message)`` tuples and persists
        nothing. Being side-effect free, it can safely run on in-memory
        (NewId) records — for instance to probe a candidate room without
        creating any data.
        """
        self.ensure_one()
        results = []
        constraints = self.env["facility.constraint"].search(
            [("active", "=", True)], order="sequence")
        for constraint in constraints:
            checker = getattr(self, constraint.check_method, None)
            if not checker:
                # No method matches this constraint's check_method: log and
                # skip it rather than fail the whole evaluation.
                _logger.info(
                    "Constraint '%s' has no implementation (%s) yet — skipped.",
                    constraint.code, constraint.check_method)
                continue
            for message in (checker() or []):
                results.append((constraint, message))
        return results

    def _evaluate_constraints(self):
        """Persist the conflicts for this (saved) booking and return them."""
        self.ensure_one()
        self.conflict_ids.unlink()
        Conflict = self.env["facility.booking.conflict"]
        for constraint, message in self._collect_conflicts():
            Conflict.create({
                "booking_id": self.id,
                "constraint_id": constraint.id,
                "severity": constraint.constraint_type,
                "weight": constraint.weight,
                "message": message,
            })
        return self.conflict_ids

    def action_evaluate_constraints(self):
        for booking in self:
            booking._evaluate_constraints()

    # ------------------------------------------------------------------
    # Room suggestion for a single booking
    #
    # Returns the rooms in which this booking would raise no blocking conflict,
    # smallest capacity first, using the constraint engine as feasibility
    # oracle.
    # ------------------------------------------------------------------
    def _suggest_rooms(self):
        self.ensure_one()
        suggestions = self.env["facility.room"]
        for room in self.env["facility.room"].search([]):
            probe = self.new(origin=self)
            probe.room_id = room
            hard = [
                message for constraint, message in probe._collect_conflicts()
                if constraint.constraint_type == "hard"
            ]
            if not hard:
                suggestions |= room
        return suggestions.sorted(key=lambda r: r.capacity)

    def action_suggest_rooms(self):
        self.ensure_one()
        rooms = self._suggest_rooms()
        if rooms:
            message = _("Suggested rooms (best capacity-fit first): %s") % (
                ", ".join("%s [%s]" % (r.display_name, r.capacity)
                          for r in rooms))
            notif_type = "success"
        else:
            message = _("No room is free of blocking conflicts for this slot.")
            notif_type = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Room Suggestions"),
                "message": message,
                "type": notif_type,
                "sticky": False,
            },
        }

    def action_confirm(self):
        for booking in self:
            conflicts = booking._evaluate_constraints()
            blocking = conflicts.filtered(lambda c: c.severity == "hard")
            if blocking:
                raise ValidationError(
                    _("This booking cannot be confirmed:\n%s")
                    % "\n".join("• %s" % c.message for c in blocking))
            booking.state = "confirmed"

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.write({"state": "draft"})

    # ------------------------------------------------------------------
    # Constraint checks
    #
    # Each check returns a list of violation messages (empty when satisfied)
    # and is bound to a facility.constraint record via its ``check_method``.
    # ------------------------------------------------------------------
    def _check_past_date(self):
        self.ensure_one()
        messages = []
        if self.start_datetime and self.start_datetime < fields.Datetime.now():
            messages.append(_("The booking starts in the past."))
        return messages

    def _check_room_overlap(self):
        self.ensure_one()
        messages = []
        if not (self.room_id and self.start_datetime and self.stop_datetime):
            return messages
        overlapping = self.search([
            ("id", "not in", self.ids),
            ("room_id", "=", self.room_id.id),
            ("state", "=", "confirmed"),
            ("start_datetime", "<", self.stop_datetime),
            ("stop_datetime", ">", self.start_datetime),
        ])
        for other in overlapping:
            messages.append(_(
                "Room %(room)s is already booked (%(ref)s) during this "
                "time window.",
                room=self.room_id.display_name, ref=other.name))
        return messages
