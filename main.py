import cv2
import os
import pickle
import face_recognition
from datetime import datetime
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendence-1ced0-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendence-1ced0.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")

# importing the mode images into a list
folder_for_mode = "Resources/Modes"
mode_path_list = os.listdir(folder_for_mode)
image_mode_list = []

for path in mode_path_list:
    image_mode_list.append(cv2.imread(os.path.join(folder_for_mode, path)))
# print(image_mode_list)


# load the encodeing filing
print("Loading Encode File.......")
file = open("EncodeFile.p", 'rb')
encode_list_with_ids = pickle.load(file)
file.close()
encodeListKnown, student_ids = encode_list_with_ids
print("Encode File Loaded")

modeType = 0
counter = 0
ids = -1
imgstudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    face_cur_fra = face_recognition.face_locations(imgS)
    encode_cur_fra = face_recognition.face_encodings(imgS, face_cur_fra)
    
    # overlaping webcam image with graphics
    imgBackground[162:162 + 480, 55:55 + 640] = img
    # overlaping with modes image
    imgBackground[44:44 + 633, 808:808 + 414] = image_mode_list[modeType]

    if face_cur_fra:
            
        for encodeface, faceloc in zip(encode_cur_fra, face_cur_fra):
            matches = face_recognition.compare_faces(encodeListKnown, encodeface)
            face_dis = face_recognition.face_distance(encodeListKnown, encodeface)
            # print(matches)
            # print(face_dis)

            matchInd = np.argmin(face_dis)
            # print(matchInd)

            if matches[matchInd]:
                # print(student_ids[matchInd])

                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=1)
                ids  =student_ids[matchInd]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # get the data
                studentInfo = db.reference(f"Students/{ids}").get()
                # print(studentInfo)

                # get teh image from
                print(ids)

                blob = bucket.get_blob(f"Images/{ids}.jpg")
                array = np.frombuffer(blob.download_as_string(), dtype=np.uint8)
                imgstudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of attendence
                datetimeObject = datetime.strptime(studentInfo["last_attendence_time"], 
                                                "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()- datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f"Students/{ids}")
                    studentInfo['total_attendence'] += 1
                    ref.child('total_attendence').set(studentInfo['total_attendence'])
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = image_mode_list[modeType]





            if modeType != 3:
                    
                if 10< counter <20:
                    modeType = 2
                
                imgBackground[44:44 + 633, 808:808 + 414] = image_mode_list[modeType]

                if counter <= 10:
                
                    cv2.putText(imgBackground, str(studentInfo['total_attendence']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(ids), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    
                    # To centarize the name
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2

                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    
                    # put image
                    imgBackground[175:175+216, 909:909+216] = imgstudent

                counter +=1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgstudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = image_mode_list[modeType]
    else:
        modeType = 0
        counter = 0
    # cv2.imshow("Face Attendance", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)