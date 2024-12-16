from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from extensions import mysql

users_blueprint = Blueprint('users', __name__)

#API endpoints for the user backend

# Create a user
@users_blueprint.route('/', methods=['POST'])
def create_user():
    try:
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']

        #hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = mysql.connection.cursor()

        # Check if email already exists
        cursor.execute("SELECT COUNT(*) FROM Users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result[0] > 0:
            return jsonify({"error": "Email already exists"}), 400

        # Insert the new user
        cursor.execute("INSERT INTO Users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, password_hash))
        mysql.connection.commit()

        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Get all users
@users_blueprint.route('/', methods=['GET'])
def get_users():
    try:
        # Extract query parameters
        user_id = request.args.get('user_id')
        email = request.args.get('email')

        cursor = mysql.connection.cursor()

        if user_id:
            # Fetch a specific user by ID
            cursor.execute("SELECT user_id, username, email FROM Users WHERE user_id = %s", (user_id,))
        elif email:
            # Fetch a specific user by email
            cursor.execute("SELECT user_id, username, email FROM Users WHERE email = %s", (email,))
        else:
            # Fetch all users
            cursor.execute("SELECT user_id, username, email FROM Users")

        users = cursor.fetchall()

        # Format the result
        user_list = [{"user_id": user[0], "username": user[1], "email": user[2]} for user in users]

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Update a user
@users_blueprint.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json  # Get the JSON data from the request
        username = data.get('username')
        email = data.get('email')

        if not username and not email:
            return jsonify({"error": "No fields to update"}), 400

        cursor = mysql.connection.cursor()

        # Build the update query dynamically based on provided fields
        query = "UPDATE Users SET "
        query_params = []
        if username:
            query += "username = %s, "
            query_params.append(username)
        if email:
            query += "email = %s, "
            query_params.append(email)

        # Remove the trailing comma and space
        query = query.rstrip(", ")

        # Add the WHERE clause
        query += " WHERE user_id = %s"
        query_params.append(user_id)

        # Execute the update query
        cursor.execute(query, tuple(query_params))
        mysql.connection.commit()

        return jsonify({"message": "User updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Delete a user
@users_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cursor = mysql.connection.cursor()

        # Execute the DELETE query
        cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

