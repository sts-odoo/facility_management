from odoo import fields, models


class FacilityConstraint(models.Model):
    """A configurable booking constraint dimension.

    This model is the *catalogue* of constraints. It holds no business logic:
    each record points (via ``check_method``) to a method implemented on
    ``facility.booking`` that performs the actual check. This keeps the engine
    generic and lets new constraints be added — typically from dedicated bridge
    modules — without ever touching the engine itself.
    """

    _name = "facility.constraint"
    _description = "Booking Constraint"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(
        required=True,
        help="Technical identifier of the constraint dimension.")
    check_method = fields.Char(
        required=True,
        help="Name of the method on facility.booking implementing this "
             "constraint, e.g. '_check_room_overlap'. It must return a list of "
             "human-readable messages (one per violation), or an empty "
             "list / None when the constraint is satisfied.")
    constraint_type = fields.Selection(
        [("hard", "Hard (blocking)"), ("soft", "Soft (penalty)")],
        required=True, default="hard",
        help="Hard constraints block confirmation. Soft constraints only raise "
             "a warning and contribute their weight to optimisation scores.")
    weight = fields.Integer(
        default=0,
        help="Penalty weight used by soft constraints in scoring / "
             "optimisation (cost functions, room suggestion, ...). "
             "Ignored for hard constraints.")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()

    _code_uniq = models.Constraint(
        "unique(code)",
        "The constraint code must be unique.",
    )
