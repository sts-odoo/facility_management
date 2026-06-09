{
    "name": "Facility Management",
    "version": "19.0.1.0.0",
    "category": "Operations",
    "summary": "Generic multi-site facility & room booking core with a pluggable "
               "constraint engine.",
    "description": """
Facility Management
===================

Multi-site management of bookable rooms and their reservations.

Features:
  * Sites, rooms and equipment.
  * Room bookings with a draft / confirmed / cancelled lifecycle.
  * A configurable constraint engine: each booking is checked against the
    active constraints on confirmation, splitting results into blocking errors
    and non-blocking warnings.
  * Room suggestion for a booking, based on the active constraints.
  * Student groups linked to bookings.
""",
    "author": "UCLouvain x Odoo",
    "website": "https://github.com/sts-odoo",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/facility_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/facility_constraint_data.xml",
        "views/facility_site_views.xml",
        "views/facility_room_views.xml",
        "views/facility_equipment_views.xml",
        "views/facility_constraint_views.xml",
        "views/facility_student_group_views.xml",
        "views/facility_booking_views.xml",
        "views/facility_menus.xml",
    ],
    "demo": ["demo/facility_demo.xml"],
    "application": True,
    "installable": True,
}
