"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from api.models import db, User
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

#from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# @ernestomedinam:
# this is where you instantiate JWT Manager 
# and register it to your app. https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html
app.config["JWT_SECRET_KEY"] = os.getenv("FLASK_APP_KEY")
jwt = JWTManager(app)

# here is the jwt custom loader
# Define a function to check for the presence of a JWT token in the request headers
# def token_required(f):
# @ernestomedinam:
# use flask-jwt-extended loader to customize jwt_required decorator
@jwt.user_lookup_loader
def custom_verify(jwt_headers, jwt_payload): 
    # @wraps(f)
    # def decorated(*args, **kwargs):
    # verifying the token is automatically done by the library
    # you can customize it with the loader_verification_loader
    # token = request.headers.get('Authorization')
    # if not token:
    #     return jsonify({'message': 'Token is missing'}), 401

    try:
        # you don't need the jwt object, you can import decode from the library data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        current_user = User.query.filter_by(id=user_id).one_or_none()
        if current_user is None: 
            raise Exception("no user")
    except:
        return jsonify({'message': 'Token is invalid'}), 401

    return current_user



# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)