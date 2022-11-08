from flask import Blueprint, request
import gb
from models.patient import PatientSchema, Patient
from models.customer import Customer
from models.veterinarian import Veterinarian
from models.appointment import Appointment
from init import db, jwt, auto
from flask_jwt_extended import jwt_required, current_user, get_jwt


patients_bp = Blueprint('patients', __name__, url_prefix='/patients')


# check if the person who has logged in has been authorized
def is_patient_authorized_person(patient_id):
    customer_id = gb.get_customer_id()
    veterinarian_id = gb.get_veterinarian_id()
    if customer_id:
        # get one record from the patients table with the given patient id and the customer id obtained from the token
        stmt = db.select(Patient).filter_by(customer_id=customer_id, id=patient_id)
        result = db.session.scalar(stmt)
        if result:
            return True
    elif veterinarian_id:
        # get one record from the appointments table with the given patient id and the veterinarian id obtained from the token
        stmt = db.select(Appointment).filter_by(veterinarian_id=veterinarian_id, patient_id=patient_id)
        result = db.session.scalar(stmt)
        if result:
            return True


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    if jwt_data['role'] == 'veterinarian':
        return Veterinarian.query.filter_by(id=identity).one_or_none()
    else:
        return Customer.query.filter_by(id=identity).one_or_none()


# read all patients
@patients_bp.route('/')
@auto.doc()
@jwt_required()
def get_all_patients():
    '''Admin interface - Return the full details of all the patients'''
    if gb.is_admin():
        # get all records from the patients table in the database
        stmt = db.select(Patient)
        patients = db.session.scalars(stmt)
        return PatientSchema(many=True).dump(patients)
    else:
        return {'error': 'You are not an administrator.'}, 401


# read one patient
@patients_bp.route('/<int:patient_id>/')
@auto.doc()
@jwt_required()
def get_one_patient(patient_id):
    '''Return one patient with the given id'''
    patient = gb.required_record(Patient, patient_id)
    if gb.is_admin() or is_patient_authorized_person(patient_id):
        # get one record from the patients table in the database with the given patient id
        return PatientSchema().dump(patient)
    else:
        return {'error': 'You are not authorized to view the information.'}, 401


# read current user's patients
@patients_bp.route('/my_patients/')
@auto.doc()
@jwt_required()
def my_patients():
    '''Return all the patients for the current user'''
    if get_jwt()['role'] == 'veterinarian':
        veterinarian_id = current_user.id
        stmt = db.select(Patient). join(Appointment, Patient.id==Appointment.patient_id).filter_by(veterinarian_id=veterinarian_id)
        result = db.session.scalars(stmt)
        return PatientSchema(many=True).dump(result)
    else:
        return PatientSchema(many=True, exclude=['customer', 'customer_id']).dump(current_user.patients)


# delete one patient
@patients_bp.route('/<int:patient_id>/', methods=['DELETE'])
@auto.doc()
@jwt_required()
def delete_patient(patient_id):
    '''Admin Interface - Delete one patient with the given id'''
    patient = gb.required_record(Patient, patient_id)
    if gb.is_admin():
        # delete one record from the patients table in the database with the given patient id
        db.session.delete(patient)
        db.session.commit()
        return {'msg': f'Patient {patient.name} deleted successfully'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one patient
@patients_bp.route('/<int:patient_id>/', methods=['PUT', 'PATCH'])
@auto.doc()
@jwt_required()
def update_patient(patient_id):
    '''Update one patient with the given id and return the updated patient'''
    patient = gb.required_record(Patient, patient_id)
    if gb.is_admin() or is_patient_authorized_person(patient_id):
        # update one record in the patients table in the database with the given patient id using the information contained in the request
        for key in list(request.json.keys()-['patient']):
            setattr(patient, key, gb.required_value_converter(patient, key))
        db.session.commit()
        return PatientSchema().dump(patient)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new patient
@patients_bp.route('/register/', methods=['POST'])
@auto.doc()
@jwt_required()
def patient_register():
    '''Patient registration and return the created patient'''
    # add a new record to the patients table in the database
    patient = Patient(
        name = request.json['name'],
        age = request.json['age'],
        weight = request.json['weight'],
        sex = request.json['sex'],
        species = request.json['species'],
        customer_id = request.json['customer_id']
    )
    db.session.add(patient)
    db.session.commit()
    return PatientSchema().dump(patient), 201
