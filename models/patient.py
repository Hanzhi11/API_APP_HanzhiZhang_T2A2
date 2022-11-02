
from sqlalchemy.orm import validates
from init import db, ma
from marshmallow import fields
from sqlalchemy import UniqueConstraint


# Define a patients table in the database with seven columns (i.e. id, name, age, weight, sex, species and customer_id).
# In this table, id is the primary key, while customer_id is the foreign key.
# This table has a relationship with the customers table and the appointments table (one-to-many), respectively.
# As one customer are not allowed to have many patients with the same name, the combination of name and customer_id must be unique.
class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    sex = db.Column(db.String(6), nullable=False)
    species = db.Column(db.String, nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    customer = db.relationship('Customer', back_populates='patients')
    appointments = db.relationship('Appointment', back_populates='patient', cascade='all, delete')

    __table_args__ = (UniqueConstraint('customer_id', 'name', name='customer_patient_uc'),)

    @validates('name')
    def validate_name(self, key, value):
        if len(value) == 0:
            raise ValueError(f'Invalid {key}')
        return value

    @validates('sex')
    def validate_sex(self, key, value):
        if value not in ['Male', 'Female']:
            raise ValueError('Invalid sex. Sex must be Male or Female.')
        return value

    @validates('species')
    def validate_species(self, key, value):
        if value not in ['dog', 'cat','bird', 'fish', 'rabbit']:
            raise ValueError('Invalid species. Species must be dog, cat, bird, fish or rabbit.')
        return value

class PatientSchema(ma.Schema):
    customer = fields.Nested('CustomerSchema', only=['first_name', 'last_name', 'email', 'contact_number'])
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'veterinarian', 'veterinarian_id']))

    class Meta:
        fields = ('id', 'name', 'age', 'weight', 'sex', 'species', 'customer_id', 'customer', 'appointments')