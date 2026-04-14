from marshmallow import Schema, fields, validate


class ExhibitionSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=120))
    title = fields.String(required=True, validate=validate.Length(max=200))
    subtitle = fields.String(allow_none=True, validate=validate.Length(max=300))
    status = fields.String(required=True, validate=validate.OneOf(['current', 'upcoming', 'past']))
    dates = fields.String(allow_none=True, validate=validate.Length(max=200))
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    description = fields.String(allow_none=True)
    display_order = fields.Integer(load_default=0)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
