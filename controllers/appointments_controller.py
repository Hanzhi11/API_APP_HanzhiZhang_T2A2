from flask import Blueprint, request, abort
import gb
from init import db
from models.appointment import AppointmentSchema, Appointment
from sqlalchemy.exc import IntegrityError


appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/')
@jwt_required()
def get_all_appointments():
    if gb.is_admin():
        appointments = gb.filter_all_records(Appointment)
        return AppointmentSchema(many=True).dump(appointments)
    else:
        abort(401)

@appointments_bp.route('/<int:appointment_id>/')
@jwt_required()
def get_one_appointment(appointment_id):
    if gb.is_admin() or gb.is_appointment_authorized_person(appointment_id):
        appointment = gb.required_record(Appointment, appointment_id)
        return AppointmentSchema().dump(appointment)
    else:
        abort(401)

@appointments_bp.route('/<int:appointment_id>/', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    if gb.is_admin():
        appointment = gb.required_record(Appointment, appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return {'msg': f'Appointment at {appointment.time} on {appointment.date} deleted successfully for patient {appointment.patient_id}'}
    else:
        abort(401)


@appointments_bp.route('/<int:appointment_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_appointment(appointment_id):
    if gb.is_admin() or gb.is_appointment_authorized_person(appointment_id):
        appointment = gb.required_record(Appointment, appointment_id)
        for key in list(request.json.keys()):
            setattr(appointment, key, gb.required_value_converter(appointment, key))
        db.session.commit()
        return AppointmentSchema().dump(appointment)
    else:
        abort(401)


@appointments_bp.route('/book/', methods=['POST'])
@jwt_required()
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
