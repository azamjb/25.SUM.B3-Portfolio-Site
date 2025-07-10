import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from peewee import *

load_dotenv()
app = Flask(__name__)

mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
	user=os.getenv("MYSQL_USER"),
	password=os.getenv("MYSQL_PASSWORD"),
	host=os.getenv("MYSQL_HOST"),
	port=3306
)


# For whatever reason flask can't handle using 127.0.0.1 AND localhost at the same time smh
def get_base_url():
    """Get the base URL for the current request"""
    return request.host_url.rstrip('/')

@app.route('/')
def index():
    return render_template('index.html', title="Portfolio Home", url=get_base_url(), mapbox_token=os.getenv("MAPBOX_API_TOKEN"))


def handle_route(route_name, content_template, page_title):
    """Helper function to handle both AJAX and direct page requests"""
    content = render_template(content_template, mapbox_token=os.getenv("MAPBOX_API_TOKEN"))
    
    # Check if this is an AJAX request by looking for Accept header that indicates JSON response is expected
    accept_header = request.headers.get('Accept', '')
    is_ajax = (
        'application/json' in accept_header or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.args.get('ajax') == 'true'
    )
    
    if is_ajax:
        # Return JSON for AJAX requests
        return jsonify({
            'title': page_title,
            'content': content
        })
    else:
        # Return full HTML page for direct visits/reloads
        return render_template('index.html', 
                             title=page_title, 
                             url=get_base_url(),
                             initial_content=content,
                             active_route=route_name)

@app.route('/about')
def about():
    return handle_route('about', 'content/about_content.html', 'About Page')

@app.route('/experience')
def experience():
    return handle_route('experience', 'content/experience_content.html', 'Experience')

@app.route('/education')
def education():
    return handle_route('education', 'content/education_content.html', 'Education')

@app.route('/hobbies')
def hobbies():
    return handle_route('hobbies', 'content/hobbies_content.html', 'Hobbies')

@app.route('/travel')
def travel():
    return handle_route('travel', 'content/travel_content.html', 'Travel')
