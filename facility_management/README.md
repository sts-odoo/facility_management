# Facility Management

Multi-site management of bookable rooms and their reservations, for Odoo 19.0.

## Data model

| Model | Purpose |
|-------|---------|
| `facility.site` | A physical site / campus (with geolocation). |
| `facility.room` | A bookable room, belonging to a site. |
| `facility.equipment` | Equipment a room can offer (projector, lab, ...). |
| `facility.student.group` | A group of attendees linked to bookings. |
| `facility.booking` | A room booking with a draft / confirmed / cancelled lifecycle. |
| `facility.constraint` | The configurable catalogue of booking constraints. |
| `facility.booking.conflict` | A violation detected for a booking by a constraint. |

## Constraint engine

`facility.booking._evaluate_constraints()` runs every active
`facility.constraint`, dispatches to the method named in its `check_method`,
and records each returned message as a `facility.booking.conflict`.

* **Hard** constraints block confirmation (`ValidationError`).
* **Soft** constraints raise a non-blocking warning and carry a `weight` used
  for scoring.

### Adding a constraint

1. Create a `facility.constraint` record (`code`, `check_method`,
   `constraint_type`, optionally `weight`).
2. Add `_check_<code>(self)` on `facility.booking`, returning a list of
   messages (one per violation), or `[]` when satisfied. It can live in a
   separate module that `_inherit`s `facility.booking`.
