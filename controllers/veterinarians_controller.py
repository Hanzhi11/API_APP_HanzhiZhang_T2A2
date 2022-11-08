from types import NoneType
from flask import Blueprint, request
from init import db, bcrypt, jwt, auto
from flask_jwt_extended import jwt_required, create_access_token, current_user, get_jwt
from models.veterinarian import VeterinarianSchema, Veterinarian
from models.token_block_list import TokenBlocklist
import gb
from datetime import timedelta, datetime


veterinarians_bp = Blueprint('veterinarians', __name__, url_prefix='/veterinarians')


# check if the veterinarian who has logged in has been authorized
def is_authorized_veterinarian(veterinarian_id):
    id = gb.get_veterinarian_id()
    if id == veterinarian_id:
        return True


# if the value is an empty string, convert it to null
def if_empty_convert_to_null(value):
    if value:
        return value


# return a correct value according to the data in the request
def nullable_value_converter(self, key):
    value = request.json.get(key)
    if isinstance(value, NoneType):
        return self.__dict__[key]
    else:
        return if_empty_convert_to_null(value)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    stmt = db.select(TokenBlocklist).filter_by(jti=jti)
    token = db.session.scalar(stmt)
    return token is not None


@jwt.revoked_token_loader
def revoked_token(jwt_header, jwt_payload):
    return {'error': "You haven't logged into the app yet."}, 401


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Veterinarian.query.filter_by(id=identity).one_or_none()


# read all veterinarians and return the public information only
@veterinarians_bp.route('/public/')
@auto.doc()
def get_all_veterinarians():
    '''Return the public information of all veterinarians'''
    # get all records from the veterinarians table in the database
    veterinarians = gb.filter_all_records(Veterinarian)
    return VeterinarianSchema(many=True, only=['id', 'first_name', 'last_name', 'description', 'email', 'sex', 'languages']).dump(veterinarians)


# read all veterinarians and return all information, except password
@veterinarians_bp.route('/')
@auto.doc()
@jwt_required()
def get_all_veterinarians_full_details():
    '''Admin interface - Return the full details of all veterinarians including is_admin and appointments'''
    if gb.is_admin():
        # get all records from the veterinarians table in the database
        veterinarians = gb.filter_all_records(Veterinarian)
        return VeterinarianSchema(many=True).dump(veterinarians)
    else:
        return {'error': 'You are not an administrator.'}, 401


# read one veterinarian and return the public information only
@veterinarians_bp.route('/<int:veterinarian_id>/public')
@auto.doc()
def get_one_veterinarian(veterinarian_id):
    '''Return the public information of one veterinarian with the given id'''
    # get one record from the veterinarians table in the database with the given veterinarian id
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    return VeterinarianSchema(only=['first_name', 'last_name', 'description', 'email', 'sex', 'languages']).dump(veterinarian)


# read current veterinarian's profile
@veterinarians_bp.route('/my_profile/')
@auto.doc()
@jwt_required()
def my_profile():
    '''Return the profile of the current veterinarian including is_admin'''
    if get_jwt()['role'] == 'veterinarian':
        return VeterinarianSchema(exclude=['appointments']).dump(current_user)
    else:
        return {'error': 'You are not a veterinarian'}, 401


# read one veterinarian and return all information, except password
@veterinarians_bp.route('/<int:veterinarian_id>/')
@auto.doc()
@jwt_required()
def get_one_veterinarian_full_details(veterinarian_id):
    '''Return the full details of one veterinarian with the given id'''
    # get one record from the veterinarians table in the database with the given veterinarian id
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    if gb.is_admin() or is_authorized_veterinarian(veterinarian_id):
        return VeterinarianSchema().dump(veterinarian)
    else:
        return {'error': 'You are not authorized to view the information.'}, 401


# delete one veterinarian
@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['DELETE'])
@auto.doc()
@jwt_required()
def delete_veterinarian(veterinarian_id):
    '''Admin interface - Delete one veterinarian with the given id'''
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    if gb.is_admin():
        # delete one record from the veterinarians table in the database with the given veterinarian id
        db.session.delete(veterinarian)
        db.session.commit()
        return {'msg': f'Veterinarian {veterinarian.first_name} {veterinarian.last_name} deleted successfully'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one veterinarian
@veterinarians_bp.route('/<int:veterinarian_id>/', methods=['PUT', 'PATCH'])
@auto.doc()
@jwt_required()
def update_veterinarian(veterinarian_id):
    '''Update one veterinarian with the given id and return the updated profile of the veterinarian excluding appointments'''
    veterinarian = gb.required_record(Veterinarian, veterinarian_id)
    if gb.is_admin() or is_authorized_veterinarian(veterinarian_id):
        # update one record in the veterinarians table in the database with the given veterinarian id using the information contained in the request
        for key in list(request.json.keys()):
            if key in ['languages', 'description']:
                setattr(veterinarian, key, nullable_value_converter(veterinarian, key))
            else:
                setattr(veterinarian, key, gb.required_value_converter(veterinarian, key))
        db.session.commit()
        return VeterinarianSchema(exclude=['appointments']).dump(veterinarian)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new veterinarian
@veterinarians_bp.route('/register/', methods=['POST'])
@auto.doc()
def veterinarian_register():
    '''Create a new veterinarian and return the full details of the veterinarian created'''
    password_input = request.json['password']
    gb.validate_password(password_input)
    is_admin_input = request.json.get('is_admin')
    if not is_admin_input:
        is_admin_input = False
    # add a new record to the veterinarians table in the database
    veterinarian = Veterinarian(
        first_name = request.json['first_name'],
        last_name = request.json['last_name'],
        email = request.json['email'],
        password = bcrypt.generate_password_hash(password_input).decode('utf-8'),
        sex = request.json['sex'],
        languages = if_empty_convert_to_null(request.json.get('languages')),
        is_admin = is_admin_input,
        description = if_empty_convert_to_null(request.json.get('description'))
    )
    db.session.add(veterinarian)
    db.session.commit()
    return VeterinarianSchema().dump(veterinarian), 201


# veterinarian authentication
@veterinarians_bp.route('/login/', methods=['POST'])
@auto.doc()
def veterinarian_login():
    '''Veterinarian login and return the email of and token for the veterinarian'''
    email=request.json['email']
    password = request.json['password']
    # get one record from the veterinarians table in the database with the given email
    veterinarian = gb.filter_one_record_by_email(Veterinarian, email)
    if veterinarian and bcrypt.check_password_hash(veterinarian.password, password):
        # identity = ''.join(['V', str(veterinarian.id)])
        identity = str(veterinarian.id)
        additional_claims = {'role': 'veterinarian'}
        token = create_access_token(identity=identity, expires_delta=timedelta(days=1), additional_claims=additional_claims)
        return {'email': veterinarian.email, 'token': token}
    else:
        return {'error': 'Invalid email or passord'}, 401


# JWT revoking
@veterinarians_bp.route("/logout/", methods=["DELETE"])
@auto.doc()
@jwt_required()
def revoke_token():
    '''Veterinarian logout'''
    jti = get_jwt()["jti"]
    now = datetime.now()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return {'msg': 'You logged out successfully'}
