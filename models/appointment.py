from sqlalchemy.orm import validates
from init import db, ma
from sqlalchemy import UniqueConstraint
from marshmallow import fields

# Define an appointments table in the database with five columns (i.e. id, date, time, veterinarian_id and patient_id).
# In this table, id is the primary key, while veterinarian_id and patient_id are foreign keys.
# This table has a relationship with the veterinarians table and the patients table, respectively.
# As one veterinarian cannot have an appointment at the same time on the same date, the combination of date, time and veterinarian_id must be unique.
# As one patient cannot have an appointment at the same time on the same date, the combination of date, time and patient_id must be unique as well.
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
    def validate_time(self, key, value):
        print(value[3:5])
        if value[3:5] not in ['00', '15', '30', '45']:
            raise ValueError('Invalid time')
        return value

class AppointmentSchema(ma.Schema):
    patient = fields.Nested('PatientSchema', only=['name', 'age', 'weight', 'sex', 'species', 'customer_id', 'customer'])
    veterinarian = fields.Nested('VeterinarianSchema', only=['first_name', 'last_name', 'email'])

    class Meta:
        fields = ['id', 'date', 'time', 'veterinarian_id', 'veterinarian', 'patient', 'patient_id']