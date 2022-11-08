
from sqlalchemy.orm import validates
from init import db, ma
from marshmallow import fields
from sqlalchemy import UniqueConstraint
import enum
from marshmallow_enum import EnumField


# Define a patients table in the database with seven columns (i.e. id, name, age, weight, sex, species and customer_id). Each colum has its own constraints.
# In this table, id is the primary key, while customer_id is the foreign key.
# This table has a relationship with the customers table and the appointments table (one-to-many), respectively.
# As one customer are not allowed to have many patients with the same name, the combination of name and customer_id must be unique.
class SpeciesEnum(enum.Enum):
    dog = 1
    cat = 2
    bird = 3
    fish = 4
    rabbit = 5

class SexEnum(enum.Enum):
    Male = 1
    Female = 2

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(4, 2), nullable=False)
    sex = db.Column(db.Enum(SexEnum), nullable=False)
    species = db.Column(db.Enum(SpeciesEnum), nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    customer = db.relationship('Customer', back_populates='patients')
    appointments = db.relationship('Appointment', back_populates='patient', cascade='all, delete')

    __table_args__ = (UniqueConstraint('customer_id', 'name', name='customer_patient_uc'),)

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError(f'Invalid {key}')
        return value

    @validates('sex')
    def validate_sex(self, key, value):
        if value not in ['Male', 'Female']:
            raise ValueError('Invalid sex. Sex must be Male or Female.')
        return value

    @validates('age')
    def validate_age(self, key, value):
        if not isinstance(value, int):
            raise TypeError('Age must be an integer.')
        elif value < 0:
            raise ValueError('Age must be greater than 0.')
        return value

    @validates('weight')
    def validate_weight(self, key, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError('Weight must be a number.')
        elif value < 0.01 or value > 99.99:
            raise ValueError('Weight should be between 0.01 and 99.99.')
        return value

class PatientSchema(ma.Schema):
    customer = fields.Nested('CustomerSchema', only=['first_name', 'last_name', 'email', 'contact_number'])
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'veterinarian', 'veterinarian_id']))
    sex = EnumField(SexEnum)
    species = EnumField(SpeciesEnum)

    class Meta:
        fields = ('id', 'name', 'age', 'weight', 'sex', 'species', 'customer_id', 'customer', 'appointments')