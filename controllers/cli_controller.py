from flask import Blueprint
from init import db, bcrypt
from models.customer import Customer

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
            contact_number = 412341234
        ),
        Customer(
            first_name = 'Rod',
            last_name = 'Stone',
            email = 'rodstone@test.com',
            password = bcrypt.generate_password_hash('Rodstone2$').decode('utf-8'),
            contact_number = 733441234
        )
    ]

    db.session.add_all(customers)
    db.session.commit()

    print('Tables seeded')
