# Applicant Tracking System

This project is a **Applicant Tracking System** designed for HR professionals and applicants. It provides features for job description management, resume uploads, and evaluations using generative AI. The system is built using Flask, PostgreSQL, and other tools for secure and efficient operations.

---

## Features

1. **Login and Signup**:
   - Separate login for HR professionals and applicants.
   - Secure password management using bcrypt.

2. **HR Dashboard**:
   - Upload and save job descriptions.
   - View and evaluate uploaded resumes.
   - Delete resumes.

3. **Applicant Dashboard**:
   - Upload resumes in PDF format.
   - View job descriptions set by HR.

4. **Resume Evaluation**:
   - Evaluate resumes against job descriptions using generative AI.
   - Generate evaluations such as:
     - Professional analysis of resume strengths and weaknesses.
     - Percentage match with job descriptions.

5. **PDF Processing**:
   - Converts PDF resumes into images for processing and evaluation.

---

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS
- **Database**: PostgreSQL
- **Security**:
  - Password hashing using bcrypt.
  - Secure session management.
- **AI Integration**: Google Generative AI (`gemini-1.5-flash`)
- **PDF Processing**: `pdf2image`, `Pillow`
- **Environment Configuration**: `python-dotenv`

---

## Prerequisites

1. **Python 3.9+**
2. **PostgreSQL**: Ensure PostgreSQL is installed and configured.
3. **Dependencies**: Install required Python libraries:
   ```bash
   pip install flask flask-bcrypt psycopg2 pdf2image pillow google-generativeai python-dotenv
4.**Environment Variables**:
  - Create a .env file with the following:
    ```makefile
    GOOGLE_API_KEY=your_google_api_key
## Setup

1.**Clone the Repository**:
  ```bash
  git clone https://github.com/yourusername/applicant-tracking-system.git
  cd applicant-tracking-system
```
2.**Set Up the Database**:
  - Create a PostgreSQL database named postgres with the following configuration:
    - Host: localhost
    - User: YOUR USERNAME
    - Password: YOUR PASSWORD
    - Port: PORT NUMBER

  - Create necessary tables:
    ```bash
    CREATE TABLE users1 (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL
    );
    CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL
    );
    ```
3.**Run the Application**:
   ```bash
  python app.py
  ```
4.**Access the Application**:
  - Open your browser and navigate to: LINK GENERATED
## Folder Structure
  ```bash
  .
├── app.py              # Main application file
├── templates/          # HTML templates
│   ├── login.html
│   ├── signup.html
│   ├── hr_dashboard.html
│   ├── applicant_dashboard.html
│   └── response.html
├── uploads/            # Directory for uploaded resumes
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
  ```
## Usage
## HR Workflow:

  - Log in as HR.
  - Upload job descriptions.
  - View uploaded resumes.
  - Evaluate resumes using generative AI for professional analysis or percentage match

## Applicant Workflow:

- Log in as an applicant.
- View the job description set by HR.
- Upload resumes in PDF format.
