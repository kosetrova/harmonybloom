#importing libraries
from openai import AzureOpenAI
import spotipy
import os
import json
import spotipy.util as util


#setting up OpenAI credentials
client = AzureOpenAI(
	azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
	api_key	= os.getenv("AZURE_OPENAI_KEY"),
	api_version = "2023-10-01-preview"
)


#reading Spotify API credentials from JSON file
credentials = "spotipy_keys.json"
with open(credentials, "r") as keys:
	api_tokens = json.load(keys)


#setting up Spotify Authentication
client_id = api_tokens["client_id"]
client_secret = api_tokens["client_secret"]
redirectURI = api_tokens["redirect"]
username = api_tokens["username"]

scope = 'user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public'
token = util.prompt_for_user_token(username, scope, client_id=client_id,
						   client_secret=client_secret,
						   redirect_uri=redirectURI)

sp = spotipy.Spotify(auth=token)



#creating spotify playlist

def find_songs(flower): 
	#Chat GPT response has 2 parts. Split function separates flower name from description with ":"
	flower_name=flower.split(":")
	#Searching for 10 songs using just the flower's name 
	search_results = sp.search(q=flower_name[0], type = 'track', limit=10)
	song = search_results['tracks']['items']
	track_selection_list = []
	for track in song:
		track_selection_list.append(track['uri'])

	#Working with Spotify API to generate a playlist
	#The name of the playlist changes depending on the birthday flower

	my_playlist = sp.user_playlist_create(user=username, name=f'❀ {flower_name[0]} ❀', public=True, description=f"This is your birthday flower playlist!")
	results = sp.user_playlist_add_tracks(username, my_playlist['id'], track_selection_list)
	playlist_link = my_playlist['external_urls']['spotify']

	#Separating the link into parts to get the id for further widget integration
	first_part_key_link = playlist_link.replace("https://open.spotify.com/playlist/", "")
	separator = "?"
	key_link = first_part_key_link.split(separator, 1)[0]
	embed_link = f"https://open.spotify.com/embed/playlist/{key_link}?utm_source=generator"
	playlist_id = my_playlist["id"]
	return (flower, embed_link)



#Passing a message to ChatGPT 
#To generate the name of the flower and its meaning based on user's input date in a format of flower_name:explanation
def gpt_find_song(question):
	my_messages = [
		{"role": "system", "content": """Name of the birthday flower based on user input date and month. 
		In the next sentence explain the meaning of the flower and tell a fortune in a mysterious manner. print it without brackets and urls, 
		please use the following format: flower_name: explanation"""},
		{"role": "user", "content": question}
	]

	response = client.chat.completions.create(
			# left side, defined by the API
			# right side, defined by us
			model="GPT-4",
			messages = my_messages
		)

	response_flower = response.choices[0].message.content

	return find_songs(response_flower)