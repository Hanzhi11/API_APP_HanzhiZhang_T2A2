from flask import Blueprint
from init import db, bcrypt
from models.customer import Customer
from models.veterinarian import Veterinarian

db_commands = Blueprint('db', __name__)

@db_commands.cli.command('create')
def create_db():
    db.create_all()
    print('Tables created')

@db_commands.cli.command('drop')
def drop_db():
    db.drop_all()
    print('Tables droped')

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
            languages = 'Korean',
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
            first_name = 'Lucy',
            last_name = 'Land',
            email = 'luckland@vet.com',
            password = bcrypt.generate_password_hash('lland01!').decode('utf-8'),
            sex = 'Female'
        )
    ]

    db.session.add_all(veterinarians)
    db.session.commit()

    print('Tables seeded')
