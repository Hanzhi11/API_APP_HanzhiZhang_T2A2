from flask import Blueprint, request
from init import db, bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.customer import CustomerSchema, Customer
import re

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
def get_all_customers():
    stmt = db.select(Customer)
    customers = db.session.scalars(stmt)
    return CustomerSchema(many=True, exclude=['password']).dump(customers)

@customers_bp.route('/<int:customer_id>/')
def get_one_customer(customer_id):
    stmt = db.select(Customer).filter_by(id=customer_id)
    customer = db.session.scalar(stmt)
    if customer:
        return CustomerSchema(exclude=['password']).dump(customer)
    else:
        return {'error': f'Customer with id {customer_id} not found'}, 404

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    stmt = db.select(Customer).filter_by(id=customer_id)
    customer = db.session.scalar(stmt)
    print(customer)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return {'msg': f'Customer {customer.first_name} {customer.last_name} deleted successfully'}
    else:
        return {'error': f'Customer with id {customer_id} not found'}, 404

@customers_bp.route('/<int:customer_id>', methods=['PUT', 'PTACH'])
def update_customer(customer_id):
    stmt = db.select(Customer).filter_by(id=customer_id)
    customer = db.session.scalar(stmt)
    if customer:
        customer.first_name = request.json.get('first_name') or customer.first_name
        customer.last_name = request.json.get('last_name') or customer.last_name
        customer.contact_number = request.json.get('contact_number') or customer.contact_number
        customer.email = request.json.get('email') or customer.email
        new_password = request.json.get('password')
        if new_password:
            if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', new_password):
                raise ValueError('Password must contain minimum 8 characters, at lease one letter, one number and one special characters')
            customer.password = bcrypt.generate_password_hash(new_password).decode('utf-8'),
        else:
            customer.password = customer.password
        db.session.commit()
        return CustomerSchema(exclude=['password']).dump(customer)
    else:
        return {'error': f'Customer with id {customer_id} not found'}, 404