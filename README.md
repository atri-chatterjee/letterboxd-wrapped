### For letterboxd wrapped (So you don't have to pay for premium)

To get letterboxd csv go to link and click export data. 
https://letterboxd.com/settings/data/
Then in your downloads unzip file and find diary.csv. Put it in this repo and replace mine. 

Uses OMDB_API (To create key use link below and create a secrets.py file where OMDB_API_KEY = "YOUR_API_KEY")

https://www.omdbapi.com/apikey.aspx

Also, rename config_template.json to config.json. 
Insert path to Letterboxd diary in csv form at csv file path. 
Insert path to cache once created after the first api call. 