import sqlite3, requests, secrets
from flask import Flask, render_template, redirect, request, session, url_for

app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.secret_key = secret_key
CANVAS_DOMAIN = 'nau-canvastest.beta.instructure.com'
CLIENT_ID = 2648500000000001
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob' 
CLIENT_SECRET = 'eNvEe7AVEPFw42w4LyYF4Rav9EQ6tMy3CZnhLMWyXrcvuefFK8A4HuMk3yFVQA'

def data():
    global courses1
    with sqlite3.connect(":memory:") as database:
        cursor = database.cursor()
        cursor.execute("CREATE TABLE courses(name TEXT)")
    for coursee in courses1:
            cursor.execute("INSERT INTO courses (name) VALUES(?)",
                       (coursee["name"],))
    cursor.execute("SELECT * FROM courses")
    return cursor.fetchall()
    
@app.route('/login')
def login():
    auth_url = (f'https://{CANVAS_DOMAIN}/login/oauth2/auth?client_id={CLIENT_ID}&response_type=code&redirect_uri=urn:ietf:wg:oauth:2.0:oob')
    return redirect(auth_url)
         
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/courses')
def get_courses():
    global client
    global courses1
    if 'access_token' in session:
        access_token = session['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'https://{CANVAS_DOMAIN}/api/v1/users/self/courses', headers=headers)
        response.raise_for_status()
        
        courses1 = response.json()
        courses = data()
        return render_template('courses.html', courses=courses)
    else:
        return redirect(url_for('login'))

@app.route('/oauth/callback', methods=['GET', 'POST'])
def oauth_callback():
    global courses 
    if request.method == 'POST':
        code = request.form['code']
        token_url = f'https://{CANVAS_DOMAIN}/login/oauth2/token'
        payload = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'code': code
        }
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data['access_token']
        session['access_token'] = access_token
        return render_template('authorized.html')
    else:
        return '''
        <h1>Enter the authorization code</h1>
        <form method="post">
            <label for="code">Authorization Code:</label>
            <input type="text" id="code" name="code" required>
            <input type="submit" value="Submit">
        </form>
        '''
    
if __name__ == '__main__':
    app.run(debug=True)
