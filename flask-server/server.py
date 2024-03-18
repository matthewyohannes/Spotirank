import requests
import urllib.parse
import base64
import json
import os
from dotenv import load_dotenv

from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, origins='http://localhost:5173')



CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
app.secret_key = os.environ.get('APP_SECRET_KEY')


REDIRECT_URI = 'http://localhost:5000/callback' # replace with deployed port

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'


@app.route('/')
def index():
    
    return "Welcome to my Spotify App <a href='/login'> Login with Spotify</a>"


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-top-read' # scopes that user gives client access to
    
    params = { # params used to create the auth_url
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI, # used to force user to login each time (testing purposes only)
        'show_dialog': True
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url) # redirects user to this url

@app.route('/callback') 
def callback():
    if 'error' in request.args: # checks if there is an error inside the url given after trying to authorize
        return jsonify({"error" : request.args['error']})
    
    if 'code' in request.args:  # checks that code was retrieved in the url
        req_body = { # params used to fetch access token in the POST request
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'show_dialog': True
        }
        
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # makes POST request using auth code to get token
        response = requests.post(TOKEN_URL, data=req_body, headers=headers)

    
        if response.status_code == 200:
            token_info = response.json()
            print("Access Token: ", token_info['access_token'])
        else:
            print("Error: ", response.text)



        # adds token info to session storage
        session['access_token'] = token_info['access_token'] 
        session['refresh_token'] = token_info['refresh_token'] 
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in'] # sets time that token will expire

        return redirect('http://localhost:5173')




@app.route('/topartists')
def get_topartists():
    if 'access_token' not in session: # checks if access_token was successfully stored, if not then login
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']: # checks if token has expired by using the current time
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}" # headers for using get request to fetch access token
    }
    
    response = requests.get(API_BASE_URL + 'me/top/artists?time_range=short_term&limit=15', headers=headers) # fetches playlists
    topartists = response.json()


    # for artist in artists: # loops through artsits inside of the `items` object array of returned data
    #     print(artist['name'])
    return jsonify(topartists)

@app.route('/refresh-token')
def refresh_token():
    print("inside refresh token")
    if 'refresh_token' not in session: # checks if refresh token ever got stored, if not then login
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:

        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'show_dialog': False
        }
    
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('http://localhost:5173')
    
@app.route('/checkLoggedIn')
def check_logged_in():
    # print(session.get('access_token'))
    if 'access_token' in session and 'expires_at' in session:
        # check if the access token is present and hasn't expired
        if datetime.now().timestamp() < session['expires_at']:
            # user is logged in
            return jsonify({'loggedIn': True}), 200
    # user is not logged in
    # print("not logged in")
    return jsonify({'loggedIn': False}), 401


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get the port from the environment variable or use 5000 as a default
    app.run(host='0.0.0.0', port=port, debug=False)

