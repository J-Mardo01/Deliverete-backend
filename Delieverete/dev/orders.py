from flask import Blueprint, request, jsonify
from extensions import mysql  # Ensure you're importing the correct MySQL object
import datetime
from decimal import Decimal

orders_blueprint = Blueprint('orders', __name__)

@orders_blueprint.route('/', methods=['POST'])
def create_order():
    try:
        data = request.json
        user_id = data['user_id']
        volume = data['volume']
        address = data.get('address')
        delivery_date = data['delivery_date']
        status = data.get('status', 'Pending')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_id = data.get('location_id')

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO Orders (user_id, volume, address, delivery_date, status, latitude, longitude, location_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, volume, address, delivery_date, status, latitude, longitude, location_id))
        mysql.connection.commit()

        return jsonify({"message": "Order created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@orders_blueprint.route('/', methods=['GET'])
def get_orders():
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT 
                orders.order_id, 
                orders.user_id,
                users.username, 
                orders.volume, 
                orders.address, 
                orders.delivery_date, 
                orders.status
            FROM orders
            JOIN users ON orders.user_id = users.user_id
        """
        cursor.execute(query)
        orders = cursor.fetchall()

        # Format the result as a list of dictionaries
        result = [
            {
                "order_id": order[0],
                "user_id": order[1],
                "username": order[2],  # This should be the third field
                "volume": float(order[3]),
                "address": order[4],
                "delivery_date": order[5].strftime('%Y-%m-%d'),
                "status": order[6]
            }
            for order in orders
        ]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@orders_blueprint.route('/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No fields to update"}), 400

        fields = []
        values = []

        # Dynamically build the query based on provided fields
        for key, value in data.items():
            fields.append(f"{key} = %s")
            values.append(value)

        if not fields:
            return jsonify({"error": "No valid fields to update"}), 400

        # Add the order_id to the query values
        values.append(order_id)

        query = f"UPDATE Orders SET {', '.join(fields)} WHERE order_id = %s"

        cursor = mysql.connection.cursor()
        cursor.execute(query, tuple(values))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Order not found"}), 404

        return jsonify({"message": "Order updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@orders_blueprint.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Orders WHERE order_id = %s", (order_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Order not found"}), 404

        return jsonify({"message": "Order deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

