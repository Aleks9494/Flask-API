from marshmallow import Schema, validate, fields


class CommentSchema(Schema):
    id = fields.Integer(dump_only=True)  # только для сериализации (вывода),чтения
    user_id = fields.Integer(load_only=True)  # только для десериализации (ввода), записи
    post_id = fields.Integer(load_only=True)
    date_posted = fields.DateTime(dump_only=True)
    body = fields.String(required=True)
    username = fields.String(required=True, validate=[validate.Length(max=20)])


class PostSchema(Schema):
    id = fields.Integer(dump_only=True)  # только для сериализации (вывода)
    user_id = fields.Integer(dump_only=True)
    date_posted = fields.DateTime(dump_only=True)
    title = fields.String(required=True, validate=[validate.Length(max=250)])
    content = fields.String(required=True)
    comments = fields.Nested(CommentSchema, many=True, dump_only=True)
    message = fields.String(dump_only=True)


class UpdatePostSchema(PostSchema):
    title = fields.String(validate=[validate.Length(max=250)])
    content = fields.String()


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)  # только для сериализации (вывода)
    username = fields.String(required=True, validate=[validate.Length(max=100)])
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=[validate.Length(max=250)])
    user_status = fields.String(validate=[validate.Length(max=40)])
    posts = fields.Nested(PostSchema, many=True, dump_only=True)     # доступ к связанной таблице posts (relationship)
    comments = fields.Nested(CommentSchema, many=True, dump_only=True)
    message = fields.String(dump_only=True)


class UpdateUserSchema(UserSchema):
    username = fields.String(validate=[validate.Length(max=100)])
    email = fields.Email()
    password = fields.String(load_only=True, validate=[validate.Length(max=250)])


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)


