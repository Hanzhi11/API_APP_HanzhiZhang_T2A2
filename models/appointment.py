from sqlalchemy.orm import validates
from init import db, ma
from sqlalchemy import UniqueConstraint
from marshmallow import fields

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    veterinarian_id = db.Column(db.Integer, db.ForeignKey('veterinarians.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    veterinarian = db.relationship('Veterinarian', back_populates='appointments')
    patient = db.relationship('Patient', back_populates='appointments')

    __table_args__ = (
        UniqueConstraint('date', 'time', 'veterinarian_id', name='appointment_veterinarian_uc'),
        UniqueConstraint('date', 'time', 'patient_id', name='appointment_patient_uc')
        )

@validates('time')
def validate_time(time):
    print(time.strftime('%H:%M:%S').minute)

class AppointmentSchema(ma.Schema):
    patient = fields.Nested('PatientSchema', only=['name', 'age', 'weight', 'sex', 'species', 'customer_id', 'customer'])
    veterinarian = fields.Nested('VeterinarianSchema', only=['first_name', 'last_name', 'email'])

    class Meta:
        fields = ['id', 'date', 'time', 'veterinarian_id', 'veterinarian', 'patient', 'patient_id']