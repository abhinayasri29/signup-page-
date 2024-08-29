from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import bcrypt  # For password hashing

app = Flask(__name__)

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
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Connect to the database
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed!'}), 500
    
    try:
        cursor = connection.cursor()
        # Insert data into the table
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
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
    username = request.form['username']
    password = request.form['password']
    
    # Connect to the database
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed!'}), 500
    
    try:
        cursor = connection.cursor()
        # Fetch user record from the database
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            stored_password = result[0]
            # Verify the provided password against the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return jsonify({'message': 'Login successful!'}), 200
            else:
                return jsonify({'error': 'Invalid username or password!'}), 401
        else:
            return jsonify({'error': 'User not found!'}), 404
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to fetch data from database'}), 500
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
