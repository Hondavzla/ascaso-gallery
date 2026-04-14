from marshmallow import Schema, fields, validate


class ArtFairSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=120))
    name = fields.String(required=True, validate=validate.Length(max=200))
    dates = fields.String(allow_none=True, validate=validate.Length(max=200))
    location = fields.String(allow_none=True, validate=validate.Length(max=200))
    booth = fields.String(allow_none=True, validate=validate.Length(max=50))
    description = fields.String(allow_none=True)
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    year = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
