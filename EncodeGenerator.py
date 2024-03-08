import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendence-1ced0-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendence-1ced0.appspot.com"
})

# importing student images
folder = "Images"
path_list = os.listdir(folder)
image_list = []
student_ids = []

for path in path_list:
    image_list.append(cv2.imread(os.path.join(folder, path)))
    sid = path.split(".")[0]
    # print(sid)
    student_ids.append(sid)
    filename = os.path.join(folder, path)
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)



print(len(image_list))


def findEncoding(imgList):
    encode_list = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list

print("Encode Started.....")
encodeListKnown = findEncoding(image_list)
encodeListKNownWithIds = [encodeListKnown, student_ids]
print("Encode Started.....")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKNownWithIds, file)
file.close()
print("File Saved")