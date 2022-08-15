
#!/usr/bin/python
import smbus
import math
import time
from tkinter import *
from PIL import Image, ImageTk
import os

import sys
import time
import datetime
import RPi.GPIO as GPIO
import tm1637 #4-Digit LED Display

from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

#####MPU-6050 Accelerometer Pin#####
#VCC 3.3V power -> (Pin 1)
#SDA -> GPIO2 -> (Pin 3)
#SCL -> GPIO3 -> (Pin 5)
#MPU 6050 -> Ground (Pin 6)

###LED PIN###
#LED -> GPIO18 (Pin 12)
#LED Ground -> Gound (Pin 39)

###4-Digit Display Pin###
#CLK -> GPIO23 (Pin 16)
#Di0 -> GPIO24 (Pin 18)
#VCC -> 5V Power (Pin 4)
#GND -> Ground (Pin 14)

# 4-Digit Display Initialisation

Display = tm1637.TM1637(23,24,tm1637.BRIGHT_TYPICAL)
Display.Clear()
Display.SetBrightnes(1)

# Hi-Score for Current game
hiscore = 0

# Graphic User Interface of the project
class GUI:
    
    ## Initialisation
    def __init__(self):
        
        #Score and Record
        self.score = 0
        self.record = []
        
        #Window setup and initialisation
        window = Tk()
        window.title("Kool Knockout")
        window.geometry("1280x960")
        window.configure(background = 'red')

        #GPIO setup for LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        
        ###################
        #ON SCREEN DISPLAY#
        ###################
        
        #Title
        self.title = Label(window, text = "Kool Knockout", height = 2, width = 80, background = 'red')
        self.title.config(font = ('Arial', 90, 'bold'))
        
        #Score display
        self.lbl = Label(window, text = "Score: ", height = 2, width = 80, background = 'gold')
        self.lbl.config(font = ('helvetica', 60, 'bold'))
        
        #HiScore display
        self.hscore = Label(window, text = "Hi-Score: ", height = 2, width = 160, background = 'gold')
        self.hscore.config(font = ('helvetica', 30, 'bold'))
        
        #Name input
        self.namelbl = Label(window, text = "Your Name:", height = 1, width = 200, background = 'white')
        self.namelbl.config(font = ('Times New Roman', 20, 'bold'))
        
        #Start Button
        self.startbutton = Button(window, text = "Press Here to Start",command = self.start, height = 2, width = 80, background = 'coral')
        self.startbutton.config(font = ('Comic Sans MS', 40))
        
        #Show the Record Button
        self.showRecordButton = Button(window, text = "Records", command = self.showRecord, height = 2, width = 300, background = 'sandy brown')
        self.showRecordButton.config(font = ('helvetica', 25))
        
        #Save the database Button
        self.savebutton = Button(window, text = "Save" , command = self.save, height = 2, width = 40, background = 'pink')
        self.savebutton.config(font = ('helvetica', 20))
        
        #Load the database Button
        self.loadbutton = Button(window, text = "Load" , command = self.load, height = 2 , width = 40, background = 'mistyrose')
        self.loadbutton.config(font = ('helvetica', 20))
        
        #Value
        self.value = StringVar()
        
        #Enter Name box
        self.nameentry = Entry(window, font = "Calibri 30 bold", justify="center", textvariable = self.value, width = 200)
        
        #Pack the data onto the display in order
        self.title.pack() #Title
        self.lbl.pack() #Score
        self.hscore.pack() #HiScore
        self.namelbl.pack() #NameLabel
        self.nameentry.pack() # NameBox
        self.startbutton.pack() # Start Button
        self.showRecordButton.pack() #Show Record Button
        self.savebutton.pack(side = LEFT) # Save Button
        self.loadbutton.pack(side = RIGHT) # Load Button
        
        #MainLoop
        window.mainloop()
        
    ##################################
    ###WHEN START BUTTON IS PRESSED###
    ##################################
    def start(self):
        
        #Read x, y, z axis from accelerometer GPU 6050
        xout = read_word_2c(0x3b)
        yout = read_word_2c(0x3d)
        zout = read_word_2c(0x3f)
        
        #Set 3 second input receival time
        now = time.time()
        future = now + 3
        
        
        #Initialise the current value and display to be prepare for other input
        maxacc = 0
        xout2 = xout
        yout2 = yout
        zout2 = zout
        
        #During the 3 second period
        #Collection of Data
        while (time.time() < future):
            
            #Turn on the LED Light
            GPIO.output(18,1)
            
            #Record Acceleration
            acc = ((xout2-xout)**2 + (yout2-yout)**2 + (zout2-zout)**2)**0.5
            
            #If current acceration is higher than the highest, then replace
            if(maxacc < acc):
                maxacc = acc
            
            #Read Value and Repeat until time passed
            xout2 = xout
            yout2 = yout
            zout2 = zout
            xout = read_word_2c(0x3b)
            yout = read_word_2c(0x3d)
            zout = read_word_2c(0x3f)
            pass

        while True:
            if time.time() > future:
                break
            
        #####################################
        #####3 Seconds input time passed#####
        #####################################
            
        #Turn off LED light
        GPIO.output(18,0)
        
        #Display result and change to INT for display
        print("Max acceleration is: ", ("%6d" % maxacc))
        print("Your Score is: ", ("%6d" % maxacc))
        maxacc = int(maxacc)
        
        #Update score and highscore on the menu
        self.update(maxacc)
        self.hiscoreupdate(maxacc)
        
        #To show that number is increasing on 4-digit display
        incr = maxacc // 250  # Speed
        if incr == 0:
            incr = 1
            
        # Dislay the number on 4-digit Display increasing
        for i in range(0,maxacc,incr):
        
            # [ 1st digit(Thousands), 2nd digit(Hundreds), 3rd digit(Tenths), 4th digit(Ones)]
            currenttime = [int((i / 100000) % 10), int((i / 10000) % 10), int((i / 1000) % 10), int((i / 100) % 10)]
            
            #Display on 4-digit Display
            Display.Show(currenttime)
            
        #When number is reached and show then append onto array
        currenttime = [int((maxacc / 100000) % 10), int((maxacc / 10000) % 10), int((maxacc / 1000) % 10), int((maxacc / 100) % 10)]

        Display.Show(currenttime)
        self.record.append([self.value.get(), maxacc//100])

    #############################
    ###UPDATE SCORE ON DISPLAY###
    #############################
    def update(self,score):
        self.lbl["text"] = "Score: " + str(int(score/100))
    
    ###############################
    ##UPDATE HI-SCORE ON DISPLAY###
    ###############################
    def hiscoreupdate(self,score):
        global hiscore
        hhhiscore = hiscore
        if(score > hhhiscore): #Higher then replaced
            hhhiscore = score
            hiscore = hhhiscore
            self.hscore["text"] = "Hi-Score: " + str(int(hhhiscore/100))
        
    ########################
    ######SAVE COMMAND######
    ########################
    def save(self):
        filenameforWriting = asksaveasfilename()
        if(filenameforWriting):
            outfile = open(filenameforWriting,"w")
            for i in self.record:
                outfile.write(str(i[0]) + "," + str(i[1]))
            outfile.close()

    ########################
    ######LOAD COMMAND######
    ########################
    def load(self):
        filenameforWriting = askopenfilename()
        if (filenameforWriting):
            infile = open(filenameforWriting , "r")
            line = infile.readline()
            self.record = []
            while line != "":
                print(line)
                
                self.record.append([line[:line.index(",")] , line[line.index(",") + 1 ::]])
                
                
                line = infile.readline()
            infile.close()
    
    #Show record
    def showRecord(self):
        ShowRecord(self.record)
            
        
########################
#####Record display#####
########################
class ShowRecord:
    def __init__(self,record):
        self.window = Tk()
        self.ListscrollBar = RecordScrollbar(self.window,record)
        self.record = record
        
        for i in record:
            Label(self.ListscrollBar.frame2, text = str(i[0] + " , " + i[1])).pack()
            
        self.ListscrollBar.frame1.grid()
        self.window.mainloop
        
##########################
#####Record scrollbar#####
##########################
class RecordScrollbar:
    def __init__(self,window,record):
        self.window = window
        self.frame1 = Frame(self.window, relief = RAISED)
        self.canvas = Canvas(self.frame1, bg = "alice blue")
        self.frame2 = Frame(self.canvas)
        self.scrollbar = Scrollbar(self.frame1, orient = "vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        self.scrollbar.pack(side = "right", fill = "y")
        self.canvas.pack(side = "left")
        self.canvas.create_window((0,0), window = self.frame2, anchor = "nw")
        self.frame2.bind("<Configure>", lambda x : self.scrollFunction(x))
        self.record = record
        
    def scrollFunction(self,event):
        maxlength = 30
        self.canvas.configure(scrollregion = self.canvas.bbox("all"), width = maxlength * 15 , height = 300)
    
    
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68       # via i2cdetect

# Activate model
bus.write_byte_data(address, power_mgmt_1, 0)

###Record data on Accelerometer
#Byte
def read_byte(reg):
    return bus.read_byte_data(address, reg)

#Word
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
 #Word 2c
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
 
def dist(a,b):
    return math.sqrt((a*a)+(b*b))
 
def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)
 
def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
###############
####RUN GUI####
###############
GUI()




