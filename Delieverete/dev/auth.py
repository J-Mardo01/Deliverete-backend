from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from extensions import mysql, bcrypt, jwt


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    print("Register endpoint hit!")  # Debugging: Confirm route is called
    try:
        print(f"Incoming data: {request.json}")  # Log the request body
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']
        role = data.get('role', 'user')

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user into DB
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, role)
        )
        mysql.connection.commit()

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({"error": str(e)}), 400




@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data['email']
        password = data['password']

        # Query user by email
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user_id, password_hash, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        user_id, password_hash, role = user

        # Verify password
        if not bcrypt.check_password_hash(password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Create token
        token = create_access_token(identity={"user_id": user_id, "role": role})
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
