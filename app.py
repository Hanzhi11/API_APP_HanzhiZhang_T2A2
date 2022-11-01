from flask import Flask
import os
from init import db, ma, bcrypt, jwt
from controllers.cli_controller import db_commands
from controllers.customers_controller import customers_bp
from controllers.veterinarians_controller import veterinarians_bp
from controllers.patients_controller import patients_bp
from controllers.appointments_controller import appointments_bp
from sqlalchemy.exc import NoResultFound, DataError
from sqlalchemy.exc import IntegrityError


def create_app():
    app = Flask(__name__)

    @app.errorhandler(404)
    def URL_not_found(err):
        return {'error': str(err)}, 404

    @app.errorhandler(405)
    def method_error(err):
        return {'error': str(err)}, 405

    @app.errorhandler(400)
    def bad_request(err):
        return {'error': str(err)}, 400

    @app.errorhandler(401)
    def unauthorized_error(err):
        return {'error': str(err)}, 401

    @app.errorhandler(ValueError)
    def value_error(err):
        return {'error': str(err)}, 403

    @app.errorhandler(IntegrityError)
    def integrity_error(err):
        if 'UniqueViolation' in err.args[0]:
            if 'appointment' in err.args[0]:
                return {'error': 'Appointment for the same date and time exists already'}, 409
            elif 'email' in err.args[0]:
                return {'error': 'Email exists already'}, 409
            elif 'patient' in err.args[0]:
                return {'error': 'Patient exists already'}, 409
        elif 'ForeignKeyViolation' in err.args[0]:
            if 'patient' in err.args[0]:
                return {'error': 'patient not exists'}, 404
            elif 'veterinarian' in err.args[0]:
                return {'error': 'veterinarian not exists'}, 404

    @app.errorhandler(NoResultFound)
    def no_result_found(err):
        return {'error': str(err)}, 404

    @app.errorhandler(DataError)
    def data_error(err):
        return {'error': str(err)}, 404

    @app.errorhandler(KeyError)
    def key_error(err):
        return {'error': f'{err.args[0]} is required'}, 400



    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(db_commands)
    app.register_blueprint(customers_bp)    
    app.register_blueprint(veterinarians_bp)    
    app.register_blueprint(patients_bp)    
    app.register_blueprint(appointments_bp)    

    return app