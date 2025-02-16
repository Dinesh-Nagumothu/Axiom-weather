from flask import Flask, render_template, request, redirect, session, url_for, jsonify, make_response
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ph23AxQZUJmtFtmgMQXFQHev6xZUMw'  # Change this to a random secret key

# MongoDB connection
client = MongoClient("mongodb+srv://dineshpolice256:%3Cdb_password%3E@cluster0.nyelh.mongodb.net/?authSource=weatherAPI")
db = client.weatherAPI  # Change this to your database name
users_collection = db.users  # Change this to your collection name

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:
            decoded_token = jwt.decode(session['token'], app.secret_key, algorithms=['HS256'])
            if(int(time.time()) >= decoded_token['exp']):
                return redirect('/logout')
        except jwt.ExpiredSignatureError:
            return jsonify({'Message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Message': 'Invalid token'}), 403

        return func(*args, **kwargs)
    return decorated

@app.route('/public')
def public():
    return 'For Public'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome to your dashboard !  '

@app.route('/')
def signin():
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if email already exists
        if users_collection.find_one({'email': email}):
            return "Email already exists. Please use a different email."

        # Insert new user
        user_data = {'email': email, 'password': hashed_password}
        users_collection.insert_one(user_data)

        return redirect('/')

    return render_template('signup.html')

@app.route('/signin', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password'], password):
        session['logged_in'] = True
        
        token = jwt.encode({'email': email, 'exp': int(time.time()) + 60}, app.secret_key)
        session['token'] = token
        
        session['user_id'] = str(user['_id'])
        return redirect('/weather')
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed "'})

@app.route('/weather')
@token_required
def weather():
    if 'user_id' in session:
        return render_template('weather.html')
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('token', None)  # Remove token from session
    return redirect('/')

@app.route('/get_token', methods=['GET'])
@token_required
def get_token():
    if 'token' in session:
        decoded_token = jwt.decode(session['token'], app.secret_key, algorithms=['HS256'])
        if(int(time.time()) < decoded_token['exp']):
            return jsonify({'token': decoded_token})
    return "Token not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)