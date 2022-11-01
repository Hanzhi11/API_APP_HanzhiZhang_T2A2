from types import NoneType
from flask import Blueprint, request
from init import db, bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.veterinarian import VeterinarianSchema, Veterinarian
import re
from sqlalchemy.exc import IntegrityError, NoResultFound

veterinarians_bp = Blueprint('veterinarians', __name__, url_prefix='/veterinarians')

def filter_one_veterinarian(id):
    stmt = db.select(Veterinarian).filter_by(id=id)
    return db.session.scalar(stmt)

def validate_password(password):
    if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
        raise ValueError('Password must contain minimum 8 characters, at lease one letter, one number and one special characters')
    return True

def required_veterinarian(id):
    vaterinarian = filter_one_veterinarian(id)
    if not vaterinarian:
        raise NoResultFound(f'Veterinarian with id {id} not found')
    return vaterinarian

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
    
@veterinarians_bp.route('/')
def get_all_veterinarians():
    stmt = db.select(Veterinarian)
    veterinarians = db.session.scalars(stmt)
    return VeterinarianSchema(many=True, exclude=['password']).dump(veterinarians)

@veterinarians_bp.route('/<int:veterinarian_id>/')
def get_one_veterinarian(veterinarian_id):
    veterinarian = required_veterinarian(veterinarian_id)
    return VeterinarianSchema(exclude=['password']).dump(veterinarian)


@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['DELETE'])
def delete_veterinarian(veterinarian_id):
    veterinarian = required_veterinarian(veterinarian_id)
    db.session.delete(veterinarian)
    db.session.commit()
    return {'msg': f'Veterinarian {veterinarian.first_name} {veterinarian.last_name} deleted successfully'}
    

@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['PUT', 'PATCH'])
def update_veterinarian(veterinarian_id):
    veterinarian = required_veterinarian(veterinarian_id)
    try:
        for key in list(request.json.keys()):
            if key in ['languages', 'description']:
                setattr(veterinarian, key, nullable_value_converter(veterinarian, key))
            else:
                setattr(veterinarian, key, required_value_converter(veterinarian, key))
        db.session.commit()
        return VeterinarianSchema(exclude=['password']).dump(veterinarian)
    except IntegrityError:
        return {'error': 'Email address exists already'}, 409

@veterinarians_bp.route('/register/', methods=['POST'])
def veterinarian_register():
    password_input = request.json.get('password')
    validate_password(password_input)

    try:
        veterinarian = Veterinarian(
            first_name = request.json['first_name'],
            last_name = request.json['last_name'],
            email = request.json['email'],
            password = bcrypt.generate_password_hash(password_input).decode('utf-8'),
            sex = request.json['sex'],
            languages = if_empty_convert_to_null(request.json.get('languages')),
            is_admin = request.json['is_admin'],
            description = if_empty_convert_to_null(request.json.get('description'))
        )
        db.session.add(veterinarian)
        db.session.commit()
        return VeterinarianSchema(exclude=['password']).dump(veterinarian), 201
    except IntegrityError:
        return {'error': 'Email address exists already'}, 409