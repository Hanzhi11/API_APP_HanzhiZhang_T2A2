
from sqlalchemy.orm import validates
from init import db, ma
from marshmallow import fields
from sqlalchemy import UniqueConstraint

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
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
    customer = fields.Nested('CustomerSchema', exclude=['password', 'id'])
    appointments = fields.List(fields.Nested('AppointmentSchema'))

    class Meta:
        fields = ('id', 'name', 'age', 'weight', 'sex', 'species', 'customer_id', 'customer')