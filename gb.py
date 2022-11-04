from init import db, bcrypt
import re
from sqlalchemy.exc import NoResultFound
from flask import request
from types import NoneType
from flask_jwt_extended import get_jwt_identity, get_jwt
from models.veterinarian import Veterinarian

# get all records from the given table in the database
def filter_all_records(model):
    stmt = db.select(model)
    return db.session.scalars(stmt)

# get one record from the given table in the database with the given id
def filter_one_record_by_id(model, id):
    stmt = db.select(model).filter_by(id=id)
    return db.session.scalar(stmt)

# get one record from the given table in the database with the given email
def filter_one_record_by_email(model, email):
    stmt = db.select(model).filter_by(email=email)
    return db.session.scalar(stmt)

# validate if the input is valid for password
def validate_password(password):
    if isinstance(password, NoneType):
        raise KeyError('password')
    if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
        raise ValueError('Password must contain minimum 8 characters, at lease one letter, one number and one special characters')
    return True

# check if the required id exists in the given table in the database
def required_record(model, id):
    record = filter_one_record_by_id(model, id)
    if not record:
        raise NoResultFound(f'{model.__name__} with id {id} not found')
    return record

# def if_empty_convert_to_null(value):
#     if len(value) == 0:
#         return None
#     else:
#         return value

# def nullable_value_converter(self, key):
#     value = request.json.get(key)
#     if isinstance(value, NoneType):
#         return self.__dict__[key]
#     else:
#         return if_empty_convert_to_null(value)

# return a correct value according to the data in the request
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


# get customer id from the token
def get_customer_id():
    if get_jwt()['role'] == 'veterinarian':
        return False
    return int(get_jwt_identity())


# # get veterinarian id from the token
def get_veterinarian_id():
    if get_jwt()['role'] == 'customer':
        return False
    return int(get_jwt_identity())

# check if the person is an administrator according to the identity contained in the token
def is_admin():
    id = get_veterinarian_id()
    if id:
        veterinarian = filter_one_record_by_id(Veterinarian, id)
        if veterinarian.is_admin:
            return True

# def is_authorized_customer(customer_id):
#     id = get_customer_id()
#     if id == customer_id:
#         return True

# def is_patient_authorized_person(patient_id):
#     customer_id = get_customer_id()
#     veterinarian_id = get_veterinarian_id()
#     if customer_id:
#         stmt = db.select(Patient).filter_by(customer_id=customer_id, id=patient_id)
#         result = db.session.scalar(stmt)
#         if result:
#             return True
#     elif veterinarian_id:
#         stmt = db.select(Appointment).filter_by(veterinarian_id=veterinarian_id, patient_id=patient_id)
#         result = db.session.scalar(stmt)
#         if result:
#             return True

# def is_appointment_authorized_person(appointment_id):
#     customer_id = get_customer_id()
#     veterinarian_id = get_veterinarian_id()
#     if customer_id:
#         stmt = db.select(Appointment).filter_by(appointment_id=id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id)
#         result = db.session.scalar(stmt)
#         if result:
#             return True
#     elif veterinarian_id:
#         stmt = db.select(Appointment).filter_by(veterinarian_id=veterinarian_id, appointment_id=appointment_id)
#         result = db.session.scalar(stmt)
#         if result:
#             return True

# def is_authorized_veterinarian(veterinarian_id):
#     id = get_veterinarian_id()
#     if id == veterinarian_id:
#         return True

# def is_authorized_veterinarians(customer_id):
#     id = get_veterinarian_id()
#     if id:
#         stmt = db.select(Appointment).filter_by(veterinarian_id=id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id)
#         result = db.session.scalar(stmt)
#         print(result)
#         if result:
#             return True


