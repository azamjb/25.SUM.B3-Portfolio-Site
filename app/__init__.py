import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from peewee import *
import datetime
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    mydb = SqliteDatabase('file:memory?mode=memory&cache=shared', uri=True)
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306
    )

class TimelinePost(Model):
	name = CharField()
	email = CharField()
	content = TextField()
	created_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = mydb

mydb.connect()
mydb.create_tables([TimelinePost])


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

@app.route('/timeline')
def timeline():
    return handle_route('timeline', 'content/timeline_content.html', 'Timeline')



@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    content = request.form.get('content', '').strip()

    if not name:
        return {'error': 'Invalid name'}, 400
    if not email or '@' not in email or '.' not in email:
        return {'error': 'Invalid email'}, 400
    if not content:
        return {'error': 'Invalid content'}, 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return model_to_dict(timeline_post)

@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
	return {
		'timeline_posts': [
			model_to_dict(p)
			for p in
TimelinePost.select().order_by(TimelinePost.created_at.desc())
		]
	}

@app.route('/api/timeline_post', methods=['DELETE'])
def delete_time_line_post():
    # Find the maximum ID in the table
    max_id_query = TimelinePost.select(fn.MAX(TimelinePost.id)).scalar()
    
    if max_id_query is None:
        return jsonify({"error": "No posts found to delete."}), 404
    
    # Delete the record with the maximum ID
    row_deleted = TimelinePost.delete().where(TimelinePost.id == max_id_query).execute()
    
    if row_deleted == 0:
        return jsonify({"error": f"Post with ID {max_id_query} not found."}), 404
    else:
        return jsonify({"message": f"Post {max_id_query} deleted successfully."}), 200

    