from flask import Blueprint, request
from init import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.customer import CustomerSchema, Customer

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
        return {'msg': f'Customer {customer_id} deleted successfully'}
    else:
        return {'error': f'Customer with id {customer_id} not found'}, 404