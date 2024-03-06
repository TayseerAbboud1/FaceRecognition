import os
import pickle
import cv2
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://attendancems-e7e35-default-rtdb.firebaseio.com/",
    'storageBucket': 'attendancems-e7e35.appspot.com'})


bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("resources/background.png")
# hek lezem yn3ml add lal modes bl image array
folderModePath = 'resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# get and load the encoding file
print("Loading Encoding file ...")
file = open('EncodingFile.p', 'rb')
encodeListKnownWithIDs = pickle.load(file)
file.close()
encodeListKnown, studentID = encodeListKnownWithIDs
print("Encoding file loaded successfully ...")
print(studentID)
modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches", matches)
        # print("face distance", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("matchIndex", matchIndex)

        if matches[matchIndex]:
            print("Face detected ...")
            print(studentID[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentID[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1
    if counter != 0:
        if counter == 1:
            studentInfo = db.reference(f'Students/{id}').get()
            print(studentInfo)

            blob = bucket.get_blob(f'images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            ref = db.reference(f'Students/{id}')
            studentInfo['Total_attendance'] += 1
            ref.child('Total_attendance').set(studentInfo['Total_attendance'])

        if 10<counter<20:
                modeType = 2
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if counter<=10:
                cv2.putText(imgBackground, str(studentInfo['Total_attendance']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['Major']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['Standing']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['Starting_Year']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w)//2

                cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                imgBackground[175:175+216, 909:909+216] = imgStudent
        counter+=1

        if counter >= 20:
            counter = 0
            modeType = 0
            studentInfo = []
            imgStudent = []
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        # cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(10)
