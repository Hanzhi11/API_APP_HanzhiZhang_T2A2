from init import db, ma
from marshmallow import fields
from sqlalchemy.orm import validates
import re


class Veterinarian(db.Model):
    __tablename__ = 'veterinarians'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    sex = db.Column(db.String(6), nullable=False)
    languages = db.Column(db.String)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    appointments = db.relationship('Appointment', back_populates='veterinarian', cascade='all, delete')

    @validates('last_name', 'first_name')
    def validate_last_name(self, key, value):
        if len(value) == 0:
            raise ValueError(f'Invalid {key}')
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not re.match('^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@vet+(\.com)+$', value):
            raise ValueError('Invalid email')
        return value

    @validates('sex')
    def validate_sex(self, key, value):
        if value not in ['Male', 'Female']:
            raise ValueError('Invalid sex')
        return value

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise ValueError(f'The value must be True or False for {key}')
        return value
    

class VeterinarianSchema(ma.Schema):
    # password = fields.String(required=True, validate=Regexp('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', error='Password must contain minimum 8 characters, at lease one letter, one number and one special characters'))
    # email = fields.String(required=True, validate=Regexp('^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$', error='Invalid email address'))
    # first_name = fields.String(required=True, validate=Length(min=1, error='invalid first name'))
    # last_name = fields.String(required=True, validate=Length(min=1, error="invalid last name"))
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'patient_id', 'patient']))

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'description', 'sex', 'languages', 'is_admin', 'appointments')
