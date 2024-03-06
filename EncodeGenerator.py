import cv2
import face_recognition
import os
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://attendancems-e7e35-default-rtdb.firebaseio.com/",
    'storageBucket': 'attendancems-e7e35.appspot.com'

})

#hek lezem yn3ml add lal modes l image array
folderPath = 'images'
PathList = os.listdir(folderPath)
#print(PathList)
imgList = []
studentID = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentID.append(os.path.splitext(path)[0])
#print(studentID)

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
def findEncoding(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding started ...")
encodeListKnown = findEncoding(imgList)
encodeListKnownWithIDs = [encodeListKnown, studentID]
print("Encoding Complete ...")

#lezem nkhabi l encoding  b file mshn nsta3mlon b3dn
file = open("EncodingFile.p", 'wb')
pickle.dump(encodeListKnownWithIDs, file)
file.close()
print("File Saved")

