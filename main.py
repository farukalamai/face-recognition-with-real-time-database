import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone

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

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    face_cur_fra = face_recognition.face_locations(imgS)
    encode_cur_fra = face_recognition.face_encodings(imgS, face_cur_fra)
    
    # overlaping webcam image with graphics
    imgBackground[162:162 + 480, 55:55 + 640] = img
    # overlaping with modes image
    imgBackground[44:44 + 633, 808:808 + 414] = image_mode_list[3]

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


    # cv2.imshow("Face Attendance", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)