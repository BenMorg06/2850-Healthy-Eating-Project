# Good Food & Healthy Eating
## Group 27

Alex Blake
Bakarina Kebe
Benjamin Morgan
David Huang
Yuanqing Gao

## Setting up food data

The data for macros and nutritional information on food comes from the McCance & Widdowson CoFID
For development branch the 'implementation-branch' with
```console
git checkout implementation-branch
git branch 'your-feature'
git checkout 'your-feature'
```

```console
pip install -r requirements.txt
```

Now when in your branch you can import the food data into the database by running
```console
python import_food_data.py
```
And then check if the food data has been imported by running
```console
python check_food_db.py
```

## To run tests
```
pytest
```

## To run the webpage server
```console
python run.py
```
This will return a local host address which you can click on and access webpage
In future we hope to run the page on a server and have users visit the website from their own devices
This feature was trialed with the use of ngrok, and users were able to access the webpage on their own devices
Commands used for this were
```console
flask --app flaskr run --host=0.0.0.0 --port=5001
ngrok http 5001
```
This returned a url which was given to users
