from flask import Blueprint, request
import gb
from init import db
from models.appointment import AppointmentSchema, Appointment
from sqlalchemy.exc import IntegrityError


appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/')
def get_all_appointments():
    appointments = gb.filter_all_records(Appointment)
    return AppointmentSchema(many=True).dump(appointments)

@appointments_bp.route('/<int:appointment_id>/')
def get_one_appointment(appointment_id):
    appointment = gb.required_record(Appointment, appointment_id)
    return AppointmentSchema().dump(appointment)

@appointments_bp.route('/<int:appointment_id>/', methods=['DELETE'])
def delete_appointment(appointment_id):
    appointment = gb.required_record(Appointment, appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return {'msg': f'Appointment at {appointment.time} on {appointment.date} deleted successfully for patient {appointment.patient_id}'}


@appointments_bp.route('/<int:appointment_id>/', methods=['PUT', 'PATCH'])
def update_appointment(appointment_id):
    appointment = gb.required_record(Appointment, appointment_id)
    for key in list(request.json.keys()):
        setattr(appointment, key, gb.required_value_converter(appointment, key))
    db.session.commit()
    return AppointmentSchema().dump(appointment)


@appointments_bp.route('/book/', methods=['POST'])
def appointment_register():
    appointment = Appointment(
        date = request.json['date'],
        time = request.json['time'],
        veterinarian_id = request.json['veterinarian_id'],
        patient_id = request.json['patient_id']
    )
    db.session.add(appointment)
    db.session.commit()
    return AppointmentSchema().dump(appointment), 201
