from flask import Blueprint, request
import gb
from models.patient import PatientSchema, Patient
from models.appointment import Appointment
from init import db
from flask_jwt_extended import jwt_required


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


# read all patients
@patients_bp.route('/')
@jwt_required()
def get_all_patients():
    if gb.is_admin():
        # get all records from the patients table in the database
        stmt = db.select(Patient)
        patients = db.session.scalars(stmt)
        return PatientSchema(many=True).dump(patients)
    else:
        return {'error': 'You are not an administrator.'}, 401


# read one patient
@patients_bp.route('/<int:patient_id>/')
@jwt_required()
def get_one_patient(patient_id):
    if gb.is_admin() or is_patient_authorized_person(patient_id):
        # get one record from the patients table in the database with the given patient id
        patient = gb.required_record(Patient, patient_id)
        return PatientSchema().dump(patient)
    else:
        return {'error': 'You are not authorized to view the information.'}, 401


# delete one patient
@patients_bp.route('/<int:patient_id>/', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    if gb.is_admin():
        # delete one record from the patients table in the database with the given patient id
        patient = gb.required_record(Patient, patient_id)
        db.session.delete(patient)
        db.session.commit()
        return {'msg': f'Patient {patient.name} deleted successfully'}
    else:
        return {'error': 'You are not an administrator.'}, 401


# update one patient
@patients_bp.route('/<int:patient_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_patient(patient_id):
    if gb.is_admin() or is_patient_authorized_person(patient_id):
        # update one record in the patients table in the database with the given patient id using the information contained in the request
        patient = gb.required_record(Patient, patient_id)
        for key in list(request.json.keys()-['patient']):
            setattr(patient, key, gb.required_value_converter(patient, key))
        db.session.commit()
        return PatientSchema().dump(patient)
    else:
        return {'error': 'You are not authorized to update the information.'}, 401


# create a new patient
@patients_bp.route('/register/', methods=['POST'])
@jwt_required()
def patient_register():
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