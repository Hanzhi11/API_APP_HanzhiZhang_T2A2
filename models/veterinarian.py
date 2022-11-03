from init import db, ma
from marshmallow import fields
from sqlalchemy.orm import validates
import re, enum
from marshmallow_enum import EnumField

# Define a veterinarians table in the database with nine columns (i.e. id, first_name, last_name, email, password, description, sex, languages and is_admin). Each column has its own contraints.
# In this table, id is the primary key.
# This table has a one-to-many relationship with the appointments table.
# As veterinarians are not allowed to share one email address, email in the table must be unique.
class LanguagesEnum(enum.Enum):
    Mandarin = 1
    Cantonese = 2
    Korean = 3
    Japanese = 4
    Spanish = 5
    French = 6

class SexEnum(enum.Enum):
    Male = 1
    Female = 2

class Veterinarian(db.Model):
    __tablename__ = 'veterinarians'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    sex = db.Column(db.Enum(SexEnum), nullable=False)
    languages = db.Column(db.ARRAY(db.Enum(LanguagesEnum)))
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

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise ValueError(f'The value must be True or False for {key}')
        return value
    

class VeterinarianSchema(ma.Schema):
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'patient_id', 'patient']))
    sex = EnumField(SexEnum)
    languages = fields.List(EnumField(LanguagesEnum))

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'description', 'sex', 'languages', 'is_admin', 'appointments')
