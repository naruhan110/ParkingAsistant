
# Import required Libraries
from __future__ import print_function, division, absolute_import
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
from PIL import Image, ImageTk
import cv2
import threading
import time
import requests
import base64
import csv

REST_API_URL_VIDEO = "http://localhost:5000/predict_video"
#REST_API_URL_VIDEO_2 = "http://localhost:5000/predict_video_2"
REST_API_URL_VIDEO_qr = "http://localhost:5000/qrscan"

def search_plate(file_path, plate):
   key = False
   data = ''
   with open(file_path, 'r') as f:
      reader = csv.reader(f)
      for row in reader:
         if plate == row[1]:
            key = True
            data = row
            break
   return key, data

def delete_row(file_path, plate):
   lines=list()
   with open(file_path, 'r') as f:
      reader = csv.reader(f)
      for row in reader:
         if plate != row[1]:
            lines.append(row)
      f.close()
   if len(lines):
      with open(file_path, 'w', newline="") as wf:
         writer = csv.writer(wf)
         writer.writerows(lines)
   print("deleted 1 line ")

def save_data(file_path, data):
   with open(file_path, 'a', newline="") as wf:
      writer = csv.writer(wf)
      writer.writerow(data)
   print("data has been inserted!")
"""def soft_string(str=''):
   str.replace('"', '', -1)
   str.replace('[', '', -1)
   str.replace(']', '', -1)
   return str"""

def send_data(frame_in, frame_out, frame_qr):
   global t_qr, plate_in, plate_out, data_path, parking_path, time_come, time_left
   try:
      if (plate_in!='[""]') or (plate_out!='[""]'):
         _, img_encoded_qr = cv2.imencode('.png', frame_qr)
         jpg_as_text_qr = base64.b64encode(img_encoded_qr)
         jpg_original_qr = base64.b64decode(jpg_as_text_qr)

         r_qr = requests.post(REST_API_URL_VIDEO_qr, data=jpg_original_qr)
         t_qr = r_qr.text
         if t_qr!='""':
            if plate_in!='[""]':
               time_come = time.ctime(time.time())
               data = [t_qr, plate_in, time_come]
               save_data(parking_path, data)
               plate_in = '[""]'
            else:
               time_left = time.ctime(time.time())
               print("qr: ", t_qr)
               ret, data = search_plate(parking_path, plate_out)
               if (ret==True) and (data[0]==t_qr):
                  data1 = [data[0], data[1], data[2], time_left]
                  save_data(data_path, data1)
                  delete_row(parking_path, plate_out)
               plate_out = '[""]'
            t_qr = '""'

      else:
         _, img_encoded = cv2.imencode('.jpg', frame_in)
         jpg_as_text = base64.b64encode(img_encoded)
         jpg_original = base64.b64decode(jpg_as_text)
         r = requests.post(REST_API_URL_VIDEO, data=jpg_original)
         t = r.text
         plate_in = t

         _, img_encoded = cv2.imencode('.jpg', frame_out)
         jpg_as_text = base64.b64encode(img_encoded)
         jpg_original = base64.b64decode(jpg_as_text)
         r = requests.post(REST_API_URL_VIDEO, data=jpg_original)
         t_2 = r.text
         plate_out = t_2

         print("bien so: ")
      #print("t: ", time.time() - t1)
      # sleep(3)
   except:
      print("loi")
# Define function to show frame
def show_frames():
   global count
   #t1 = time.time()
   # Get the latest frame and convert into Image
   cv2image_in = cv2.cvtColor(cap_in.read()[1], cv2.COLOR_BGR2RGB)
   img = Image.fromarray(cv2image_in)
   # Convert image to PhotoImage
   imgtk = ImageTk.PhotoImage(image = img)
   label.imgtk = imgtk
   label.configure(image=imgtk)

   # Get the latest frame and convert into Image
   cv2image_in = cv2.cvtColor(cap_in.read()[1], cv2.COLOR_BGR2RGB)
   img = Image.fromarray(cv2image_in)
   # Convert image to PhotoImage
   imgtk = ImageTk.PhotoImage(image=img)
   label2.imgtk = imgtk
   label2.configure(image=imgtk)

   frame_qr = cv2.cvtColor(cap_qr.read()[1], cv2.COLOR_BGR2RGB)

   if count>20:
      count=0
      #insert api here
      test = cv2.imread('test/test.jpg')
      thread = threading.Thread(target=send_data, args=(cv2image_in, test, cv2image_in))
      thread.start()
   else:
      count+=1

   var1 = StringVar()
   var1.set((plate_in))
   var2 = StringVar()
   var2.set(time_come)
   var3 = StringVar()
   var3.set(plate_out)
   var4 = StringVar()
   var4.set(time_left)

   Label1 = Label(win, text='Biển số xe : ', font=("Arial", 10),background="white").grid(row=1, column=0, sticky=W + N)
   Label1 = Label(win, textvariable=var1, font=("Arial", 10),background="white").grid(row=1, column=0)
   Label1 = Label(win, text='Thời điểm xe vào :', font=("Arial", 10)).grid(row=2, column=0, sticky=W + N)
   Label1 = Label(win, textvariable=var2, font=("Arial", 10)).grid(row=2, column=0)

   Label1 = Label(win, text='Thời điểm xe ra :', font=("Arial", 10)).grid(row=2, column=1, sticky=W + N)
   Label1 = Label(win, textvariable=var4, font=("Arial", 10)).grid(row=2, column=1)
   Label1 = Label(win, text='Biển số xe :', font=("Arial", 10)).grid(row=1, column=1, sticky=W + N)
   Label1 = Label(win, textvariable=var3, font=("Arial", 10)).grid(row=1, column=1)

   # Repeat after an interval to capture continiously
   win.after(60, show_frames)

if __name__=="__main__":
   data_path = 'data.csv'
   parking_path = 'xe_trong_bai.csv'
   win = Tk()
   # Set the size of the window
   # win.geometry("1000x750")
   win.configure(bg='lavender')

   trv = ttk.Treeview(win, columns=(1, 2, 3), show="headings", height="6")
   trv.grid(row=11, column=0)
   trv.heading(1, text="STT")
   trv.heading(2, text="Biển số xe")
   trv.heading(3, text="Thời gian vào")

   # Create a Label to capture the Video frames
   label = Label(win)
   label.grid(row=6, column=0, sticky=W + N)

   label2 = Label(win)
   label2.grid(row=6, column=1, sticky=W + N)

   count = 0

   cap_in = cv2.VideoCapture(1)
   cap_in.set(3, 400)
   cap_in.set(4, 300)

   cap_qr = cv2.VideoCapture(0)

   t_qr = '""'
   plate_in = '[""]'
   plate_out = '[""]'
   time_come = None
   time_left = None
   show_frames()

   #mybutton1 = Button(win, text = 'Doanh thu trong ngày:',font= ("Arial", 10)).grid(row=5,column=0,sticky=W+N)
   Labelb = Label(win, text = 'DANH SÁCH XE HIỆN ĐANG TRONG BÃI ',font= ("Arial", 25)).grid(row=10,column=0,sticky=W)
   Labell = Label(win, text = 'TÌM KIẾM XE TRONG BÃI NGÀY HÔM NAY ',font= ("Arial", 25)).grid(row=12,column=0,sticky=W)

   Labelll = Label(win,text = 'Nhập số xe',font= ("Arial", 10)).grid(row = 13,column = 0,sticky=W)
   e1=Entry(win, textvariable='Nhap bien so xe')
   e1.grid(row=13, column=0)
   bienso = ""
   Btn = Button(win, text='Tìm kiếm')
   Btn.grid(row=13, column=1, sticky=W)

   win.mainloop()
