from flask import Flask
import os
from init import db, ma, bcrypt, jwt
from controllers.cli_controller import db_commands
from controllers.customers_controller import customers_bp
from controllers.veterinarians_controller import veterinarians_bp
from controllers.patients_controller import patients_bp
from sqlalchemy.exc import NoResultFound


def create_app():
    app = Flask(__name__)

    @app.errorhandler(404)
    def not_found(err):
        return {'error': str(err)}, 404

    @app.errorhandler(405)
    def method_error(err):
        return {'error': str(err)}, 405

    @app.errorhandler(400)
    def bad_request(err):
        return {'error': str(err)}, 400

    @app.errorhandler(ValueError)
    def value_error(err):
        return {'error': str(err)}, 403

    @app.errorhandler(NoResultFound)
    def no_result_found(err):
        return {'error': str(err)}, 404

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(db_commands)
    app.register_blueprint(customers_bp)    
    app.register_blueprint(veterinarians_bp)    
    app.register_blueprint(patients_bp)    

    return app