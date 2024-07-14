# All spotify api functions, called upon in views.py
import requests
import base64
import json
from pprint import pprint
import os
# I used the spotify api for this project. To authenticate a token you need to include a client id and secret from spotify.
# This should not be revealed in production so something like environment variables/files should be used to store these.
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes),'utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization":"Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data={
        "grant_type": "client_credentials"
    }
    result = requests.post(url,headers=headers,data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    expiration_time = json_result['expires_in']
    return token, expiration_time

def get_auth_header(token):
    return {"Authorization":"Bearer " + token}

def song_search(artist_name,track,token):
    url = "https://api.spotify.com/v1/search"
    
    headers = get_auth_header(token)
    query = f"?q={artist_name},{track}&type=artist,track&limit=1"

    query_url = url+query
    result = requests.get(query_url,headers=headers)
    json_result = json.loads(result.content)
    
    return json_result



# album cover img
# pprint(result['tracks']['items'][0]['album']['images'][2]['url'])

# #snippit
# pprint(result['tracks']['items'][0]['preview_url'])
# # link to spotify song
# pprint(result['tracks']['items'][0]['external_urls']['spotify'])






