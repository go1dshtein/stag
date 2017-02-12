<img src="http://maxpixel.freegreatpicture.com/static/photo/1x/Antler-Funny-Deer-Brown-Moose-Animal-Mammal-159022.png" width="300">
# stag
CLI utility to fill attendance sheet

# requirements

You need: 
 - python3 as runtime
 - google api secret token
 - browser for oauth authentication
 
You can retrieve the token from this [page](https://console.developers.google.com/start/api?id=sheets.googleapis.com).
For details see [tutorial](https://developers.google.com/sheets/api/quickstart/python#step_1_turn_on_the_api_name).

# installation
As usual

    $ python3 -mvenv env
    $ . env/bin/activate
    $ pip install .
    
# usage

## setup
First of all you should set up the program with your sheet url and secret token.

    $ ./stag.py setup https://docs.google.com/spreadsheets/d/ALOTOFSYMBOLSHERE/edit#gid=362406503 file-with-oauth-token.json
    
## update
When you come to office

    $ ./stag.py start
    
And then before leave out office

    $ ./stag.py stop
