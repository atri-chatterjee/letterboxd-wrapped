### For letterboxd wrapped (So you don't have to pay for premium)

Uses OMDB_API (To create key use link below and create a secrets.py file where OMDB_API_KEY = 'YOUR_API_KEY')
There is a secrets_template.py where you can put the key in and rename to my_secrets.py 

https://www.omdbapi.com/apikey.aspx

Also, rename config_template.json to config.json. 
Insert path to Letterboxd diary in csv form at csv file path. 
Insert path to cache once created after the first api call. 

Install pip packages before running 
``` console 
pip install -r requirements.txt
```

To run  
``` console 
python app.py 
```