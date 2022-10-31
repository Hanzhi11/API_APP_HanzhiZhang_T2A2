from types import NoneType
from flask import Blueprint, request
from init import db, bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.veterinarian import VeterinarianSchema, Veterinarian
import re
from sqlalchemy.exc import IntegrityError

veterinarians_bp = Blueprint('veterinarians', __name__, url_prefix='/veterinarians')

@veterinarians_bp.route('/')
def get_all_veterinarians():
    stmt = db.select(Veterinarian)
    veterinarians = db.session.scalars(stmt)
    return VeterinarianSchema(many=True, exclude=['password']).dump(veterinarians)

@veterinarians_bp.route('/<int:veterinarian_id>/')
def get_one_veterinarian(veterinarian_id):
    stmt = db.select(Veterinarian).filter_by(id=veterinarian_id)
    veterinarian = db.session.scalar(stmt)
    if veterinarian:
        return VeterinarianSchema(exclude=['password']).dump(veterinarian)
    else:
        return {'error': f'Veterinarian with id {veterinarian_id} not found'}, 404

@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['DELETE'])
def delete_veterinarian(veterinarian_id):
    stmt = db.select(Veterinarian).filter_by(id=veterinarian_id)
    veterinarian = db.session.scalar(stmt)
    if veterinarian:
        db.session.delete(veterinarian)
        db.session.commit()
        return {'msg': f'Veterinarian {veterinarian.first_name} {veterinarian.last_name} deleted successfully'}
    else:
        return {'error': f'Veterinarian with id {veterinarian_id} not found'}, 404

@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['PUT', 'PATCH'])
def update_veterinarian(veterinarian_id):
    stmt = db.select(Veterinarian).filter_by(id=veterinarian_id)
    veterinarian = db.session.scalar(stmt)
    if veterinarian:
        veterinarian.first_name = request.json.get('first_name') or veterinarian.first_name
        veterinarian.last_name = request.json.get('last_name') or veterinarian.last_name
        veterinarian.email = request.json.get('email') or veterinarian.email
        veterinarian.sex = request.json.get('sex') or veterinarian.sex
        veterinarian.is_admin = request.json.get('is_admin') or veterinarian.is_admin

        new_description = request.json.get('description')
        if isinstance(new_description, NoneType):
            veterinarian.description = veterinarian.description
        else:
            if len(new_description) == 0:
                veterinarian.description = None
            else:
                veterinarian.description = request.json.get('description')
        
        new_languages = request.json.get('languages')
        if isinstance(new_languages, NoneType):
            veterinarian.languages = veterinarian.languages
        else:
            if len(new_languages) == 0:
                veterinarian.languages = None
            else:
                veterinarian.languages = request.json.get('languages')

        new_password = request.json.get('password')
        if new_password:
            if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', new_password):
                raise ValueError('Password must contain minimum 8 characters, at lease one letter, one number and one special characters')
            veterinarian.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        else:
            veterinarian.password = veterinarian.password
        db.session.commit()
        return VeterinarianSchema(exclude=['password']).dump(veterinarian)
    else:
        return {'error': f'Veterinarian with id {veterinarian_id} not found'}, 404

@veterinarians_bp.route('/register/', methods=['POST'])
def veterinarian_register():
    password_input = request.json.get('password')
    if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password_input):
        raise ValueError('Password must contain minimum 8 characters, at lease one letter, one number and one special characters')
    try:
        veterinarian = Veterinarian(
            first_name = request.json['first_name'],
            last_name = request.json['last_name'],
            email = request.json['email'],
            password = bcrypt.generate_password_hash(password_input).decode('utf-8'),
            sex = request.json['sex'],
            languages = request.json.get('languages'),
            is_admin = request.json['is_admin'],
            description = request.json.get('description')
        )
        db.session.add(veterinarian)
        db.session.commit()
        return VeterinarianSchema(exclude=['password']).dump(veterinarian), 201
    except IntegrityError:
        return {'error': 'Email address exists already'}, 409