from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length, Regexp, And
from sqlalchemy.orm import validates
import re


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.String(10), nullable=False)

    @validates('last_name', 'first_name')
    def validate_last_name(self, key, value):
        if len(value) == 0:
            raise ValueError(f'Invalid {key}')
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not re.match('^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$', value):
            raise ValueError('Invalid email')
        return value

    @validates('contact_number')
    def validate_contact_number(self, key, value):
        if len(value) != 10:
            raise ValueError('Length of contact number must be 10')
        if not re.match('^0[0-9]*$', value):
            raise ValueError('Contact number must contain numbers only and start with 0')
        return value

class CustomerSchema(ma.Schema):
    # password = fields.String(required=True, validate=Regexp('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', error='Password must contain minimum 8 characters, at lease one letter, one number and one special characters'))
    # email = fields.String(required=True, validate=Regexp('^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$', error='Invalid email address'))
    # contact_number = fields.String(required=True, validate=And(Length(equal=10, error='Length of contact number must be 10'), Regexp('^[0-9]*{10, 10}$', error='Contact number must contain numbers only')))

        
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'contact_number')

    