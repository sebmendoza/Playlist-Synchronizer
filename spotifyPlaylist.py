from itertools import count
from re import search
import ssl
from turtle import end_fill
from unicodedata import name
from xml.sax.handler import DTDHandler
import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth # allows us to authenticate the user

import json
load_dotenv()


def CreatePlaylist():
    playlist_name = input("Enter a playlist name: ")
    playlist_description = input("Enter a playlist description: ")
    spotifyObject.user_playlist_create(user=username,name=playlist_name,public=True,description=playlist_description)  # function to create playlist
    return playlist_name, playlist_description

def SearchQueries():
    file = open("PLAYLISTNAME.txt", "r",  encoding="utf-16")  #encoding makes sure we can read the file in english instead of unicode
    
    # readlines() returns a list where each line is a string element
    data = file.readlines()
    set = [] #the complete info we want after reading 

    for current_line in data:
        wanted_queries = []

        # creating a split list of each line
        split_list = (current_line.split('\t'))

        title = split_list[0]  # song name
        real_title = ""

        # apple music includes long features in their song titles.
        # this is makes titles really specific and sometimes we can get no results when we
        # query the Spotify API, these long features are wrapped in brackets
        # so we can stop the title when we see an bracket and just use the song name
        # example title for apple music: 12.38 (feat. 21 Savage, Ink & Kadhja Bonet)
        # after the cut: 12.38
        for letter in range(0, len(title)-1):
            if title[letter] == '(':
                real_title = title[0:letter-1]

        if real_title:
            query = real_title + " " + split_list[1]
            wanted_queries.append(query)
        else:
        # add wanted columns to our search query
            query = split_list[0] + " " + split_list[1]
            wanted_queries.append(query)
    
        # add wanted col to complete set
        set.append(wanted_queries)

    set.pop(0) # Removes [Name, Artist]
    return set



scope = 'playlist-modify-public' # tells spotify what we want to do 
username = os.getenv('SPOTIFY_USER')

token = SpotifyOAuth(scope=scope,username=username)
spotifyObject = spotipy.Spotify(auth_manager=token) # this creates our object, need to read documentation

CreatePlaylist()
search_queries = SearchQueries()

## you can easily edit this based on your size of playlist
all_tracklists = []
track_uris_v1 = []
track_uris_v2 = []

for i in range(len(search_queries)):
    track = search_queries[i]
    result = spotifyObject.search(q=track, limit=3, offset=0, type='track')
    json.dumps(result, sort_keys=True, indent=4)

    uri = result['tracks']['items'][0]['uri']
    if len(track_uris_v1) >= 99:
        track_uris_v2.append(uri)
    else: 
        track_uris_v1.append(uri)



# accessing the playlist we just created
users_playlists = spotifyObject.user_playlists(user=username)
playlist = users_playlists['items'][0]['id']

all_tracklists.append(track_uris_v1)
all_tracklists.append(track_uris_v2)


# add songs to the playlist
for t in all_tracklists:
    spotifyObject.user_playlist_add_tracks(user=username,playlist_id=playlist, tracks=t)


# TODO: Ask the user for the specifications of how big the playlist is. Then we can make appropriate things