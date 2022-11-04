from flask import Blueprint, request
from init import db, bcrypt, jwt
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


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    stmt = db.select(TokenBlocklist).filter_by(jti=jti)
    token = db.session.scalar(stmt)
    return token is not None


@jwt.revoked_token_loader
def revoked_token(jwt_header, jwt_payload):
    return {'error': "You haven't logged into the app yet."}, 401


# check if the customer who has logged in has been authorized 
def is_authorized_customer(customer_id):
    id = gb.get_customer_id()
    if id == customer_id:
        return True


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return Customer.query.filter_by(id=identity).one_or_none()


# read all customers
@customers_bp.route('/')
@jwt_required()
def get_all_customers():
    if gb.is_admin():
        # get all records from the customers table in the database
        customers = gb.filter_all_records(Customer)
        return CustomerSchema(many=True, exclude=['password']).dump(customers)
    else:
        return {'error': 'You are not an administrator.'}, 401


# read current customer's profile
@customers_bp.route('/my_profile/')
@jwt_required()
def my_profile():
    return CustomerSchema(only=['id', 'first_name', 'last_name', 'contact_number', 'email']).dump(current_user)


# read current customer's registered pets (patients)
@customers_bp.route('/my_pets/')
@jwt_required()
def my_pets():
    return CustomerSchema(only=['patients']).dump(current_user)


# read one customer
@customers_bp.route('/<int:customer_id>/')
@jwt_required()
def get_one_customer(customer_id):
    if gb.is_admin() or is_authorized_customer(customer_id) or is_authorized_veterinarians(customer_id):
        # get one record from the customers table in the database with the given customer id
        customer = gb.required_record(Customer, customer_id)
        return CustomerSchema(exclude=['password']).dump(customer)
    else:
        return {'error': 'You are not authorized to view the information.'}, 401


# delete one customer
@customers_bp.route('/<int:customer_id>/', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    if gb.is_admin():
        # delete one record from the customers table in the database with the given customer id
        customer = gb.required_record(Customer, customer_id)
        db.session.delete(customer)
        db.session.commit()
        return {'msg': f'Customer {customer.first_name} {customer.last_name} deleted successfully'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one customer's details
@customers_bp.route('/<int:customer_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_customer(customer_id):
    if gb.is_admin() or is_authorized_customer(customer_id) or is_authorized_veterinarians(customer_id):
        # update one record in the customers table in the database with the given customer id using the information contained in the request
        customer = gb.required_record(Customer, customer_id)
        for key in list(request.json.keys()):
            setattr(customer, key, gb.required_value_converter(customer, key))
        db.session.commit()
        return CustomerSchema(exclude=['password']).dump(customer)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new customer
@customers_bp.route('/register/', methods=['POST'])
def customer_register():
    password_input = request.json.get('password')
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
    return CustomerSchema(exclude=['password']).dump(customer), 201


# customer authentication
@customers_bp.route('/login/', methods=['POST'])
def customer_login():
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
@jwt_required()
def revoke_token():
    jti = get_jwt()["jti"]
    now = datetime.now()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return {'msg': 'You logged out successfully'}