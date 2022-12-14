from flask import Blueprint, request
from init import db, bcrypt, jwt, auto
from flask_jwt_extended import jwt_required, create_access_token, current_user, get_jwt
from models.customer import CustomerSchema, Customer
from models.appointment import Appointment
from models.patient import Patient
from models.token_block_list import TokenBlocklist
import gb
from datetime import timedelta, datetime


customers_bp = Blueprint('customers', __name__, url_prefix='/customers')


# check if the veterinarian who has logged in has been authorized 
def is_authorized_veterinarians(customer_id):
    id = gb.get_veterinarian_id()
    if id:
        # by joining the appointments and patients tables and using the given customer id, get one record from the appointments table with the appointment_id obtained from the token
        # i.e. get one appointment which is related to both the given customer id and the obtained veterinarian id
        stmt = db.select(Appointment).filter_by(veterinarian_id=id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id) 
        result = db.session.scalar(stmt)
        if result:
            return True         


# check if the customer who has logged in has been authorized 
def is_authorized_customer(customer_id):
    id = gb.get_customer_id()
    if id == customer_id:
        return True


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
    identity = jwt_data['sub']
    return Customer.query.filter_by(id=identity).one_or_none()


# read all customers
@customers_bp.route('/')
@auto.doc()
@jwt_required()
def get_all_customers():
    '''Admin interface - Return the full details of all customers.'''
    if gb.is_admin():
        # get all records from the customers table in the database
        customers = gb.filter_all_records(Customer)
        return CustomerSchema(many=True).dump(customers)
    else:
        return {'error': 'You are not an administrator.'}, 401


# read current customer's profile
@customers_bp.route('/my_profile/')
@auto.doc()
@jwt_required()
def my_profile():
    '''Return the profile of the current customer excluding patients.'''
    if get_jwt()['role'] == 'customer':
        return CustomerSchema(only=['id', 'first_name', 'last_name', 'contact_number', 'email']).dump(current_user)
    else:
        return {'error': 'You are not an customer'}, 401


# read one customer
@customers_bp.route('/<int:customer_id>/')
@auto.doc()
@jwt_required()
def get_one_customer(customer_id):
    '''Return the full details of one customer with the given id in the format of integer as argument.'''
    customer = gb.required_record(Customer, customer_id)
    if gb.is_admin() or is_authorized_customer(customer_id) or is_authorized_veterinarians(customer_id):
        # get one record from the customers table in the database with the given customer id
        return CustomerSchema().dump(customer)
    else:
        return {'error': 'You are not authorized to view the information.'}, 401


# delete one customer
@customers_bp.route('/<int:customer_id>/', methods=['DELETE'])
@auto.doc()
@jwt_required()
def delete_customer(customer_id):
    '''Admin interface - Delete one customer with the given id in the format of integer as argument.'''
    customer = gb.required_record(Customer, customer_id)
    if gb.is_admin():
        # delete one record from the customers table in the database with the given customer id
        db.session.delete(customer)
        db.session.commit()
        return {'msg': f'Customer {customer.first_name} {customer.last_name} deleted successfully'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one customer's details
@customers_bp.route('/<int:customer_id>/', methods=['PUT', 'PATCH'])
@auto.doc()
@jwt_required()
def update_customer(customer_id):
    '''Update one customer with the given id in the format of integer as argument and the key-value pairs as request body, and return the updated full details of the customer. The keys are first_name, last_name, email, password and contact_number, and are all optional. The format of the values are: non-empty string for first_name and last_name with the maximum length of 25 characters, string for email with the maximum length of 50 characters, string for password with the mininum length of 8 characters and containing at lease one letter, one number and one special character, and string for contact_number with the fixed length of 10 characters.'''
    customer = gb.required_record(Customer, customer_id)
    if gb.is_admin() or is_authorized_customer(customer_id) or is_authorized_veterinarians(customer_id):
        # update one record in the customers table in the database with the given customer id using the information contained in the request
        for key in list(request.json.keys()):
            setattr(customer, key, gb.required_value_converter(customer, key))
        db.session.commit()
        return CustomerSchema().dump(customer)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new customer
@customers_bp.route('/register/', methods=['POST'])
@auto.doc()
def customer_register():
    '''Customer registration with key-value pairs, and return the full details of the customer registered. The keys are first_name, last_name, email, password and contact_number, and are all required. The format of the values are: non-empty string for first_name and last_name with the maximum length of 25 characters, string for email with the maximum length of 50 characters, string for password with the mininum length of 8 characters and containing at lease one letter, one number and one special character, and string for contact_number with the fixed length of 10 characters.'''
    password_input = request.json['password']
    gb.validate_password(password_input)
    # add a new record in the customers table in the database
    customer = Customer(
        first_name = request.json['first_name'],
        last_name = request.json['last_name'],
        contact_number = request.json['contact_number'],
        email = request.json['email'],
        password = bcrypt.generate_password_hash(password_input).decode('utf-8')
    )
    db.session.add(customer)
    db.session.commit()
    return CustomerSchema().dump(customer), 201


# customer authentication
@customers_bp.route('/login/', methods=['POST'])
@auto.doc()
def customer_login():
    '''Customer login with the key-value pairs for email and password as request body, and return the email of and the token for the customer.'''
    email=request.json['email']
    password = request.json['password']
    # get one record from the customers table in the database with the given email
    customer = gb.filter_one_record_by_email(Customer, email)
    if customer and bcrypt.check_password_hash(customer.password, password):
        # identity = ''.join(['C', str(customer.id)])
        identity = str(customer.id)
        additional_claims = {'role': 'customer'}
        token = create_access_token(identity=identity, expires_delta=timedelta(days=1), additional_claims=additional_claims)
        return {'email': customer.email, 'token': token}
    else:
        return {'error': 'Invalid email or passord'}, 401


# JWT revoking
@customers_bp.route('/logout', methods=['DELETE'])
@auto.doc()
@jwt_required()
def revoke_token():
    '''Customer logout.'''
    jti = get_jwt()["jti"]
    now = datetime.now()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return {'msg': 'You logged out successfully'}


