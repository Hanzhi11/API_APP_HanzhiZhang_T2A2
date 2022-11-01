from types import NoneType
from flask import Blueprint, request
from init import db, bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.veterinarian import VeterinarianSchema, Veterinarian
import gb
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta

veterinarians_bp = Blueprint('veterinarians', __name__, url_prefix='/veterinarians')
    
@veterinarians_bp.route('/')
def get_all_veterinarians():
    veterinarians = gb.filter_all_records(Veterinarian)
    return VeterinarianSchema(many=True, exclude=['password']).dump(veterinarians)


@veterinarians_bp.route('/<int:veterinarian_id>/')
def get_one_veterinarian(veterinarian_id):
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    return VeterinarianSchema(exclude=['password']).dump(veterinarian)


@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['DELETE'])
def delete_veterinarian(veterinarian_id):
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    db.session.delete(veterinarian)
    db.session.commit()
    return {'msg': f'Veterinarian {veterinarian.first_name} {veterinarian.last_name} deleted successfully'}


@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['PUT', 'PATCH'])
def update_veterinarian(veterinarian_id):
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    for key in list(request.json.keys()):
        if key in ['languages', 'description']:
            setattr(veterinarian, key, gb.nullable_value_converter(veterinarian, key))
        else:
            setattr(veterinarian, key, gb.required_value_converter(veterinarian, key))
    db.session.commit()
    return VeterinarianSchema(exclude=['password']).dump(veterinarian)


@veterinarians_bp.route('/register/', methods=['POST'])
def veterinarian_register():
    password_input = request.json.get('password')
    gb.validate_password(password_input)

    veterinarian = Veterinarian(
        first_name = request.json['first_name'],
        last_name = request.json['last_name'],
        email = request.json['email'],
        password = bcrypt.generate_password_hash(password_input).decode('utf-8'),
        sex = request.json['sex'],
        languages = gb.if_empty_convert_to_null(request.json.get('languages')),
        is_admin = request.json['is_admin'],
        description = gb.if_empty_convert_to_null(request.json.get('description'))
    )

    db.session.add(veterinarian)
    db.session.commit()
    return VeterinarianSchema(exclude=['password']).dump(veterinarian), 201


@veterinarians_bp.route('/login/', methods=['POST'])
def veterinarian_login():
    email=request.json['email']
    password = request.json['password']
    veterinarian = gb.filter_one_record_by_email(Veterinarian, email)
    if veterinarian and bcrypt.check_password_hash(veterinarian.password, password):
        identity = ''.join(['V', str(veterinarian.id)])
        token = create_access_token(identity=identity, expires_delta=timedelta(days=1))
        return {'email': veterinarian.email, 'token': token}
    else:
        return {'error': 'Invalid email or passord'}, 401