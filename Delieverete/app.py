from flask import Flask
from dev.users import users_blueprint
from dev.orders import orders_blueprint
from dev.auth import auth_blueprint
from extensions import mysql, bcrypt, jwt
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_secret_key')

# Initialize extensions with the app
mysql.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Register Blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(users_blueprint, url_prefix='/users')
app.register_blueprint(orders_blueprint, url_prefix='/orders')

# Print routes for debugging
for rule in app.url_map.iter_rules():
    print(f"Endpoint: {rule.endpoint}, URL: {rule}")

if __name__ == '__main__':
    app.run(debug=True)

