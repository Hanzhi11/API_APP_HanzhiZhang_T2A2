from flask import Blueprint, request
from init import db, bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.customer import CustomerSchema, Customer
import re, gb
from sqlalchemy.exc import IntegrityError

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
def get_all_customers():
    customers = gb.filter_all_records(Customer)
    return CustomerSchema(many=True, exclude=['password']).dump(customers)

@customers_bp.route('/<int:customer_id>/')
def get_one_customer(customer_id):
    customer = gb.required_record(Customer, customer_id)
    return CustomerSchema(exclude=['password']).dump(customer)


@customers_bp.route('/<int:customer_id>/', methods=['DELETE'])
def delete_customer(customer_id):
    customer = gb.required_record(Customer, customer_id)
    db.session.delete(customer)
    db.session.commit()
    return {'msg': f'Customer {customer.first_name} {customer.last_name} deleted successfully'}


@customers_bp.route('/<int:customer_id>/', methods=['PUT', 'PATCH'])
def update_customer(customer_id):
    customer = gb.required_record(Customer, customer_id)
    try:
        for key in list(request.json.keys()):
            setattr(customer, key, gb.required_value_converter(customer, key))
        db.session.commit()
        return CustomerSchema(exclude=['password']).dump(customer)
    except IntegrityError:
        return {'error': 'Email address exists already'}, 409

@customers_bp.route('/register/', methods=['POST'])
def customer_register():
    password_input = request.json.get('password')
    gb.validate_password(password_input)
    try:
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
    except IntegrityError:
        return {'error': 'Email address exists already'}, 409
    except KeyError as e:
        return {'error': f'{e.args[0]} is missing'}, 400