from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow requests from any origin

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'training'
}
 
# Function to create a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None
    
# Define a route to test the connection
@app.route('/test_connection')
def test_connection():
    connection = get_db_connection()
    if connection:
        return 'Database connection successful!'
    else:
        return 'Database connection failed!', 500


@app.route("/")
def home():
    return "Hello, World!"

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    # Validate required fields
    if not all([username, email, password, first_name, last_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Connect to the database
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed!'}), 500
    
    try:
        cursor = connection.cursor()
        # Insert data into the table
        cursor.execute(
            """
            INSERT INTO users (username, email, password, phone_number, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (username, email, password, phone_number, first_name, last_name)
        )
        connection.commit()
        cursor.close()
        return jsonify({'message': 'User registered successfully!'}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to insert data into database'}), 500
    finally:
        if connection.is_connected():
            connection.close()

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Connect to the database
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed!'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Check the password (assuming passwords are stored as plain text for this example)
            if user['password'] == password:
                return jsonify({'message': 'Login successful!'}), 200
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
        else:
            return jsonify({'error': 'User not found'}), 404
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to retrieve data from database'}), 500
    finally:
        if connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)