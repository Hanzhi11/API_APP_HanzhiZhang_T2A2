from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length, Email, Regexp

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.Integer, nullable=False)

class CustomerSchema(ma.Schema):
    password = fields.String(required=True, validate=Regexp('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', error='Password must contain minimum 8 characters, at lease one letter, one number and one special characters'))
    email = fields.String(required=True, validate=Email(error='Invalid email address'))
    contact_number = fields.Integer(required=True, validate=Length(equal=9, error='Invalid contact number'))

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'contact_number')