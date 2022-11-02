from flask import Blueprint, request, abort
import gb
from models.patient import PatientSchema, Patient
from init import db
from flask_jwt_extended import jwt_required


patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patients_bp.route('/')
@jwt_required()
def get_all_patients():
    if gb.is_admin():
        stmt = db.select(Patient)
        patients = db.session.scalars(stmt)
        return PatientSchema(many=True).dump(patients)
    else:
        abort(401)

@patients_bp.route('/<int:patient_id>/')
@jwt_required()
def get_one_patient(patient_id):
    if gb.is_admin() or gb.is_patient_authorized_person(patient_id):
        patient = gb.required_record(Patient, patient_id)
        return PatientSchema().dump(patient)
    else:
        abort(401)

@patients_bp.route('/<int:patient_id>/', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    if gb.is_admin():
        patient = gb.required_record(Patient, patient_id)
        db.session.delete(patient)
        db.session.commit()
        return {'msg': f'Patient {patient.name} deleted successfully'}
    else:
        abort(401)

@patients_bp.route('/<int:patient_id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_patient(patient_id):
    if gb.is_admin() or gb.is_patient_authorized_person(patient_id):
        patient = gb.required_record(Patient, patient_id)
        for key in list(request.json.keys()-['patient']):
            setattr(patient, key, gb.required_value_converter(patient, key))
        db.session.commit()
        return PatientSchema().dump(patient)
    else:
        abort(401)


@patients_bp.route('/register/', methods=['POST'])
@jwt_required()
def patient_register():
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