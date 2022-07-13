from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, validates, ValidationError, post_load
from setup_db import db


class Advert(db.Model):
    __tabelname__ = 'advert'

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(Date, default=datetime.now().date())
    owner_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    owner = relationship('User')


class AdvertSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, allow_none=False)
    description = fields.Str()
    created_at = fields.Date()
    owner = fields.Str(required=True, allow_none=False)

    @post_load
    def make_advert(self, data, **kwargs):
        return Advert(**data)


adv_schema = AdvertSchema()
advs_schema = AdvertSchema(many=True)


class User(db.Model):
    __tabelname__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)


class UserSchema(Schema):
    id = fields.Int()
    email = fields.Email(required=True, allow_none=False)
    password = fields.Str(required=True, allow_none=False)

    @validates('password')
    def validate_password(self, password):
        if not password or len(password) < 8:
            raise ValidationError("password to easy")

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
