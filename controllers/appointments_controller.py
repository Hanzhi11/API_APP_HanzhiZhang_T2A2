from flask import Blueprint, request
import gb
from init import db
from models.appointment import AppointmentSchema, Appointment
from models.patient import Patient
from flask_jwt_extended import jwt_required


appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')


# check if the person is authorized
def is_appointment_authorized_person(appointment_id):
    customer_id = gb.get_customer_id()
    veterinarian_id = gb.get_veterinarian_id()
    if customer_id:
        # Through the relationships among the appointments, patients and customers tables, get one record from the appointments table using the given appointment_id and the customer_id obtained from the token
        stmt = db.select(Appointment).filter_by(appointment_id=id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id)
        result = db.session.scalar(stmt)
        if result:
            return True
    elif veterinarian_id:
        # In the appointments table, get one record with the given appointment_id and the veterinarian_id obtained from the token
        stmt = db.select(Appointment).filter_by(veterinarian_id=veterinarian_id, appointment_id=appointment_id)
        result = db.session.scalar(stmt)
        if result:
            return True


# get all appointments with one veterinarian
def filter_all_records(id):
    stmt = db.select(Appointment).filter_by(veterinarian_id=id)
    return db.session.scalars(stmt)

# read all appointments
@appointments_bp.route('/admin')
@jwt_required()
def get_all_appointments():
    if gb.is_admin():
        # get all records from the appointments table
        appointments = gb.filter_all_records(Appointment)
        return AppointmentSchema(many=True).dump(appointments)
    else:
        return {'error': 'You are not an administrator.'}, 401
        

# read all appointments of the veterinarian who has logged in
@appointments_bp.route('/')
@jwt_required()
def get_veterinarian_all_appointments():
    id = gb.get_veterinarian_id()
    appointments = filter_all_records(id)
    return AppointmentSchema(many=True).dump(appointments)


# read one appointment
@appointments_bp.route('/<int:appointment_id>/')
@jwt_required()
def get_one_appointment(appointment_id):
    if gb.is_admin() or is_appointment_authorized_person(appointment_id):
        # get one record from the appointments table with the given appointment_id
        appointment = gb.required_record(Appointment, appointment_id)
        return AppointmentSchema().dump(appointment)
    else:
       return {'error': 'You are not authorized to view the information.'}, 401


# delete one appointment
@appointments_bp.route('/<int:appointment_id>/', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    if gb.is_admin():
        # delete one record from the appointments table with the given appointment_id
        appointment = gb.required_record(Appointment, appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return {'msg': f'Appointment at {appointment.time} on {appointment.date} deleted successfully for patient {appointment.patient_id}'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one appointment
@appointments_bp.route('/<int:appointment_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_appointment(appointment_id):
    if gb.is_admin() or is_appointment_authorized_person(appointment_id):
        # update one record in the appointments table with the given appointment_id using the information contained in the request
        appointment = gb.required_record(Appointment, appointment_id)
        for key in list(request.json.keys()):
            setattr(appointment, key, gb.required_value_converter(appointment, key))
        db.session.commit()
        return AppointmentSchema().dump(appointment)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new appointment
@appointments_bp.route('/book/', methods=['POST'])
@jwt_required()
def appointment_register():
    # add one record in the appointments table 
    appointment = Appointment(
        date = request.json['date'],
        time = request.json['time'],
        veterinarian_id = request.json['veterinarian_id'],
        patient_id = request.json['patient_id']
    )
    db.session.add(appointment)
    db.session.commit()
    return AppointmentSchema().dump(appointment), 201
