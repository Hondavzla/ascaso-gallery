from marshmallow import Schema, fields, validate


class ArtWorkSchema(Schema):
    slug = fields.String(required=True, validate=validate.Length(max=120))
    title = fields.String(required=True, validate=validate.Length(max=200))
    year = fields.Integer(allow_none=True)
    medium = fields.String(allow_none=True, validate=validate.Length(max=100))
    image_url = fields.String(required=True, validate=validate.Length(max=500))
    display_order = fields.Integer(load_default=0)
    created_at = fields.DateTime(dump_only=True)


class ArtistSummarySchema(Schema):
    slug = fields.String()
    name = fields.String()
    medium = fields.String()
    eyebrow = fields.String()
    hero_image_url = fields.String()
    featured = fields.Boolean()
    display_order = fields.Integer()


class ArtistSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=120))
    name = fields.String(required=True, validate=validate.Length(max=200))
    medium = fields.String(allow_none=True, validate=validate.Length(max=100))
    nationality = fields.String(allow_none=True, validate=validate.Length(max=100))
    eyebrow = fields.String(allow_none=True, validate=validate.Length(max=100))
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    featured = fields.Boolean(load_default=False)
    display_order = fields.Integer(load_default=0)

    bio = fields.Dict(allow_none=True)
    quote = fields.Dict(allow_none=True)
    awards = fields.List(fields.String(), allow_none=True)
    collections = fields.List(fields.String(), allow_none=True)
    exhibitions_history = fields.List(fields.Dict(), allow_none=True)
    monumental_works = fields.List(fields.Dict(), allow_none=True)

    works = fields.List(fields.Nested(ArtWorkSchema), dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
