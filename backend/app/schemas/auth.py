from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class AdminUserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email()
    created_at = fields.DateTime()
    last_login_at = fields.DateTime(allow_none=True)
