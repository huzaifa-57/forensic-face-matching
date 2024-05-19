from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QStyle
from passporteye import read_mrz
import sqlite3
import os
import sys
import filetype
import cv2
import dlib
import numpy as np
import pandas as pd
import webbrowser
from numpy import dot
from numpy.linalg import norm
from report_generator import generate_report
import time
import torch
from PIL import Image
from torchvision import transforms
from mtlface.face_aligment import face_process
from layout import interface
torch.autograd.set_grad_enabled(False)

class Modules(interface.Ui_MainWindow):
    def __init__(self, MainWindow):
        # Calling Parent Constructor
        super().__init__(MainWindow)

        # Declaring variables for the project
        self.var = ''
        self.path_pas = ''
        self.path_pe = ''
        self.count = 5
        self.logic = False
        self.per_ver = False
        self.value = 1
        self.start_timer = 0
        self.end_timer = 0
        self.metadata = {"passport": "",
                         "Name": "",
                         "Gender": "", 
                         "Country": "",
                        }
        self.report = {"passport_num": "",
                       "name": "",
                       "gender": "",
                       "country":"",
                       "pn_manual": 0,
                       "passport_face_detected": 0,
                       "passport_verified": 0,
                       "passport_similarity": 0.0,
                       "passport_verification_time": 0.0,
                       "person_face_detected": 0,
                       "person_verified": 0,
                       "person_varification_time": 0.0,
                       "person_similarity": 0.0,
                       "total_time": 0.0,
                       "date": "",
                       "time": ""}
        
        # Button Mapping
        self.up_passport_btn.clicked.connect(self.upload_passport)  # Modify
        self.verify_passport_btn.clicked.connect(self.seq_for_pass_verfication)  # Modify
        self.up_pass_no_btn.clicked.connect(self.seq_for_m_pass_verfication)
        self.close_btn.clicked.connect(self.close_win)
        self.min_btn.clicked.connect(self.min_win)
        self.up_person_btn.clicked.connect(self.upload_person)
        self.up_person_btn.setEnabled(False)
        
        self.open_cam_btn.clicked.connect(self.open_webcam)
        self.open_cam_btn.setEnabled(False)
        self.report_gen_btn.clicked.connect(self.report_gen)

    # Interface Maipulation
    def close_win(self):
        try:
            conn.commit()
            cur.close()
            conn.close()

            if os.path.exists('temp/pass_face.png'):
                os.remove('temp/pass_face.png')
                print('Image pass_face.png has been removed on closing')
            if os.path.exists('temp/db_face.png'):
                os.remove('temp/db_face.png')
                print('Image db_face.png has been removed on closing')
            if os.path.exists('temp/person_face.png'):
                os.remove('temp/person_face.png')
                print('Image person_face.png has been removed on closing')
        except:
            print("Error in closing Database and removing pictures")
            sys.exit(503)
        finally:
            sys.exit(0)

    def min_win(self):
        MainWindow.setWindowState(self.windowState() | QtCore.Qt.WindowState.WindowMinimized)

    # Functionalities & Modules
    # Passport Verification Module
    def upload_passport(self):
        try:
            if not os.path.exists('temp'):
                os.mkdir('temp')
            if os.path.exists("temp/db_face.png"):
                os.remove("temp/db_face.png")
            if os.path.exists("temp/pass_face.png"):
                os.remove("temp/pass_face.png")
            if os.path.exists('temp/person_face.png'):
                os.remove('temp/person_face.png')
            self.report = {"passport_num": "",
                       "name": "",
                       "gender": "",
                       "country": "",
                       "pn_manual": 0,
                       "passport_face_detected": 0,
                       "passport_verified": 0,
                       "passport_similarity": 0,
                       "passport_verification_time": 0,
                       "person_face_detected": 0,
                       "person_verified": 0,
                       "person_varification_time": 0,
                       "person_similarity": 0,
                       "total_time": 0,
                       "date": "",
                       "time": ""}
            
            self.start_timer = time.time()
            self.cam_per_btn(action=False)
            self.wind_reset()
            filename = QFileDialog.getOpenFileName()
            filename = filename[0]
            if(len(filename) != 0):
                if filetype.is_image(filename):
                    self.var = "-- Selected file is valid image.\n" + self.var
                    self.path_pas = filename
                    self.passport.setPixmap(QPixmap(self.path_pas))
                    self.status_update(message="", color="black")
                    self.var = "-- Passport Data Page is uploaded successfully.\n   Path: " + self.path_pas  +"\n"+ self.var
                    self.plainTextEdit.setPlainText(self.var)
                    self.prog_update(value=0, inc=10)
                    message = "Passport Data Page is uploaded successfully.\nPath: " + self.path_pas
                else:
                    self.status_update(message="Select the Passport Image!", color="red")
                    self.var = "-- Selected file is NOT an Image.\n" + self.var
                    self.plainTextEdit.setPlainText(self.var)
                    message = "Passport Data Page is not selected"
            else:
                self.path_pas = ''
                self.status_update(message="Please Upload Passport Image!", color="red")
                self.passport.setPixmap(QPixmap(None))
                self.plainTextEdit.setPlainText(self.var)
                message = "Passport Data page is not uploded"
        except Exception as e:
            self.var = "-- Error Occur: " + str(e) + "\n" + self.var
            message = "-- Error Occur: " + str(e)
            self.plainTextEdit.setPlainText(self.var)

        self.log_reg(log_hist=message, passport_no="")

    def seq_for_pass_verfication(self):
        if (len(self.path_pas) != 0):
            curr_time = 0
            pn = self.passport_num_extract()
            if (pn != 0):
                dbf = self.fetch_DB_photo(pn)
                if (dbf != 0):
                    self.db_name.setText(" "+self.metadata["Name"])
                    if self.metadata["Gender"] == 'M':
                        self.db_gender.setText(" Male")
                    elif self.metadata["Gender"] == 'F':
                        self.db_gender.setText(" Female")
                    self.db_passNo.setText(str(" "+self.metadata['passport']))
                    self.db_nationality.setText(" "+self.metadata["Country"])
                    start = time.time()
                    pf = self.pass_face_detect()
                    if (pf != 0):
                        self.pass_verification()
                        end = time.time()
                        curr_time = end - start
                    self.cam_per_btn(action=True)
                    self.report["passport_verification_time"] = curr_time
            self.plainTextEdit.setPlainText(self.var)
        else:
            self.status_update(message="Please Upload the Passport Image!", color="red")
            self.plainTextEdit.setPlainText(self.var)
            message = "Passport Image not uploaded"
            self.log_reg(log_hist=message, passport_no="")

    def seq_for_m_pass_verfication(self):
        if (len(self.path_pas) != 0):
            curr_time = 0
            pn = self.pass_no_le.text()
            if (len(pn) != 9):
                self.status_update("Invalid Passport Number! 🚫", color="red")
                message = "Invalid Passport Number. Passport Number Entered: {}".format(pn)
                self.log_reg(log_hist=message, passport_no=pn)
            else:
                if os.path.exists("temp/db_face.png"):
                    os.remove("temp/db_face.png")
                if os.path.exists("temp/pass_face.png"):
                    os.remove("temp/pass_face.png")
                
                self.cam_per_btn(action=False)
                self.wind_reset()
                # self.passport.setPixmap(QPixmap(self.path_pas))
                self.report['pn_manual'] = 1
                self.report['passport_num'] = pn
                self.prog_update(value=10, inc=10)
                dbf = self.fetch_DB_photo(pn)
                if (dbf != 0):
                    self.db_name.setText(" "+self.metadata["Name"])
                    if self.metadata["Gender"] == 'M':
                        self.db_gender.setText(" Male")
                    elif self.metadata["Gender"] == 'F':
                        self.db_gender.setText(" Female")
                    self.db_passNo.setText(str(" "+self.metadata['passport']))
                    self.db_nationality.setText(" "+self.metadata["Country"])
                    start = time.time()
                    pf = self.pass_face_detect()
                    if (pf != 0):
                        self.pass_verification()
                        end = time.time()
                        curr_time = end - start
                    self.report["passport_verification_time"] = curr_time
                    self.cam_per_btn(action=True)
            self.plainTextEdit.setPlainText(self.var)
        else:
            self.status_update("Please Upload the Passport Image!", color="red")
            self.passport.setPixmap(QPixmap(None))
            self.plainTextEdit.setPlainText(self.var)
            message = "Passport Image not uploaded"
            self.log_reg(log_hist=message, passport_no="")

    def passport_num_extract(self):
        mrz = read_mrz(self.path_pas)
        if(mrz == None):
            self.status_update(message="Passport number extraction FAILED ❌.", color="red")
            message = "Passport Number Extraction failed"
            val = 0
        else:
            mrz_data = mrz.to_dict()
            pn = mrz_data['number']
            self.metadata["passport"] = pn
            self.report['passport_num'] = pn
            self.var = "-- Passport Number is extracted successfully.\n   Passport Number:"+ pn +"\n"+ self.var
            message = "Passport Number Extraction Completed. Passport Number: {}".format(pn)
            val = self.metadata['passport']
        self.prog_update(value=10, inc=10)
        self.log_reg(log_hist=message, passport_no=str(val))
        return val

    def fetch_DB_photo(self, pn):
        pass_no = pn
        cur.execute('SELECT name, gender, country, photo FROM Users WHERE pass_no = ?', (pass_no,))
        db_data = cur.fetchall()
        val = 0
        if (len(db_data) == 0):
            self.status_update(message="Passport Number NOT found in Database! ❌", color="red")
            message = "Passport Number not Found in Database"
        else:
            for i in db_data:
                person_name = i[0]
                self.metadata["passport"] = pass_no
                self.metadata["Name"] = person_name
                self.report['name'] = person_name
                self.report["gender"] = i[1]
                self.report["country"] = i[2]
                self.metadata["Gender"] = i[1]
                self.metadata["Country"] = i[2]
                person_photo = i[3]
            db_f = "temp/db_face.png"
            with open(db_f, 'wb') as f:
                f.write(person_photo)
            f.close()

            temp = face_process(db_f, plot=False)
            temp.save(db_f)
            temp.close()
            self.db_face.setPixmap(QPixmap(db_f))
            self.var = "-- Database Photo Fetched successfully.\n   Person Name: " + person_name + "\n" +"-- Passport Number Matched successfully.\n" +  self.var
            message = "Database photo fetched successfully. Person Name:{}\nPassport Number Matched Successfully".format(person_name)
            val = 1
        self.prog_update(value=20, inc=10)
        self.log_reg(log_hist=message, passport_no=str(self.metadata['passport']))
        return val
        
    def pass_face_detect(self):
        path = self.path_pas
        face_location = face_process(path, plot=False)
        val = 0
        if (face_location is None):
            self.status_update(message="Face NOT detected! ❌", color="red", bg_color='rgb(255, 215, 215)')
            message = "Face not detected in the photo"
        else:
            pass_f = "temp/pass_face.png"
            face_location.save(pass_f)
            self.passport_face.setPixmap(QPixmap(pass_f))
            face_location.close()
            message = "Face detected successfully"
            val = 1
        self.prog_update(value=30, inc=10)
        self.report["passport_face_detected"] = val
        self.log_reg(log_hist=message, passport_no=str(self.metadata['passport']))
        return val

    def pass_verification(self):
        results = self.ver_module('pass_face.png', 'db_face.png')
        result = round(results * 100)
        if results >= 0.75:
            verify = 1
            self.pass_box(message="{}%".format(result), color="rgb(215, 255, 215)")
            self.status_update(message="Passport is verified ✔️", color='green', bg_color='rgb(215, 255, 215)')
            self.label_6.setText("Passport face ✔️")
            message = "Face on passport matched successfully\n"
            if self.count <= 0:
                self.count = 5
            
        else:
            verify = 0
            self.status_update(message="Passport Face Not Matched! ❌", color='red', bg_color='rgb(255, 215, 215)')
            self.label_6.setText("Passport Face ❌")
            self.pass_box(message="{}%".format(result), color="rgb(255, 215, 215)")
            message = "Face on passport NOT matched"
            self.count = 5
        print("Passport Page and Database Photo similarity: ", results)
        self.prog_update(value=40, inc=10)
        self.report["passport_verified"] = verify
        self.report["passport_similarity"] = float(results)
        self.log_reg(log_hist=message, passport_no=str(self.metadata['passport']))

    # Person Verification Module
    def upload_person(self):
        if os.path.exists("temp/person_face.png"):
            os.remove("temp/person_face.png")
        self.person_face.setPixmap(QPixmap(None))
        self.person.setPixmap(QPixmap(None))
        self.pers_box(message="", color="rgb(220, 230, 220)")
        filename = QFileDialog.getOpenFileName()
        filename = filename[0]
        if (len(filename) != 0):
            if filetype.is_image(filename):
                self.var = "-- Selected file is valid image.\n" + self.var
                self.path_pe = filename
                self.person.setPixmap(QPixmap(self.path_pe))
                self.prog_update(value=50, inc=10)
                self.status_update(message="", color='black')
                self.var = "-- (Person's Photo is uploaded successfully.)\nPath: " + self.path_pe + "\n" + self.var
                self.plainTextEdit.setPlainText(self.var)
                message = "Selected image is a valid image. Path: {}".format(self.path_pe)
                self.seq_for_person_verfication()
            else:
                self.s_status.setText("Select valid image!")
                self.s_status.setStyleSheet("QLabel{color:'red'; background-color:rgb(255,235,235); font-weight: bold; border: 2px solid gray;}")
                self.var = "-- Selected file is NOT an Image.\n" + self.var
                message = "Selected Invalid Image. Path: {}".format(filename)
                self.plainTextEdit.setPlainText(self.var)
        else:
            self.s_status.setText("Please select Person's Image!")
            self.s_status.setStyleSheet("QLabel{color:'red'; background-color:rgb(255,235,235); font-weight: bold; border: 2px solid gray;}")
            self.plainTextEdit.setPlainText(self.var)
            self.label_8.setText("Live Face")
            message = "Image is not selected"
        
        self.log_reg(log_hist=message, passport_no=str(self.metadata['passport']))

    def seq_for_person_verfication(self):
        if (len(self.path_pe) != 0):
            curr_time = 0
            if self.count <= 5 and self.count > 0:
                self.progressBar.setValue(60)
                self.progressBar.setProperty('value', self.progressBar.value())
                start = time.time()
                pf = self.per_face_detect()
                if (pf != 0):
                    self.per_verification()
                    end = time.time()
                    if self.per_ver is True:
                        self.count = 5
                    elif self.per_ver is False:
                        self.count = self.count  - 1
                    else:
                        print('Try again...')
                    curr_time = end - start
                self.report["person_varification_time"] = curr_time
                self.report_write()
            else: 
                self.status_update(message="Verification attempts limit Exceeded ⛔", color='red')
                self.plainTextEdit.setPlainText('-- Person Verification attempt limits exceeded.\n> Person does not have any match with the Database.\n> Call the Authorities!\n')
                message = "Verification attempts limit Exceeded"
                self.pass_box(message="", color="rgb(220, 230, 220)")
                self.label_8.setText("Live Face")
                self.log_reg(log_hist=message, passport_no=self.metadata['passport'])
        else:
            self.status_update(message="Please select Person's Image!", color="red")
            message = "Image is not selected"
            self.label_8.setText("Live Face")
            self.plainTextEdit.setPlainText(self.var)
            self.log_reg(log_hist=message, passport_no=str(self.metadata['passport']))

    def per_face_detect(self):
        path = self.path_pe
        val = 0
        person_img = face_process(path, plot=False)
        if person_img is None:
            self.status_update(message="Person Face NOT Detected", color='red', bg_color='rgb(255, 215, 215)')
            message = "Person face NOT Detected"
        else:
            per_f = "temp/person_face.png"
            person_img.save(per_f)
            
            self.person_face.setPixmap(QPixmap(per_f))
            message  = "Person face detected"
            val = 1
        self.prog_update(value=60, inc=20)
        self.report["person_face_detected"] = val
        self.log_reg(log_hist=message, passport_no=self.metadata['passport'])
        return val

    def per_verification(self):
        if (len(self.path_pas) != 0):
            results = self.ver_module('db_face.png', 'person_face.png')
            result = round(results * 100)
            verify = 0
            if results >= 0.5:
                verify = 1
                self.status_update(message="Person is verified   ✔️", color='green', bg_color='rgb(215, 255, 215)')
                self.label_8.setText("Live Face ✔️")
                self.pers_box(message="{}%".format(result), color="rgb(215,255,215)")
                message = "Person is verified"
                self.per_ver = True
            else:
                self.status_update(message="Person is not verified   ❌", color='red', bg_color='rgb(255, 215, 215)')
                self.label_8.setText("Live Face ❌")
                self.pers_box(message="{}%".format(result), color="rgb(255, 215, 215)")
                self.per_ver = False
                message = "Person is not verified"
            print("Person's Live and Database Photo similarity: ", results)
            self.prog_update(value=80, inc=20)
            self.report["person_verified"] = verify
            self.report["person_similarity"] = float(results)
        else:
            self.status_update(message="⚠️ Please Upload the Passport Image!", color='red')
            message = 'Passport Image has not uploaded'
        self.end_timer = time.time()
        self.report["total_time"] = self.end_timer - self.start_timer
        self.log_reg(log_hist=message, passport_no=self.metadata['passport'])
    
    def open_webcam(self):
        self.status_update(message="Opening Live Video Feed...", color='black')
        print('Opening Live Video Feed...')
        cap_f = "temp/person_face.png"
        self.all_btn(action=False)
        gaze_direction = "center"
        if os.path.exists(cap_f):
            os.remove(cap_f)
        try:
            cap = cv2.VideoCapture(0)
            self.log_reg(log_hist='Camera Opens', passport_no=self.metadata['passport'])
            while cap.isOpened():
                ret, frame = cap.read()
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                faces_dlib = face_detector(frame)
                roi_color = frame.copy()
                self.status_update(message="🔍 Detecting Face, Get in Center of Screen...", color='red')
                for (x, y, w, h), face in zip(faces, faces_dlib):
                    color = (0, 0, 255) # Default Red
                    landmarks = landmark_detector(frame, face)
                    points = [(p.x, p.y) for p in landmarks.parts()]
                    left_eye = landmarks.part(36)
                    right_eye = landmarks.part(45)
                    nose = landmarks.part(30)

                    left_eye_dist = int(np.round(np.sqrt((nose.x - left_eye.x)**2 + (nose.y - left_eye.y)**2)))
                    right_eye_dist = int(np.round(np.sqrt((nose.x - right_eye.x)**2 + (nose.y - right_eye.y)**2)))

                    if x + w//2 > gray.shape[1]//2 - w//4 and x + w//2 < gray.shape[1]//2 + w//4:
                        color = (0, 255, 0) # Turns green if face is detected
                        if left_eye_dist > right_eye_dist:
                            gaze_direction = "right"
                            self.status_update(message="Turn your Face LEFT...", color='green')
                        elif left_eye_dist < right_eye_dist:
                            gaze_direction = "left"
                            self.status_update(message="Turn your Face RIGHT...", color='green')
                        elif left_eye_dist == right_eye_dist:
                            gaze_direction = "center"
                            

                        print("Right Eye:   ", right_eye_dist, "    Left Eye:   ", left_eye_dist)


                        if gaze_direction == "center":
                            self.status_update(message="Face Detected! Taking Picture... ✔️", color='green')
                            self.log_reg(log_hist='Face captured', passport_no=self.metadata['passport'])
                            print("Face Captured...")
                            if self.logic is False:
                                self.logic = True
                        
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)

                self.displayImage(frame)

                cv2.waitKey(0)

                if self.logic is True:
                    print('Taking Picture...')
                    self.log_reg(log_hist='Picture taken', passport_no=self.metadata['passport'])
                    cv2.imwrite(cap_f, roi_color)
                    self.logic = False
                    self.person.setPixmap(QPixmap(cap_f))
                    self.path_pe = cap_f
                    break
            cap.release()
            cv2.destroyAllWindows()
            self.prog_update(value=50, inc=10)
            self.seq_for_person_verfication()
        except Exception as e:
            self.status_update(message="Problem with the CAMERA! Kindly Check...", color='red')
            print("Error: {}".format(e))
           
        self.all_btn(action=True)
        
    def displayImage(self, img):
        qformat = QImage.Format.Format_Indexed8
        # print(qformat)
        if len(img.shape) == 3:
            if(img.shape[2]) == 4:
                qformat = QImage.Format.Format_RGBA8888
            else:
                qformat = QImage.Format.Format_RGB888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()
        self.person.setPixmap(QPixmap.fromImage(img))

    # Verification Module
    def ver_module(self, main_face_to_compare_with='',  face_to_compare=''):
        root = 'temp/'
        images = []
        for fname in [main_face_to_compare_with, face_to_compare]:
            path = os.path.join(root, fname)
            input_img = Image.open(path).convert("RGB")
            transform = transforms.Compose([
                transforms.Resize(112),
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5], inplace=True)
            ])
            input_img = transform(input_img).unsqueeze(0)
            images.append(input_img)
                
        images = torch.cat(images, dim=0)

        x_vec = mtlface.encode((images))
        results = dot(x_vec[0], x_vec[1]) / (norm(x_vec[0]) * norm(x_vec[1]))

        return results

    # Log File Module
    def log_reg(self, log_hist="",  passport_no=""):
        name_tuple = time.localtime()
        localDatetime = time.strftime("%m-%d-%Y, %H:%M:%S", name_tuple)
        
        local = []
        local.append(localDatetime)
        pn = passport_no
        local.append(pn)
        local.append(log_hist)
        
        log_file_path = 'log/immigrationLogs.csv'
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w+") as f:
                pass
            f.close()

        columns = ['Datetime', 'Passport #', 'Log History']
        df_log = pd.read_csv(log_file_path, names=columns, header=0)

        local[0] = localDatetime
        local[1] = pn
        local[2] = log_hist
        dataframe = []
        dataframe.append(local)
        dataframe = pd.DataFrame(dataframe, columns=columns)
        df_log = pd.concat([df_log, dataframe])

        df_log.to_csv(log_file_path, index=False, columns=columns, header=True)

    # Report Generation Module
    def report_write(self):
        try:
            conn = sqlite3.connect('Database/immigration_DB.db')
            cur = conn.cursor()

            name_tuple = time.localtime()
            self.report['date'] = time.strftime("%m-%d-%Y", name_tuple)
            self.report['time'] = time.strftime("%H:%M:%S", name_tuple)
            cur.execute("""INSERT INTO Report (passport_num, 
                            name,
                            gender,
                            country, 
                            pn_manual, 
                            passport_face_detected, 
                            passport_verified, 
                            passport_similarity, 
                            passport_verification_time, 
                            person_face_detected,                                                                                                 
                            person_similarity, 
                            person_verified, 
                            person_varification_time, 
                            total_time, 
                            date, 
                            time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (self.report['passport_num'], self.report['name'], self.report['gender'],
                                                                            self.report['country'], self.report['pn_manual'], 
                                                                            self.report['passport_face_detected'], self.report['passport_verified'],
                                                                            self.report['passport_similarity'],
                                                                            self.report["passport_verification_time"], self.report['person_face_detected'],
                                                                            self.report['person_similarity'], self.report["person_verified"],
                                                                            self.report['person_varification_time'], self.report["total_time"], 
                                                                            self.report['date'], self.report['time']))
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("Failure with database or entering in data")
            print("Erro: "+ str(e))
            sys.exit(503)

    # Generating and viewing report
    def report_gen(self):
        def dlg_show(message="", icon=QMessageBox.Icon.Information, on_console=""):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Report Generation")
            pixmapi = QStyle.StandardPixmap.SP_TitleBarMenuButton
            win_icon = self.style().standardIcon(pixmapi)
            dlg.setWindowIcon(win_icon)
            dlg.setText(message)
            dlg.setIcon(icon)
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print(on_console)
            
        cwd = os.getcwd()           
        try:
            name_tuple = time.localtime()
            root_folder = "Report"
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)
            date = time.strftime("%m-%d-%Y_%H.%M.%S", name_tuple)
            pdf_filename = "report_{}.pdf".format(date)
            folder = root_folder + "/Report_{}".format(date)
            if not os.path.exists(folder):
                os.mkdir(folder)
            generate_report(filename=folder+'/'+pdf_filename)

            conn = sqlite3.connect('Database/immigration_DB.db')
            columns = ["passport_num", 
                            "name",
                            "gender",
                            "country", 
                            "pn_manual",
                            "passport_face_detected", 
                            "passport_verified", 
                            "passport_similarity", 
                            "passport_verification_time", 
                            "person_face_detected", 
                            "person_similarity", 
                            "person_verified", 
                            "person_varification_time", 
                            "total_time", 
                            "date", 
                            "time"]
            

            csv_filename = "report_{}.csv".format(date)
            sql_table = pd.read_sql_query("SELECT * FROM 'Report'", con=conn)
            df = pd.DataFrame(sql_table, columns=columns)
            df.to_csv(folder+'/'+csv_filename, index=False)

            pixmapi = QStyle.StandardPixmap.SP_MessageBoxInformation
            icon = self.style().standardIcon(pixmapi)
            message = "Report generated Successfully.\n\nFor more details, visit: \"{}\"".format(os.path.join(cwd, folder))
            dlg_show(message=message, icon=QMessageBox.Icon.Information, on_console="Report Generated Successfully!")
            webbrowser.open_new(os.path.join(cwd, folder+'/'+pdf_filename))

        except Exception as e:
            print("Error: {}".format(e))
            message = "Report Generation failed.\n\nError: {}".format(e)
            pixmapi = QStyle.StandardPixmap.SP_MessageBoxInformation
            icon = self.style().standardIcon(pixmapi)
            dlg_show(message=message, icon=QMessageBox.Icon.Critical, on_console="Report Generated Failed!")


# Driver Code
if __name__ == "__main__":
    try:
        conn = sqlite3.connect('Database/immigration_DB.db')
        cur = conn.cursor()
    except Exception as e:
        print("Database connection failed")
        print("Error: {}".format(e))
        sys.exit(503)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Modules(MainWindow=MainWindow)
    MainWindow.show()
    
    try:
        mtlface = torch.load('Resources/model/Smart_One.pth', map_location=torch.device('cpu'))
        face_cascade = cv2.CascadeClassifier('Resources/detectors/haarcascade_frontalface_default.xml')
        face_detector = dlib.get_frontal_face_detector()
        landmark_detector = dlib.shape_predictor("Resources/detectors/shape_predictor_68_face_landmarks.dat")
    except Exception as e:
        print("Problem in loading Model(s)! Kindly check if the model is present in the path \"/Resources/model/\""
                +"\nOr there Might be a problem while loading the model...")
        print("Error: {}".format(e))
        sys.exit(404)

    app.exec()
        