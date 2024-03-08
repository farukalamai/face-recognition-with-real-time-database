import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendence-1ced0-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "2005001":
    {
        "name": "Elon Musk",
        "major": "Space",
        "starting_year": 2017,
        "total_attendence": 6,
        "standing": "6",
        "year": 4,
        "last_attendence_time": "2024-01-01 00:54:34"
    },
    "2005007":
    {
        "name": "Sumon",
        "major": "AET",
        "starting_year": 2018,
        "total_attendence": 7,
        "standing": "7",
        "year": 5,
        "last_attendence_time": "2023-01-01 00:54:34"
    },
    "2005064":
    {
        "name": "Faruk",
        "major": "CSE",
        "starting_year": 2019,
        "total_attendence": 10,
        "standing": "9",
        "year": 6,
        "last_attendence_time": "2022-01-01 00:54:34"
    }  
}

for key, value in data.items():
    ref.child(key).set(value)