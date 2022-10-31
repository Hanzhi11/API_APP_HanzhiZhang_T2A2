from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length, Regexp, And
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

class VeterinarianSchema(ma.Schema):
    # password = fields.String(required=True, validate=Regexp('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', error='Password must contain minimum 8 characters, at lease one letter, one number and one special characters'))
    # email = fields.String(required=True, validate=Regexp('^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$', error='Invalid email address'))

        
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'description', 'sex', 'languages', 'is_admin')