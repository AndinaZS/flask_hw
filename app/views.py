from marshmallow import exceptions
from sqlalchemy.exc import IntegrityError
from models import User, user_schema, users_schema
from models import Advert, adv_schema, advs_schema
from flask import request
from flask_restx import Resource, Namespace
from flask_bcrypt import Bcrypt
from setup_db import db

advert_ns = Namespace('adverts')
user_ns = Namespace('users')
bcrypt = Bcrypt()

def verify_data(schema, data):
    try:
        return  schema.load(data)
    except exceptions.ValidationError as er:
        raise HttpError(400, er.messages)

class HttpError(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message


@advert_ns.route('/')
class AdvertsView(Resource):
    def get(self):
        all_advs = Advert.query.all()
        return advs_schema.dump(all_advs), 200

    def post(self):
        adv = request.json
        new_adv = Advert(**adv)
        db.session.add(new_adv)
        try:
            db.session.commit()
        except IntegrityError:
            raise HttpError(400, 'user not exists')
        return adv_schema.dump(new_adv), 201


@advert_ns.route('/<int:aid>')
class AdvertView(Resource):
    def get(self, aid: int):
        adv = Advert.query.get(aid)
        return adv_schema.dump(adv)

    def patch(self, aid):
        adv = Advert.query.get_or_404(aid, description='id does not exist')
        request_json = request.json
        adv.title = request_json.get('title', adv.title)
        adv.description = request_json.get('description', adv.description)
        db.session.add(adv)
        db.session.commit()
        return adv_schema.dump(adv), 204

    def delete(self, aid):
        adv = Advert.query.get_or_404(aid, description='id does not exist')
        db.session.delete(adv)
        db.session.commit()
        return "", 204


@user_ns.route('/')
class UsersView(Resource):
    def get(self):
        all_users = User.query.all()
        return users_schema.dump(all_users), 200

    def post(self):
        user_data = request.json
        user = verify_data(user_schema, user_data)
        db.session.add(user)
        user.password = bcrypt.generate_password_hash(user.password.encode()).decode()
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as er:
            raise HttpError(400, 'email is already in use')
        return user_schema.dump(user), 201


@user_ns.route('/<int:uid>')
class UserView(Resource):
    def get(self, uid: int):
        user = User.query.get(uid)
        return user_schema.dump(user), 200

    def patch(self, uid):
        user = User.query.get_or_404(uid, description='id does not exist')
        request_json = request.json
        user.email = request_json.get('email', user.email)
        if request_json.get('password'):
            user.password = bcrypt.generate_password_hash(request_json['password'].encode()).decode()
        db.session.add(verify_data(user_schema, user_schema.dump(user)))
        try:
            db.session.commit()
        except IntegrityError as er:
            raise HttpError(400, 'email is already in use')
        return "", 204

    def delete(self, uid):
        user = User.query.get_or_404(uid, description='id does not exist')
        db.session.delete(user)
        db.session.commit()
        return (f'{uid}', 204)

