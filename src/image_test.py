import requests

# http://www.omdbapi.com/?t=Gladiator&y=2000

title = input("Movie title: ").strip()
apikey = 'f34d45dd'

url = f'http://www.omdbapi.com/?t={title}&apikey={apikey}'

response = requests.get(url)
response.raise_for_status()

data = response.text

# print(data)

import json

data = json.loads(data)

poster_url = data['Poster']

# print(poster_url)

poster_content = requests.get(poster_url).content

