from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import bcrypt
import jwt
import datetime
from db import get_db_connection
from ml_model import ml_service
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend')
CORS(app)

JWT_SECRET = os.getenv('JWT_SECRET', 'secret')

# --- Middleware Helper ---
def token_required(f):
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if ' ' in auth_header:
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user_id = data['id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
            
        return f(current_user_id, *args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

# --- Static File Serving ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# --- Auth Routes ---
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('fullName')
    
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s) RETURNING id, email, full_name, created_at",
            (email, hashed_pw, full_name)
        )
        user = cur.fetchone()
        conn.commit()
        
        token = jwt.encode({
            'id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm="HS256")
        
        return jsonify({'token': token, 'user': user}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'message': 'Email already exists'}), 400
    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({'message': 'Server error'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            token = jwt.encode({
                'id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, JWT_SECRET, algorithm="HS256")
            
            # Remove password hash from response
            user_resp = {k: v for k, v in user.items() if k != 'password_hash'}
            return jsonify({'token': token, 'user': user_resp}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server error'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    data = request.json
    full_name = data.get('fullName')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE users SET full_name = %s WHERE id = %s RETURNING id, email, full_name",
            (full_name, current_user_id)
        )
        user = cur.fetchone()
        conn.commit()
        return jsonify(user)
    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({'message': 'Server error'}), 500
    finally:
        cur.close()
        conn.close()

# --- Application Routes ---
@app.route('/api/applications', methods=['GET'])
@token_required
def get_applications(current_user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM applications WHERE user_id = %s ORDER BY created_at DESC", (current_user_id,))
        apps = cur.fetchall()
        return jsonify(apps)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server error'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/applications', methods=['POST'])
@token_required
def submit_application(current_user_id):
    data = request.json
    business_name = data.get('businessName')
    amount = data.get('amount')
    app_data = data.get('data') # Expecting JSON object
    
    # ML Scoring
    # Merge amount into data for processing
    process_data = app_data.copy()
    process_data['loanAmount'] = amount
    
    prediction = ml_service.predict(process_data)
    
    score = prediction['credit_score']
    confidence = prediction['confidence']
    probability = prediction['probability']
    
    # Decision Logic
    decision = 'review_required'
    status = 'analyzing'
    
    if probability > 0.7:
        decision = 'approved'
        status = 'decision'
    elif probability < 0.4:
        decision = 'rejected'
        status = 'decision'
        
    # Generate Insights
    insights = []
    if probability > 0.6:
        insights.append({'type': 'positive', 'text': f'High Approval Probability ({(probability*100):.1f}%)'})
    if confidence > 0.8:
        insights.append({'type': 'positive', 'text': f'High Confidence Analysis ({(confidence*100):.1f}%)'})
    
    # Add engineered features based strictly on inputs for feedback
    try:
        rev = float(app_data.get('annualRevenue', 0))
        loan = float(amount)
        if rev > 0 and (loan/rev) > 0.5:
            insights.append({'type': 'negative', 'text': 'High Loan-to-Revenue Ratio'})
    except:
        pass

    # Update app_data with ML metadata
    app_data['ml_metadata'] = {
        'probability': probability,
        'confidence': confidence,
        'credit_score': score
    }
    app_data['insights'] = insights
    app_data['decision'] = decision
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        import json
        
        cur.execute(
            """INSERT INTO applications (user_id, business_name, amount, status, ai_score, data) 
               VALUES (%s, %s, %s, %s, %s, %s) 
               RETURNING *""",
            (current_user_id, business_name, amount, status, score, json.dumps(app_data))
        )
        new_app = cur.fetchone()
        conn.commit()
        return jsonify(new_app), 201
    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({'message': 'Server error'}), 500
    finally:
        cur.close()
        conn.close()

# --- Admin Routes ---
@app.route('/api/admin/applications', methods=['GET'])
# @token_required # In a real app, verify admin role. For demo, allowing access or basic auth.
def get_all_applications():
    # Allow querying all applications for the Underwriter Dashboard
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.*, u.email, u.full_name 
            FROM applications a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
        """)
        apps = cur.fetchall()
        return jsonify(apps)
    except Exception as e:
        print(e)
        return jsonify({'message': 'Server error'}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    # Running on port 5000 by default for Flask
    app.run(debug=True, port=5000)
