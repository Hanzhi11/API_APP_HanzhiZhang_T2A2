from flask import Blueprint
from init import db, bcrypt
from models.customer import Customer
from models.veterinarian import Veterinarian
from models.patient import Patient
from models.appointment import Appointment
from datetime import datetime


db_commands = Blueprint('db', __name__)


# create all defined tables in the database
@db_commands.cli.command('create')
def create_db():
    db.create_all()
    print('Tables created')


# drop all tables in the database
@db_commands.cli.command('drop')
def drop_db():
    db.drop_all()
    print('Tables droped')


# seed all tables (i.e. customers, patients, appointments, veterinarians) in the database
@db_commands.cli.command('seed')
def seed_db():
    customers = [
        Customer(
            first_name = 'Harry',
            last_name = 'Porter',
            email = 'harryporter@test.com',
            password = bcrypt.generate_password_hash('HarryPorter1!').decode('utf-8'),
            contact_number = '0412341234'
        ),
        Customer(
            first_name = 'Ham',
            last_name = 'Port',
            email = 'hamport@test.com',
            password = bcrypt.generate_password_hash('Hamport1!').decode('utf-8'),
            contact_number = '0412344321'
        ),
        Customer(
            first_name = 'Rod',
            last_name = 'Stone',
            email = 'rodstone@test.com',
            password = bcrypt.generate_password_hash('Rodstone2$').decode('utf-8'),
            contact_number = '0733441234'
        )
    ]
    db.session.add_all(customers)
    db.session.commit()
    veterinarians = [
        Veterinarian(
            first_name = 'Sam',
            last_name = 'Sky',
            email = 'samsky@vet.com',
            password = bcrypt.generate_password_hash('Samsky1?').decode('utf-8'),
            description = 'Lorem ipsum dolor sit amet.',
            sex = 'Male',
            languages = ['Korean', 'French'],
            is_admin = True
        ),
        Veterinarian(
            first_name = 'Sammy',
            last_name = 'Soil',
            email = 'sammysoil@vet.com',
            password = bcrypt.generate_password_hash('sammys1!').decode('utf-8'),
            description = 'Lorem ipsum dolor sit amet lorem ipsum dolor sit amet.',
            sex = 'Female'
        ),
        Veterinarian(
            first_name = 'Gigi',
            last_name = 'Sky',
            email = 'gigisky@vet.com',
            password = bcrypt.generate_password_hash('gigis11!').decode('utf-8'),
            sex = 'Male'
        ),
        Veterinarian(
            first_name = 'Lucy',
            last_name = 'Land',
            email = 'luckland@vet.com',
            password = bcrypt.generate_password_hash('lland01!').decode('utf-8'),
            sex = 'Female'
        )
    ]
    db.session.add_all(veterinarians)
    db.session.commit()
    patients = [
        Patient(
            name = 'Lily',
            age = 10,
            weight = 8,
            sex = 'Female',
            species = 'dog',
            customer_id = 1
        ),
        Patient(
            name = 'Jan',
            age = 1,
            weight = 5.2,
            sex = 'Male',
            species = 'cat',
            customer_id = 2
        ),
        Patient(
            name = 'April',
            age = 2,
            weight = 6.1,
            sex = 'Male',
            species = 'rabbit',
            customer_id = 2
        ),
        Patient(
            name = 'July',
            age = 10,
            weight = 2,
            sex = 'Male',
            species = 'bird',
            customer_id = 3
        )
    ]
    db.session.add_all(patients)
    db.session.commit()
    appointments = [
        Appointment(
            date = '2022-11-3',
            time = '10:15',
            veterinarian_id = 3,
            patient_id = 3,
        ),
        Appointment(
            date = '2022-11-4',
            time = '10:30',
            veterinarian_id = 3,
            patient_id = 2,
        ),
        Appointment(
            date = '2022-11-2',
            time = '10:45',
            veterinarian_id = 1,
            patient_id = 4,
        ),
        Appointment(
            date = '2022-11-2',
            time = '10:00',
            veterinarian_id = 4,
            patient_id = 1,
        ),
        Appointment(
            date = '2022-11-3',
            time = '10:30',
            veterinarian_id = 2,
            patient_id = 4,
        )
    ]
    db.session.add_all(appointments)
    db.session.commit()
    print('Tables seeded')
