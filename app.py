from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
import whisper
from googletrans import Translator

# Flask app setup 
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Load the Whisper model
model = whisper.load_model("base")

# Translator for multilingual support
translator = Translator()

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class FormSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    father_name = db.Column(db.String(50), nullable=False)
    mother_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    branch = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    roll_number = db.Column(db.String(20), nullable=False)
    year_of_study = db.Column(db.String(10), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(10), nullable=True)
    address = db.Column(db.Text, nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Function to sanitize inputs
def sanitize_input(value):
    return value.strip()

# Function to transcribe speech and translate it
def transcribe_speech(audio_path, target_language='en'):
    result = model.transcribe(audio_path)
    original_text = result['text']
    
    # Handle specific terms for special characters
    # Replace "at" with "@"
    original_text = original_text.replace(" at ", "@")
    # Optionally, replace "dot" with "."
    original_text = original_text.replace(" dot ", ".")
    # Handle other potential keywords for special characters if needed

    if target_language != 'en':
        translated_text = translator.translate(original_text, dest=target_language).text
        return translated_text
    return original_text

# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)  # Pass user data if logged in
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = sanitize_input(request.form['userName'])
        email = sanitize_input(request.form['email'])
        password = sanitize_input(request.form['password'])

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists. Please log in.", "error")
            return redirect('/login')  # Redirect to the login page if the user exists

        # Hash the password and save the user to the database
        hashed_password = generate_password_hash(password)
        new_user = User(
            user_name=user_name,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! You can now log in.", "success")
        return redirect('/login')  # Redirect to the login page after successful signup

    return render_template('login signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'user_id' in session:
        flash("You are already logged in.", "info")
        return redirect('/')  # Redirect to home if the user is already logged in

    if request.method == 'POST':
        email = sanitize_input(request.form['email'])
        password = sanitize_input(request.form['password'])

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User does not exist. Please sign up first.", "error")
            return redirect('/signup')

        # Check the password
        if check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect('/')
        else:
            flash("Invalid credentials. Please try again.", "error")

    return render_template('login signup.html')




@app.route('/form', methods=['GET', 'POST'])
def form_filling():
    if request.method == 'POST':
        try:
            # Extracting form data
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            father_name = request.form['fatherName']
            mother_name = request.form['motherName']
            dob = request.form['dob']
            gender = request.form['gender']
            branch = request.form['branch']
            section = request.form['section']
            roll_number = request.form['rollNumber']
            year_of_study = request.form['yearOfStudy']
            percentage = request.form['percentage']
            phone = request.form['phone']
            email = request.form['email']
            blood_group = request.form.get('bloodGroup', '')
            address = request.form['address']

            # Save form data to the database
            new_submission = FormSubmission(
                first_name=first_name,
                last_name=last_name,
                father_name=father_name,
                mother_name=mother_name,
                dob=dob,
                gender=gender,
                branch=branch,
                section=section,
                roll_number=roll_number,
                year_of_study=year_of_study,
                percentage=percentage,
                phone=phone,
                email=email,
                blood_group=blood_group,
                address=address
            )
            db.session.add(new_submission)
            db.session.commit()

            flash("Student details submitted successfully!", "success")
            return redirect('/success')
        except Exception as err:
            print(f"Error: {err}")
            flash("There was an error while submitting the form. Please try again.", "error")
            return redirect('/form')

    return render_template('forms.html')

@app.route('/success')
def success_page():
    return render_template('thnx.html')

@app.route('/secondpg')
def second_page():
    return render_template('login signup.html')

if __name__ == '__main__':
    app.run(debug=True)