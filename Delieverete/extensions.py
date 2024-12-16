from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Initialize extensions without attaching to the app
mysql = MySQL()
bcrypt = Bcrypt()
jwt = JWTManager()
