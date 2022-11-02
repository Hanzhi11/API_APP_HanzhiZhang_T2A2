from init import db, bcrypt
import re
from sqlalchemy.exc import NoResultFound
from flask import request
from types import NoneType
from flask_jwt_extended import get_jwt_identity
from models.veterinarian import Veterinarian
from models.patient import Patient
from models.appointment import Appointment

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

def get_customer_id():
    identity = get_jwt_identity()
    if 'V' in identity:
        return False
    return int(identity[1:])

def get_veterinarian_id():
    identity = get_jwt_identity()
    if 'C' in identity:
        return False
    return int(identity[1:])

def is_admin():
    id = get_veterinarian_id()
    if id:
        veterinarian = filter_one_record_by_id(Veterinarian, id)
        if veterinarian.is_admin:
            return True

def is_authorized_customer(customer_id):
    id = get_customer_id()
    if id == customer_id:
        return True

def is_authorized_veterinarian(veterinarian_id):
    id = get_veterinarian_id()
    if id == veterinarian_id:
        return True

def is_authorized_veterinarians(customer_id):
    id = get_veterinarian_id()
    if id:
        stmt = db.select(Appointment).filter_by(veterinarian_id=id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id)
        result = db.session.execute(stmt).all()
        if result:
            return True

# def is_authorized_person(customer_id):
#     if is_admin() or is_authorized_customer(customer_id) or is_authorized_veterinarian(customer_id):
#         return True

