import os

import  face_recognition
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

from tkinter import messagebox
import time


def validation(self):
    """validates if email entry field is left empty, if True
    returns info message displaying to enter the email address"""

    if self.email_entry.get() == '':
        messagebox.showinfo("Empty", "Please Enter Email Address or mobile")
    else:
        self.click_send_otp()


def countdown(self):
    times = int(self.hrs.get()) * 3600 + int(self.mins.get()) * 60 + int(self.sec.get())
    while times > -1:
        minute, second = (times // 60, times % 60)
        hour = 0
        if minute > 60:
            hour, minute = (minute // 60, minute % 60)
        self.sec.set(second)
        self.mins.set(minute)
        self.hrs.set(hour)

        self.window.update()
        time.sleep(1)
        if (times == 0):
            messagebox.showinfo("time's up", "you must resend the otp")
            self.sec.set('00')
            self.mins.set('02')
            self.hrs.set('00')
        times -= 1


Received_OTP = []

import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_otp_email(to_email, otp_value):
    from_email = "jesimayasmeenismail@gmail.com"
    subject = "OTP Verification code"
    message = f"Your OTP: {otp_value}"
    print(message)

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, "oprlgamapfgrkezs")
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", str(e))


def click_send_otp(email):
    """Sends an OTP to the provided email."""
    if email != '':
        try:
            value = random.randint(100000, 999999)

            # Sending OTP via email
            send_otp_email(email, value)

            print(value, '{{{{{{{{{{{{}}}}}}}}}}}}}}}')
            Received_OTP.append(int(value))
            print(type(Received_OTP))
            return value
        except Exception as e:
            print("Error sending OTP:", str(e))
            return None
    else:
        print("Email is required.")
        return None


def click_verification(otp):
    """if OTP entry field is not empty, it will verify the actual OTP with user OTP that they
    entered in OTP field"""

    if otp != "":
        received_otp = None
        for i in Received_OTP:
            print(i, '88888888888888888')
            received_otp = int(i)
            print(received_otp, '9999999999999999')
        try:
            if int(otp) == received_otp:
                print("Success", "You Have Been Successfully Verified")
                return True
            else:
                print("Bad Requests", "Sorry we were not able to identify you")
                return False
        except ValueError:

            print("Bad Requests", "Sorry we were not able to identify you")
            return False

    else:
        print("Empty", "Please Enter recent OTP from your email")
        return False


'''Face Recognition function'''
import cv2
import tkinter as tk
from PIL import Image, ImageTk

'''take frames automatically when camera is ON ,without user interation and sending the data to the backend using flask-socketio library'''


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        print(user, 'sljlsjlvfsdl')
        if user:
            if check_password_hash(user.password, password):
                # mobile_no = user.mobile_no
                email_id = user.email
                print(email, 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                print(user.mobile_no, '00000000000000000000000000000000')
                click_send_otp(email_id)
                # flash('Logged in successfully!', category='success')
                session['resend_email'] = email_id
                login_user(user, remember=True)
                return redirect(url_for('auth.pop_up_for_otp_verify'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/verify_otp', methods=['GET', 'POST'])
def pop_up_for_otp_verify():
    if request.method == 'POST':
        otp = request.form.get('otp')
        print(otp, 'otp')
        otp_verify = click_verification(otp)
        print(otp_verify, 'T' * 10)
        if otp_verify == True:
            flash('OTP Verified successfully!', category='success')
            return redirect(url_for('auth.face_rec'))
        else:
            flash('OTP Verification Failed!', category='success')
    return render_template("otp_verification.html", user=current_user)


@auth.route('/resend_otp', methods=['GET', 'POST'])
def resend_otp():
    if request.method == 'POST':
        print("Resending OTP...")
        resend_email = session.get('resend_email')
        print(resend_email, 'email' * 10)
        click_send_otp(resend_email)
        return redirect(url_for('auth.pop_up_for_otp_verify'))
    return render_template("otp_verification.html", user=current_user)


'''Global variable to store image data'''

import face_recognition as fr

import os


def get_encoded_faces():
    encoded = {}

    base_path = r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\Face_Recognition"

    for dirpath, dnames, fnames in os.walk(base_path):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png"):
                face_path = os.path.join(base_path, f)
                try:
                    face = fr.load_image_file(face_path)
                    face_encodings = fr.face_encodings(face)
                    if len(face_encodings) > 0:
                        encoding = face_encodings[0]
                        encoded[f.split(".")[0]] = encoding
                    else:
                        print(f"No face detected in {face_path}")
                except Exception as e:
                    print(f"Error processing {face_path}: {e}")

    return encoded


import numpy as np


def classify_face_live():
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    # Load an image using face_recognition library
    image_path = r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\website\Faces\captured.jpg"
    image = face_recognition.load_image_file(image_path)

    # Find face locations in the image
    face_locations = face_recognition.face_locations(image)
    unknown_face_encodings = face_recognition.face_encodings(image, face_locations)

    face_names = []
    for face_encoding in unknown_face_encodings:
        matches = face_recognition.compare_faces(faces_encoded, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            print(name, 'Matching face found')
            # Return True when a match is found
            return True
        else:
            print('No matching face found')

        face_names.append(name)
    if not any(face_names):
        print('No faces found in the image')
    # Process the face_names list as needed


def save_image_recived_from_frondend(captured_image_data):
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    image_filename = f"captured.jpg"
    image_data = captured_image_data.split(',')[1]  # Remove data:image/jpeg;base64,
    save_directory = r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\website\Faces"
    image_path = os.path.join(save_directory, image_filename)
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))
    return image_path


@auth.route('/face_rec', methods=['GET', 'POST'])
def face_rec():
    global captured_image_data

    if request.method == 'POST':
        captured_image_data = request.form.get('imageData')
        if captured_image_data:
            save_image_recived_from_frondend(captured_image_data)
            match_result = classify_face_live()
            print(match_result, 'match result found')
            if match_result is True:
                # Assuming the classify_face_live() function returns True when a match is found
                flash('Face Recognition successfully completed!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Face Recognition Failed!', category='error')

    return render_template("face_recognition.html", user=current_user)


"""Analysing Fingerprint Data"""

from PIL import Image
from difflib import SequenceMatcher


def fingerprint_similarity(image1, image2):
    sequence_matcher = SequenceMatcher(None, image1, image2)
    similarity_ratio = sequence_matcher.ratio() * 100  # Convert to percentage
    return similarity_ratio


def compare_fingerprint_data(test_original):
    for file in os.listdir(r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\data"):
        fingerprint_database_path = os.path.join(
            r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\data", file)
        fingerprint_database_image = Image.open(fingerprint_database_path).convert("L")

        test_original_data = test_original.tobytes()
        database_image_data = fingerprint_database_image.tobytes()

        # Simulate some processing time for analysis
        import time
        time.sleep(2)  # Simulate 2 seconds of analysis time

        match_percentage = fingerprint_similarity(test_original_data, database_image_data)

        if match_percentage > 75:
            print("% match:", match_percentage)
            print("Fingerprint ID:", file)
            print("Fingerprint is a potential match!")
            return True
            break

        else:  # This else block executes if no match is found
            print("No matching fingerprint found.")


@auth.route('/finger_analyze', methods=['GET', 'POST'])
def finger_analyze():
    test_original_path = r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\website\img_22.tif"
    print(test_original_path, 'fffffffffffffffffffffffffffff')
    test_original = Image.open(test_original_path).convert("L")
    match_result = compare_fingerprint_data(test_original)
    print(match_result, '{{{{{{{{{{{}}}}}}}}}}}')
    if match_result is True:
        flash('Finger Print Matched successfully!', category='success')
        return redirect(url_for('views.home'))
    else:
        flash('Finger Print Recognition Failed!', category='error')
        return redirect(url_for('auth.login'))
    return render_template("Analyze_fingerprint.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))




@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        mobile_no = request.form.get('mobile_no')
        password1 = request.form.get('password1')
        passwordCon = request.form.get('passwordCon')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 3 characters', category='error')
        elif len(last_name) <= 1:
            flash('last name is mandatory', category='error')
        elif password1 != passwordCon:
            flash('password mismatch', category='error')
        elif len(password1) < 7:
            flash('password must be at least 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, mobile_no=mobile_no,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            # Store new_user in the session
            concatenated_name = f"{new_user.first_name} {new_user.last_name}"
            session['new_user_name'] = concatenated_name
            print(concatenated_name)
            flash('All credentials are filled', category='success')
            return redirect(url_for('auth.bio_auth'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/bio_auth', methods=['GET', 'POST'])
def bio_auth():
    return render_template("Biometric Authentication.html", user=current_user)


'''Function to capture and save the image'''


def save_image(image_data, new_user_name):
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    image_filename = f"{new_user_name}.jpg"
    image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64,
    save_directory = r"D:\Advanced Level Three Factor Authentication\Website_authentication\Website_authentication\Research Project\authentication\website\Face_Recoginition"
    image_path = os.path.join(save_directory, image_filename)
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))
    return image_path


import base64
import datetime

'''To Access Camera '''


@auth.route('/face_capture', methods=['GET', 'POST'])
def face_capture():
    if request.method == 'POST':
        print('hhfhfjhfgjgjhgjgjhgjg')
        image_data = request.form.get('imageData')
        print(image_data, '[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]')
        new_user_name = session.get('new_user_name')
        print(new_user_name, '())))()()()09)((09009')
        if image_data != None:
            print(image_data, '[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]')
            save_image(image_data, new_user_name)
            return redirect(url_for('auth.login'))
    return render_template("face_capture.html", user=current_user)


'''ADD finger print for Authorization'''


@auth.route('/add_finger_print', methods=['GET', 'POST'])
def add_finger_print():
    return render_template("fingerprint.html", user=current_user)


@auth.route('/delete', methods=['GET', 'POST'])
def delete_all_elements():
    try:
        # Delete all records from the Item table
        db.session.query(User).delete()
        print(User)
        db.session.commit()
        return "All elements deleted from the database."
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}", 500
