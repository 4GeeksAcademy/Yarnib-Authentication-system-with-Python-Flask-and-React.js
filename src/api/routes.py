from flask import request, jsonify, Blueprint
from .models import db, User
from .utils import generate_sitemap, APIException
import datetime
from functools import wraps
# import jwt
from flask_jwt_extended import create_access_token, jwt_required, current_user

api = Blueprint('api', __name__)

# moved the custom jwt loader to app.py

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the Google inspector, and you will see the GET request"
    }
    return jsonify(response_body), 200

# @api.route('/api/signup', methods=['POST'])
# you don't need the extra /api because that is being added on the 
# app.py file where it says app.register_blueprint(api, url_prefix="/api")
@api.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Implement user registration logic here, including password hashing
    # Example:
    # hashed_password = hash_password_function(password)

    # Create a new user in the database and store the hashed password
    
    # @ernestomedinam:
    # you are not hasing the user password :S
    # to hash a password you need to create a random salt for 
    # an user and then use their password + the salt and hash
    # that hash is what you'd store in the database.
    # in such case, checking password is valid consists on
    # retrieving the user salt, adding it to the password the user
    # sent on the log in request, hashing it using the 
    # same method that you use when you create users,
    # and then comparing if both hashes match (the one you just
    # created and the one stored in database.)

    # user = User(email=email, password=hashed_password, is_active=True)
    # this is what it would look like using regular password and 
    # not sending is_active=True, because your model __init__ function
    # is not expecting it but rather just setting it to True always.
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# @api.route('/api/login', methods=['POST'])
# same as for sign up
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists and verify the password
    user = User.query.filter_by(email=email).first()

    # @ernestomedinam
    # because you are not hashing, just compare both passwords
    # if user is None or not check_password(user.password, password):
    if user is None or user.password != password: 
        return jsonify({'message': 'Invalid credentials'}), 401

    # Generate a JWT token for the user
    # token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
    token = create_access_token(identity=user.id)

    # return jsonify({'token': token.decode('UTF-8')}), 200
    return jsonify({'token': token}), 200

# default jwt_required fn is usualy enough
# because you are using your own custom one, then this
# function received current_user as argument.
@api.route("/private", methods=["GET"])
@jwt_required() 
def get_private_data(*args, **kwargs):
    return jsonify({
        "user": current_user.serialize(),
        "data": "some private data."
    }), 200