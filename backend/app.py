from flask import Flask, request, jsonify, send_from_directory, session, send_file
from flask_session import Session
from flask_cors import CORS
import psycopg2 
from config import load_config
from dotenv import load_dotenv
from auth import auth as auth_blueprint
from main import main as main_blueprint
import os, re
from cbf_pipeline.scrap import check_path
from datetime import timedelta
from middleware import needs_auth
import collaborative as col
import cbf_result as cbf_result

app = Flask(__name__)
app.debug = True
load_dotenv()

# client = MongoClient('mongodb://localhost:27017')
app.config['SECRET_KEY'] = 'random'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) 
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None' 
# app.config['SESSION_COOKIE_PATH'] = "/"
Session(app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)

CORS(app, supports_credentials=True) 


@app.route('/check_session', methods=['POST'])
@needs_auth()
def check_session(account):
    print("in check session route")
    print(account)
    print(session)
    user_id = session.get('uid')
    if user_id:
        return 'Session found'
    else:
        return 'Session not found'

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/receive-location', methods=['POST'])
def receive_location():
    location = request.json.get('location')
    location = location.lower()
    print(location)
    result = check_path(location)
    return jsonify(result)

@app.route('/uploads/<place>/<filename>', methods=['GET'])
def send_image(place, filename):
    print(place)
    print(filename)
    uploads_directory = os.getenv("UPLOADS_DIRECTORY")
    if place == "pie":
        return send_from_directory(uploads_directory, filename)
    else:
        directory = f"{uploads_directory}/{place}"
        return send_from_directory(directory, filename)

@app.route('/recommend', methods=['POST'])
def recommend():
    body = request.json
    location = body['location'].lower()
    user_rating = float(body['rating'])
    if body['restaurant_type'].lower() == 'any':
        user_restaurant_type = 'Restaurant'
    else:
        user_restaurant_type = body['restaurant_type']
    
    user_max_cost = body['max_cost'].lower()
    if user_max_cost.lower() == "inexpensive":
        user_max_cost = 0
    elif user_max_cost.lower() == "moderate":
        user_max_cost = 1
    elif user_max_cost.lower() == "expensive":
        user_max_cost = 2
    elif user_max_cost.lower() == "very expensive":
        user_max_cost = 3

    print(location)
    print(user_rating)
    print(user_restaurant_type) 
    print(user_max_cost)

    recommendations = cbf_result.cbf_main_function(user_restaurant_type, user_max_cost)
    print(recommendations)
    return jsonify(recommendations)

@app.route('/collabrecommend', methods=['POST'])
def colrecommend():
    print(session)
    user_id = session.get('uid')
    recommendations = col.main(user_id)
    
    return jsonify(recommendations)


@app.route('/restaurant_details', methods=['POST'])
def get_restaurant_details():
    data = request.json
    location = data.get('location')
    restaurant_names = data.get('restaurant_names')

    if not location or not restaurant_names:
        return jsonify({'error': 'Missing parameters'})

    restaurant_details = []
    for restaurant_name in restaurant_names:
        details = fetch_details(location, restaurant_name)
        if details:
            restaurant_details.append(details)

    print(jsonify(restaurant_details))

    return jsonify(restaurant_details[:7])

def fetch_details(location, restaurant_name):
    # file_path = "../backend/dataset/" + location

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            cur = conn.cursor()
            get_query = f"""
                SELECT rest_id, rest_name, rest_budget, main_category, rest_rating, rest_rev_count, feature_opinions, rest_location
                FROM test.restaurants
                WHERE rest_name = '{restaurant_name}'
            """
            cur.execute(get_query)
            row = cur.fetchone()

            img_name = re.sub(r'[^a-zA-Z0-9\s]', '', row[1])

            return {
                "rest_id":f"{row[0]}",
                "restaurant_name": f"{row[1]}",
                "budget": f"{row[2]}",
                "type": f"{row[3]}",
                "rating": f"{row[4]}",
                "rev_count":f"{row[5]}",
                "location":f"{row[7]}",
                "img_name": img_name,
                "feature_opinions": f"{row[6]}"
            }


    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return None

    # try:
    #     with open(os.path.join(file_path, f"{location}_profile.csv"), newline='') as csvfile:
    #         reader = csv.DictReader(csvfile)
    #         for row in reader:
    #             if row.get("restaurant_name") == restaurant_name:
    #                 return {
    #                     "restaurant_name": row.get("restaurant_name", "N/A"),
    #                     "budget": row.get("budget", "N/A"),
    #                     "type": row.get("restaurant_type", "N/A"),
    #                     "rating": row.get("avg_rating", "N/A"),
    #                     "img_file_path": file_path + "/reviews/" + restaurant_name + '/' + restaurant_name+ ".jpg",
    #                     "rec_dishes": row.get("rec_dishes", "N/A"),
    #                     "rating_graph": file_path + "/graphs/" + restaurant_name + '/' + "rating_graph.jpg",
    #                     "sentiment_graph": file_path + "/graphs/" + restaurant_name + '/' + "sentiment_graph.jpg",
    #                 }
    #     return None  # Restaurant not found
    # except Exception as e:
    #     print(f"Error fetching details from CSV: {e}")
    #     return None

if __name__ == '__main__':
    app.run()

