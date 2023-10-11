from flask import request, jsonify, Blueprint
from .models import db, User
from .utils import generate_sitemap, APIException
import jwt
import datetime
from functools import wraps

api = Blueprint('api', __name__)

# Define a function to check for the presence of a JWT token in the request headers
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the Google inspector, and you will see the GET request"
    }
    return jsonify(response_body), 200

@api.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Implement user registration logic here, including password hashing
    # Example:
    # hashed_password = hash_password_function(password)

    # Create a new user in the database and store the hashed password
    user = User(email=email, password=hashed_password, is_active=True)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@api.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists and verify the password
    user = User.query.filter_by(email=email).first()

    if user is None or not check_password(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Generate a JWT token for the user
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token.decode('UTF-8')}), 200
