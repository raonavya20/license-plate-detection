from os import read
import cv2
import pytesseract
import sqlite3
import datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

conn = sqlite3.connect("database.db")

harcascade = "model/haarcascade_russian_plate_number.xml"

cap = cv2.VideoCapture(0)

cap.set(3, 640) # width
cap.set(4, 480) #height

min_area = 500
count = 0

while True:
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x,y,w,h) in plates:
        area = w * h
        wT,hT,cT=img.shape
        a,b=(int(0.02*wT),int(0.02*hT))
        plate=img[y+a:y+h-a,x+b:x+w-b,:]
        
        if area > min_area:            
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(img, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
            read=pytesseract.image_to_string(plate)
            read=''.join(e for e in read if e.isalnum())

            img_roi = img[y: y+h, x:x+w]
            cv2.imshow("ROI", img_roi)

    cv2.imshow("Result", img)

    # Print the extracted license plate number
    print("License plate number:", read)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        # cv2.imwrite("plates/scaned_img_" + str(count) + ".jpg", img_roi)
        cv2.rectangle(img, (0,200), (640,300), (0,255,0), cv2.FILLED)
        cv2.putText(img, "Plate Saved", (150, 265), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 2)
        cv2.imshow("Results",img)
        cv2.waitKey(500)
        count += 1

    #connect the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    license_number = read
    entry_time = datetime.datetime.now().strftime('%H:%M:%S')

    # check if the license number already exists in the table
    c.execute("SELECT * FROM LicenseTable WHERE number = ?", (license_number,))
    row = c.fetchone()

    if row is not None:
        # if the license number already exists, update the entry time for the existing row
        c.execute("UPDATE LicenseTable SET entry_time = ? WHERE number = ?", (entry_time, license_number))
    else:
        # if the license number does not exist, insert a new row with the license number and entry time
        c.execute("INSERT INTO LicenseTable (number, entry_time) VALUES (?, ?)", (license_number, entry_time))

    conn.commit()
    conn.close()



