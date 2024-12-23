from flask import Flask
from flask_mysqldb import MySQL

# Initialize MySQL
mysql = MySQL()

# Function to initialize MySQL configuration
def init_app(app):
    app.config['MYSQL_HOST'] = '127.0.0.1'  # MySQL host address
    app.config['MYSQL_USER'] = 'root'       # MySQL username
    app.config['MYSQL_PASSWORD'] = 'Lasya@2004'  # MySQL password
    app.config['MYSQL_DB'] = 'voxform_db'  # Default database name
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Optional: Use dictionary cursor
    mysql.init_app(app)

# Function to initialize the database and test the connection
def test_connection(app):
    try:
        connection = mysql.connection
        cursor = connection.cursor()

        # Create the database if it does not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS voxform_db;")
        connection.commit()

        # Switch to the created database
        cursor.execute("USE voxform_db;")

        # Create Users table if it doesn't exist
        create_users_table_query = """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_users_table_query)
        connection.commit()

        # Create FormSubmission table if it doesn't exist
        create_form_submission_table_query = """
        CREATE TABLE IF NOT EXISTS FormSubmission (
            submission_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            father_name VARCHAR(50) NOT NULL,
            mother_name VARCHAR(50) NOT NULL,
            dob VARCHAR(20),
            gender VARCHAR(10),
            branch VARCHAR(50) NOT NULL,
            section VARCHAR(10) NOT NULL,
            roll_number VARCHAR(20) NOT NULL,
            year_of_study VARCHAR(10) NOT NULL,
            percentage FLOAT NOT NULL,
            phone VARCHAR(15) NOT NULL,
            email VARCHAR(100) NOT NULL,
            blood_group VARCHAR(10),
            address TEXT NOT NULL
        );
        """
        cursor.execute(create_form_submission_table_query)
        connection.commit()

        print("Database connection and initialization successful.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
    finally:
        # Ensure cursor is closed after operations
        cursor.close()

# Initialize Flask app
app = Flask(__name__)

# Initialize the app configuration for MySQL
init_app(app)

# Initialize the connection and test
with app.app_context():
    test_connection(app)
