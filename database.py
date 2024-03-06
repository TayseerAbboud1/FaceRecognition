import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://attendancems-e7e35-default-rtdb.firebaseio.com/"

})
ref = db.reference('Students')

data = {
    '01':
        {
            "name": "Elon Musk",
            "Major": "Rockets",
            "Starting_Year": 2002,
            "Total_attendance": 6,
            "Standing": "G",
            "year": 4,
            "Last_attendance_time": "2023-12-19 09:29:44"
        },

    '02':
        {
            "name": "Emily Blunt",
            "Major": "Theater",
            "Starting_Year": 1998,
            "Total_attendance": 4,
            "Standing": "B",
            "year": 6,
            "Last_attendance_time": "2023-12-08 10:32:53"
        },

    '03':
        {
            "name": "Tayseer Abboud",
            "Major": "CSCI",
            "Starting_Year": 2017,
            "Total_attendance": 10,
            "Standing": "G",
            "year": 3,
            "Last_attendance_time": "2023-12-19 09:31:06"
        },
}
for key, value in data.items():
    ref.child(key).set(value)
