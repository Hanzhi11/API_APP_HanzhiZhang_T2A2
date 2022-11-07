from init import db, ma
from marshmallow import fields
from sqlalchemy.orm import validates
import re

# Define a customers table in the database with six columns (i.e. id, first_name, last_name, email, password and contact_number). Each colum has its own constraints.
# In this table, id is the primary key.
# This table has a one-to-many relationship with the patients table.
# As customers are not allowed to share one email address, email in the table must be unique.
class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.String(10), nullable=False)

    patients = db.relationship('Patient', back_populates='customer', cascade='all, delete')

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
    patients = fields.List(fields.Nested('PatientSchema', only=['name', 'age', 'weight', 'sex', 'species', 'appointments']))

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'contact_number', 'patients')

    