from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
import cv2
import os
import numpy as np

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a random key for development

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['facial_auth']
users = db['users']

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if not username:
        flash('Username is required!')
        return redirect(url_for('home'))
    
    user = users.find_one({'username': username})
    if user:
        return redirect(url_for('authenticate', username=username))
    else:
        flash('User not found!')
        return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash('Username is required!')
            return redirect(url_for('signup'))
        
        if users.find_one({'username': username}):
            flash('Username already exists!')
            return redirect(url_for('signup'))
        
        return redirect(url_for('capture_image', username=username))
    return render_template('signup.html')

@app.route('/capture_image/<username>')
def capture_image(username):
    return render_template('capture_image.html', username=username)

@app.route('/save_image/<username>', methods=['POST'])
def save_image(username):
    file_path = os.path.join(UPLOAD_FOLDER, f"{username}.jpg")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        equalized_frame = cv2.equalizeHist(gray_frame)
        cv2.imwrite(file_path, equalized_frame)
    cap.release()
    users.insert_one({'username': username, 'image_path': file_path})
    flash('User registered successfully!')
    return jsonify({'success': True})

@app.route('/authenticate/<username>')
def authenticate(username):
    user = users.find_one({'username': username})
    if user:
        return render_template('authenticate.html', user=user)
    else:
        flash('User not found!')
        return redirect(url_for('home'))

@app.route('/authenticate_user/<username>')
def authenticate_user(username):
    user = users.find_one({'username': username})
    if user:
        stored_image_path = user['image_path']
        stored_image = cv2.imread(stored_image_path, cv2.IMREAD_GRAYSCALE)
        
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({'authenticated': False})
        
        current_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        current_image = cv2.equalizeHist(current_image)
        current_image = cv2.resize(current_image, (stored_image.shape[1], stored_image.shape[0]))
        
        diff = cv2.absdiff(stored_image, current_image)
        _, diff = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
        count_nonzero = np.count_nonzero(diff)
        
        # Debugging information
        print(f'Difference count (non-zero pixels): {count_nonzero}')
        
        if count_nonzero < 5000:  # Threshold for matching
            return jsonify({'authenticated': True})
        else:
            return jsonify({'authenticated': False})
    else:
        return jsonify({'authenticated': False})

if __name__ == '__main__':
    app.run(debug=True)
