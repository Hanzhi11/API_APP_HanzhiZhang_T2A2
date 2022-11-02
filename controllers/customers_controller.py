from flask import Blueprint, request
from init import db, bcrypt
from flask_jwt_extended import jwt_required, create_access_token
from models.customer import CustomerSchema, Customer
from models.appointment import Appointment
from models.patient import Patient
import gb
from datetime import timedelta


customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

def is_authorized_veterinarians(customer_id):
    id = gb.get_veterinarian_id()
    if id:
        stmt = db.select(Appointment).filter_by(veterinarian_id=id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id)
        result = db.session.scalar(stmt)
        print(result)
        if result:
            return True

def is_authorized_customer(customer_id):
    id = gb.get_customer_id()
    if id == customer_id:
        return True

@customers_bp.route('/')
@jwt_required()
def get_all_customers():
    if gb.is_admin():
        customers = gb.filter_all_records(Customer)
        return CustomerSchema(many=True, exclude=['password']).dump(customers)
    else:
        return {'error': 'You are not an administrator.'}, 401

@customers_bp.route('/<int:customer_id>/')
@jwt_required()
def get_one_customer(customer_id):
    if is_authorized_customer(customer_id) or gb.is_admin():
        customer = gb.required_record(Customer, customer_id)
        return CustomerSchema(exclude=['password']).dump(customer)
    else:
        return {'error': 'You are not authorized to view the information.'}, 401

@customers_bp.route('/<int:customer_id>/', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    if gb.is_admin():
        customer = gb.required_record(Customer, customer_id)
        db.session.delete(customer)
        db.session.commit()
        return {'msg': f'Customer {customer.first_name} {customer.last_name} deleted successfully'}
    else:
        return {'error': 'You are not an administrator.'}, 401


@customers_bp.route('/<int:customer_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_customer(customer_id):
    if gb.is_admin() or is_authorized_customer(customer_id) or is_authorized_veterinarians(customer_id):
        customer = gb.required_record(Customer, customer_id)
        for key in list(request.json.keys()):
            setattr(customer, key, gb.required_value_converter(customer, key))
        db.session.commit()
        return CustomerSchema(exclude=['password']).dump(customer)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


@customers_bp.route('/register/', methods=['POST'])
def customer_register():
    password_input = request.json.get('password')
    gb.validate_password(password_input)
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

@customers_bp.route('/login/', methods=['POST'])
def customer_login():
    email=request.json['email']
    password = request.json['password']
    customer = gb.filter_one_record_by_email(Customer, email)
    if customer and bcrypt.check_password_hash(customer.password, password):
        identity = ''.join(['C', str(customer.id)])
        token = create_access_token(identity=identity, expires_delta=timedelta(days=1))
        return {'email': customer.email, 'token': token}
    else:
        return {'error': 'Invalid email or passord'}, 401

