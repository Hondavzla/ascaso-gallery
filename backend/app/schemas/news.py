from marshmallow import Schema, fields, validate


class NewsArticleSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=200))
    title = fields.String(required=True, validate=validate.Length(max=300))
    excerpt = fields.String(allow_none=True, validate=validate.Length(max=500))
    content = fields.String(allow_none=True)
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    external_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    source = fields.String(allow_none=True, validate=validate.Length(max=200))
    published_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
