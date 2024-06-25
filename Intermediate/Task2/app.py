from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from cryptography.fernet import Fernet

app = Flask(__name__)

# Generate a key for encryption and decryption
# In production, this key should be securely stored and not regenerated each time the app runs
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
db = client['credit_card_db']
collection = db['users']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form['name']
    cc_number = request.form['cc_number'].encode('utf-8')
    
    # Encrypt the credit card number
    encrypted_cc = cipher_suite.encrypt(cc_number)
    
    # Store name and encrypted credit card number in MongoDB
    collection.insert_one({'name': name, 'encrypted_cc': encrypted_cc.decode('utf-8')})
    return render_template('signup.html', message="Signup successful. Please log in.")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    name = request.form['name']
    cc_number = request.form['cc_number'].encode('utf-8')
    
    # Retrieve user from MongoDB
    user = collection.find_one({'name': name})
    if user:
        encrypted_cc = user['encrypted_cc'].encode('utf-8')
        decrypted_cc = cipher_suite.decrypt(encrypted_cc)
        
        if decrypted_cc == cc_number:
            return render_template('valid.html')
        else:
            return render_template('login.html', message="Invalid credit card number.")
    else:
        return render_template('login.html', message="User not found.")

if __name__ == '__main__':
    app.run(debug=True)

