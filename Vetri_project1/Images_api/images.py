import os
import mysql.connector
import uuid  # Import UUID for generating unique filenames
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "Vijaymaris07"
# Configuration for saving images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Connect to MySQL database
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vijay@006",
        database="admin"
    )
    return connection

# Route to render upload form
@app.route('/')
def index():
    return render_template('imges.html')

# Route for image upload using form
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Get the filename from the form
        provided_filename = request.form.get('filename')  # Retrieve the filename from form
        unique_filename =  secure_filename(file.filename)  # Create unique filename

        # Save file to the directory
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        # Save details in MySQL database
        connection = get_db_connection()
        cursor = connection.cursor()

        sql = "INSERT INTO images (img, filename, mimetype) VALUES (%s, %s, %s)"
        val = (unique_filename, provided_filename, file.mimetype)  # Store unique filename and provided filename
        cursor.execute(sql, val)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'File successfully uploaded'}), 201

# Route to retrieve image
@app.route('/retrieve/<string:id>', methods=['GET'])
def retrieve_image(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    sql = "SELECT img, filename FROM images WHERE id = %s"
    cursor.execute(sql, (id,))
    result = cursor.fetchone()
    
    if not result:
        return jsonify({'error': 'Image not found'}), 404

    unique_filename = result[0]  # Unique filename saved in the database
    cursor.close()
    connection.close()

    # Send the file from the upload directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], unique_filename)

if __name__ == '__main__':
    app.run(debug=True)
