from init import db, bcrypt
import re
from sqlalchemy.exc import NoResultFound
from flask import request, abort
from types import NoneType
from flask_jwt_extended import get_jwt_identity, get_jwt
from models.veterinarian import Veterinarian

def filter_all_records(model):
    stmt = db.select(model)
    return db.session.scalars(stmt)

def filter_one_record_by_id(model, id):
    stmt = db.select(model).filter_by(id=id)
    return db.session.scalar(stmt)

def filter_one_record_by_email(model, email):
    stmt = db.select(model).filter_by(email=email)
    return db.session.scalar(stmt)

def validate_password(password):
    if isinstance(password, NoneType):
        raise KeyError('password')
    if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
        raise ValueError('Password must contain minimum 8 characters, at lease one letter, one number and one special characters')
    return True

def required_record(model, id):
    record = filter_one_record_by_id(model, id)
    if not record:
        raise NoResultFound(f'{model.__name__} with id {id} not found')
    return record

def if_empty_convert_to_null(value):
    if len(value) == 0:
        return None
    else:
        return value

def nullable_value_converter(self, key):
    value = request.json.get(key)
    if isinstance(value, NoneType):
        return self.__dict__[key]
    else:
        return if_empty_convert_to_null(value)

def required_value_converter(self, key):
    value = request.json.get(key)
    if isinstance(value, NoneType):
        return self.__dict__[key]
    else:
        if key == 'password':
            validate_password(value)
            return bcrypt.generate_password_hash(value).decode('utf-8')
        else:
            return value

def is_admin():
    identity = get_jwt_identity()
    if 'C' in identity:
        abort(401)
    elif 'V' in identity:
        id = identity[1:]
        veterinarian = filter_one_record_by_id(Veterinarian, id)
        if not veterinarian.is_admin:
            abort(401)
    return True