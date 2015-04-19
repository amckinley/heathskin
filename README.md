# heathskin

heathskin is used for providing useful game-tracking information in real-time,
and statistically over many games.


# get heathskin
clone from github. inside the repo:
```
  pip install -r requirements.txt
  pip install -e .
```

# update your heathskin logging config
mac: `cp config/log.config  ~/Library/Preferences/Blizzard/Hearthstone/log.config`

windows: `copy config\log.config %LOCALAPPDATA%\Blizzard\Hearthstone\log.config`

# starting heathskin
Just start a single webserver so you can play with it:

`heathskin-frontend`

Start 5 web servers with a HAProxy server in front of it:

`circusd config/circus.ini`

Then go to your browser to create an account: localhost:3000/register

Then start the uploader:

`heathskin-uploader --username foo@bar.com --password fizzbuzz`
