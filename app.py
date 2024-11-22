# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from flask_bcrypt import Bcrypt
import os
import io
import base64
from werkzeug.utils import secure_filename
from PIL import Image
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

# Database configuration
conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="Postgres",
                        port="5432")

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to interact with the generative AI model and get a response
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text
# Function to convert PDF to an image and process the first page
def input_pdf_setup(uploaded_file_path):
    if uploaded_file_path is not None:
        # Convert the PDF to image
        images = pdf2image.convert_from_path(uploaded_file_path)

        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Routes and functions for handling login, dashboard, and other actions

@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

# HR login route (POST request to handle authentication)
@app.route('/login_hr', methods=['POST'])
def login_hr():
    username = request.form['username']
    password = request.form['password']

    with conn.cursor() as cursor:
        cursor.execute("SELECT id, password FROM users1 WHERE username = %s AND role = 'hr'", (username,))
        user = cursor.fetchone()
    
    if user and bcrypt.check_password_hash(user[1], password):
        session['username'] = username
        session['role'] = 'hr'
        return redirect(url_for('hr_dashboard'))
    else:
        return "Invalid credentials"

# Applicant login route (POST request to handle authentication)
@app.route('/login_applicant', methods=['POST'])
def login_applicant():
    username = request.form['username']
    password = request.form['password']

    with conn.cursor() as cursor:
        cursor.execute("SELECT id, password FROM users1 WHERE username = %s AND role = 'applicant'", (username,))
        user = cursor.fetchone()
    
    if user and bcrypt.check_password_hash(user[1], password):
        session['username'] = username
        session['role'] = 'applicant'
        return redirect(url_for('applicant_dashboard'))
    else:
        return "Invalid credentials"

# Route for handling sign-up functionality
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users1 WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
        
        if not existing_user:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users1 (username, password, role) VALUES (%s, %s, %s)",
                               (username, hashed_password, role))
                conn.commit()
            session['username'] = username
            session['role'] = role
            if role == 'hr':
                return redirect(url_for('hr_dashboard'))
            elif role == 'applicant':
                return redirect(url_for('applicant_dashboard'))
        else:
            return "User already exists"
    return render_template('signup.html')

# HR Dashboard route (handles job description and resume viewing)
@app.route('/hr', methods=['GET', 'POST'])
def hr_dashboard():
    if 'username' not in session or session['role'] != 'hr':
        return redirect(url_for('login'))

    if request.method == 'POST':
        job_description = request.form['job_description']
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO job_descriptions (description) VALUES (%s)", (job_description,))
            conn.commit()
        return "Job Description Saved"

    resumes = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('hr_dashboard.html', resumes=resumes)

# Route for deleting a resume
@app.route('/delete_resume', methods=['POST'])
def delete_resume():
    if 'username' not in session or session['role'] != 'hr':
        return redirect(url_for('login'))

    resume_name = request.form['resume_name']
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_name)

    try:
        if os.path.exists(resume_path):
            os.remove(resume_path)  # Delete the file
            return redirect(url_for('hr_dashboard'))
        else:
            return "File not found", 404
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

# Applicant Dashboard route (handles resume upload and job description view)
@app.route('/applicant', methods=['GET', 'POST'])
def applicant_dashboard():
    if 'username' not in session or session['role'] != 'applicant':
        return redirect(url_for('login'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT description FROM job_descriptions ORDER BY id DESC LIMIT 1")
        job_description = cursor.fetchone()
    job_description_text = job_description[0] if job_description else 'No job description available'

    if request.method == 'POST':
        file = request.files['resume']
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return "Resume Uploaded Successfully"
        else:
            return "Please upload a PDF file"

    return render_template('applicant_dashboard.html', job_description=job_description_text)

# Route for evaluating resumes (using generative AI to assess)
@app.route('/evaluate_resume', methods=['POST'])
def evaluate_resume():
    if 'username' not in session or session['role'] != 'hr':
        return redirect(url_for('login'))

    filename = request.form['resume']
    action = request.form['action']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        with conn.cursor() as cursor:
            cursor.execute("SELECT description FROM job_descriptions ORDER BY id DESC LIMIT 1")
            job_description = cursor.fetchone()[0]
        pdf_content = input_pdf_setup(file_path)

        if action == 'tell_me_about_the_resume':
            prompt = """
            You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
            Please share your professional evaluation on whether the candidate's profile aligns with the role. 
            Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
            """
        elif action == 'percentage_match':
            prompt = """
            You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
            your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
            the job description. First, the output should come as percentage and then keywords missing and last final thoughts.
            """
        else:
            return redirect(url_for('hr_dashboard'))

        response = get_gemini_response(job_description, pdf_content, prompt)
        return render_template('response.html', response=response)
    else:
        return redirect(url_for('hr_dashboard'))

# Logout route (clears session)
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
