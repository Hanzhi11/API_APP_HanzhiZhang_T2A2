from flask import Blueprint, request
import gb
from init import db, jwt
from models.appointment import AppointmentSchema, Appointment
from models.patient import Patient
from models.customer import Customer
from models.veterinarian import Veterinarian
from flask_jwt_extended import jwt_required, get_jwt, current_user
from datetime import datetime


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


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    if jwt_data['role'] == 'veterinarian':
        return Veterinarian.query.filter_by(id=identity).one_or_none()
    else:
        return Customer.query.filter_by(id=identity).one_or_none()


# read all appointments
@appointments_bp.route('/')
@jwt_required()
def get_all_appointments():
    if gb.is_admin():
        # get all records from the appointments table
        appointments = gb.filter_all_records(Appointment)
        return AppointmentSchema(many=True).dump(appointments)
    else:
        return {'error': 'You are not an administrator.'}, 401
        

# read all appointments of the current user
@appointments_bp.route('/my_appointments/')
@jwt_required()
def get_my_appointments():
    if get_jwt()['role'] == 'veterinarian':
        return AppointmentSchema(many=True, exclude=['patient.name']).dump(current_user.appointments)
    else:
        # get all records from the appointments table which is associated with the current customer id through the patients table
        customer_id = current_user.id
        stmt = db.select(Appointment).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id) 
        result = db.session.scalars(stmt)
        return AppointmentSchema(many=True, exclude=['patient']).dump(result)


# read future appointments of the current user
@appointments_bp.route('/my_appointments/future/')
@jwt_required()
def get_future_appointments():
    print(get_jwt()['role'])
    if get_jwt()['role'] == 'veterinarian':
        # get all records from the appointments table which date is later than today's date and with the current veterinarian
        future_appointments = [appointment for appointment in current_user.appointments if appointment.date > datetime.today().date()]
        if future_appointments:
            return AppointmentSchema(many=True).dump(future_appointments)
        else:
            return {'msg': 'No appointments found'}, 404
    else:
        # get all records from the appointments table which date is later than today's date and are associated with the current customer throuth the patients table
        customer_id = current_user.id
        stmt = db.select(Appointment).join(Patient, Patient.id==Appointment.patient_id).filter(customer_id==customer_id, Appointment.date > datetime.today().date())
        result = db.session.scalars(stmt).all()
        if result:
            return AppointmentSchema(many=True, exclude=['patient']).dump(result)
        else:
            return {'msg': 'No appointments found'}, 404


# read previous appointments of the current user
@appointments_bp.route('/my_appointments/previous/')
@jwt_required()
def get_previous_appointments():
    if get_jwt()['role'] == 'veterinarian':
        # get all records from the appointments table which date is earlier than today's date and with the current veterinarian
        previous_appointments = [appointment for appointment in current_user.appointments if appointment.date < datetime.today().date()]
        # future_appointments = current_user.appointments.filter(Appointment.date < datetime.today())
        if previous_appointments:
            return AppointmentSchema(many=True).dump(previous_appointments)
        else:
            return {'msg': 'No appointments found'}, 404
    else:
        # get all records from the appointments table which date is earlier than today's date and are associated with the current customer throuth the patients table
        customer_id = current_user.id
        stmt = db.select(Appointment).join(Patient, Patient.id==Appointment.patient_id).filter(customer_id==customer_id, Appointment.date < datetime.today().date())
        result = db.session.scalars(stmt).all()
        if result:
            return AppointmentSchema(many=True, exclude=['patient']).dump(result)
        else:
            return {'msg': 'No appointments found'}, 404


# read today's appointments of the current user
@appointments_bp.route('/my_appointments/today/')
@jwt_required()
def get_today_appointments():
    if get_jwt()['role'] == 'veterinarian':
        # get all records from the appointments table which date is today's date and with the current veterinarian
        today_appointments = [appointment for appointment in current_user.appointments if appointment.date == datetime.today().date()]
        if today_appointments:
            return AppointmentSchema(many=True).dump(today_appointments)
        else:
            return {'msg': 'No appointments found'}, 404
    else:
        # get all records from the appointments table which date is today's date and are associated with the current customer throuth the patients table
        customer_id = current_user.id
        stmt = db.select(Appointment).join(Patient, Patient.id==Appointment.patient_id).filter(customer_id==customer_id, Appointment.date==datetime.today().date())
        result = db.session.scalars(stmt).all()
        if result:
            return AppointmentSchema(many=True, exclude=['patient']).dump(result)
        else:
            return {'msg': 'No appointments found'}, 404


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
