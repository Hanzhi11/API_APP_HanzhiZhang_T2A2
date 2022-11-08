from flask import Blueprint, request
import gb
from init import db, jwt, auto
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
        stmt = db.select(Appointment).filter_by(id=appointment_id).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id)
        result = db.session.scalar(stmt)
        if result:
            return True
    elif veterinarian_id:
        # In the appointments table, get one record with the given appointment_id and the veterinarian_id obtained from the token
        stmt = db.select(Appointment).filter_by(veterinarian_id=veterinarian_id, id=appointment_id)
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
@auto.doc()
@jwt_required()
def get_all_appointments():
    '''Admin interface - Return all appointments.'''
    if gb.is_admin():
        # get all records from the appointments table
        appointments = gb.filter_all_records(Appointment)
        return AppointmentSchema(many=True).dump(appointments)
    else:
        return {'error': 'You are not an administrator.'}, 401
        

# read all appointments of the current user
@appointments_bp.route('/my_appointments/')
@auto.doc()
@jwt_required()
def get_my_appointments():
    '''Return all appointments of the current user.'''
    if get_jwt()['role'] == 'veterinarian':
        return AppointmentSchema(many=True, exclude=['veterinarian', 'veterinarian_id']).dump(current_user.appointments)
    else:
        # get all records from the appointments table which is associated with the current customer id through the patients table
        customer_id = current_user.id
        stmt = db.select(Appointment).join(Patient, Patient.id==Appointment.patient_id).filter_by(customer_id=customer_id) 
        result = db.session.scalars(stmt)
        return AppointmentSchema(many=True, exclude=['patient']).dump(result)


# read future appointments of the current user
@appointments_bp.route('/my_appointments/future/')
@auto.doc()
@jwt_required()
def get_future_appointments():
    '''Return all future appointments of the current user.'''
    if get_jwt()['role'] == 'veterinarian':
        # get all records from the appointments table which date is later than today's date and with the current veterinarian
        future_appointments = [appointment for appointment in current_user.appointments if appointment.date > datetime.today().date()]
        if future_appointments:
            return AppointmentSchema(many=True, exclude=['veterinarian', 'veterinarian_id']).dump(future_appointments)
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
@auto.doc()
@jwt_required()
def get_previous_appointments():
    '''Return all previous appointments of the current user.'''
    if get_jwt()['role'] == 'veterinarian':
        # get all records from the appointments table which date is earlier than today's date and with the current veterinarian
        previous_appointments = [appointment for appointment in current_user.appointments if appointment.date < datetime.today().date()]
        # future_appointments = current_user.appointments.filter(Appointment.date < datetime.today())
        if previous_appointments:
            return AppointmentSchema(many=True, exclude=['veterinarian', 'veterinarian_id']).dump(previous_appointments)
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
@auto.doc()
@jwt_required()
def get_today_appointments():
    '''Return all today appointments of the current user.'''
    if get_jwt()['role'] == 'veterinarian':
        # get all records from the appointments table which date is today's date and with the current veterinarian
        today_appointments = [appointment for appointment in current_user.appointments if appointment.date == datetime.today().date()]
        if today_appointments:
            return AppointmentSchema(many=True, exclude=['veterinarian', 'veterinarian_id']).dump(today_appointments)
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
@auto.doc()
@jwt_required()
def get_one_appointment(appointment_id):
    '''Return one appointment with the given id in the format of integer as argument.'''
    appointment = gb.required_record(Appointment, appointment_id)
    if gb.is_admin() or is_appointment_authorized_person(appointment_id):
        # get one record from the appointments table with the given appointment_id
        return AppointmentSchema().dump(appointment)
    else:
       return {'error': 'You are not authorized to view the information.'}, 401


# delete one appointment
@appointments_bp.route('/<int:appointment_id>/', methods=['DELETE'])
@auto.doc()
@jwt_required()
def delete_appointment(appointment_id):
    '''Admin interface - Delete one appointment with the given id in the format of integer as argument.'''
    appointment = gb.required_record(Appointment, appointment_id)
    if gb.is_admin():
        # delete one record from the appointments table with the given appointment_id
        db.session.delete(appointment)
        db.session.commit()
        return {'msg': f'Appointment at {appointment.time} on {appointment.date} deleted successfully for patient {appointment.patient_id}'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one appointment
@appointments_bp.route('/<int:appointment_id>/', methods=['PUT', 'PATCH'])
@auto.doc()
@jwt_required()
def update_appointment(appointment_id):
    '''Update one appointment with the given id in the format of integer as argument and the key-value pairs as the request body, and then return the updated appointment. The keys are date, time, patient_id and veterinarian_id, and are all optional. The format of the values are: yyyy-mm-dd for date, hh:mm for time and mm should be one of 00, 15, 30 or 45, and integer for patient_id and veterinarian_id.'''
    appointment = gb.required_record(Appointment, appointment_id)
    if gb.is_admin() or is_appointment_authorized_person(appointment_id):
        # update one record in the appointments table with the given appointment_id using the information contained in the request
        for key in list(request.json.keys()):
            setattr(appointment, key, gb.required_value_converter(appointment, key))
        db.session.commit()
        return AppointmentSchema(exclude=['patient']).dump(appointment)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new appointment
@appointments_bp.route('/book/', methods=['POST'])
@auto.doc()
@jwt_required()
def appointment_register():
    '''Book an appointment with the key-value pairs as the request body, and reutrn the appointment created. The keys are date, time, patient_id and veterinarian_id, and are all required. The format of the values are: yyyy-mm-dd for date, hh:mm for time and mm should be one of 00, 15, 30 or 45, and integer for patient_id and veterinarian_id.'''
    date_input = request.json['date']
    date_datetime = datetime.strptime(date_input, '%Y-%m-%d').date()
    today = datetime.today().date()
    if date_datetime < today:
        return {'error': 'Invalid date.'}, 403
    elif date_datetime == today:
        return {'error': 'Booking has to be made one day in advance.'}, 403
    # check if the required patient or veterinarian exists in the database already
    patient_id_input = request.json['patient_id']
    gb.required_record(Patient, patient_id_input)
    veterinarian_id_input = request.json['veterinarian_id']
    gb.required_record(Veterinarian, veterinarian_id_input)
    if get_jwt()['role'] == 'customer':
        customer_id = current_user.id
        # get patients' id from the patients table using the current customer's id
        stmt = db.select(Patient.id).filter_by(customer_id=customer_id)
        result = db.session.scalars(stmt).all()
        if patient_id_input not in result:
            return {'error': 'You are not authorized to book an appointment for this patient.'}, 401
    elif get_jwt()['role'] == 'veterinarian' and not current_user.is_admin:
        if veterinarian_id_input != current_user.id:
            return {'error': 'You are not authorized to book an appointment for this veterinarian.'}, 401
    # add one record in the appointments table 
    appointment = Appointment(
        date = date_input,
        time = request.json['time'],
        veterinarian_id = veterinarian_id_input,
        patient_id = patient_id_input
    )
    db.session.add(appointment)
    db.session.commit()
    return AppointmentSchema(exclude=['patient']).dump(appointment), 201
