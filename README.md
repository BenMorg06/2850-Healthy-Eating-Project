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

Now when in your branch you can import the food data into the database by running
```console
python import_food_data.py
```
And then check if the food data has been imported by running
```console
python check_food_db.py
```
