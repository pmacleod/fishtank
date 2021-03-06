USE_FIRMATA = True
USE_NANPY = False

from bottle import route, run, template, redirect, request, post, static_file
import math
import sys
from apscheduler.scheduler import Scheduler
if USE_FIRMATA:
    import pyfirmata
    board = pyfirmata.ArduinoMega("/dev/ttyACM0")
elif USE_NANPY:
    from nanpy import Arduino
    from nanpy.arduinotree import ArduinoTree

import datetime
import nanpy
import sys
import time
from time import sleep
import logging;logging.basicConfig()
logging.basicConfig(level=logging.INFO,format='%(asctime)s : %(name)s : %(levelname)s : %(module)s.%(funcName)s(%(lineno)d) : %(thread)d %(threadName)s: %(message)s')

##PWM TIMER SHIT
#sets all pins to 120hz
def set_timer(timer, prescale):
    a= ArduinoTree()
    mask = 7
    register = a.register.get("TCCR" + str(timer) + "B")
    register.value = (register.value & ~mask) | prescale
 
def set_timers():
    prescale = 4
    set_timer(2, prescale)
    set_timer(3, prescale)
    set_timer(4, prescale)
    set_timer(5, prescale)

##
##Pin assignments!    
if USE_FIRMATA:
    boardPin = board.get_pin("d:13:p")
    pwmPin1 = board.get_pin("d:2:p")
    pwmPin2 = board.get_pin("d:3:p")
    pwmPin3 = board.get_pin("d:4:p")
    pwmPin4 = board.get_pin("d:5:p")
    pwmPin5 = board.get_pin("d:6:p")
    pwmPin6 = board.get_pin("d:7:p")
    pwmPin7 = board.get_pin("d:8:p")
    pwmPin8 = board.get_pin("d:9:p")
else:
    boardPin = 13
    pwmPin1 = 2
    pwmPin2 = 3
    pwmPin3 = 4
    pwmPin4 = 5
    pwmPin5 = 6
    pwmPin6 = 7
    pwmPin7 = 8
    pwmPin8 = 9

if USE_NANPY:
    Arduino.pinMode(boardPin, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin1, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin2, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin3, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin4, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin5, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin6, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin7, Arduino.OUTPUT)
    Arduino.pinMode(pwmPin8, Arduino.OUTPUT)
    # my version of firmata sets the pwm in the firmware
    set_timers()

targetpin = boardPin
PWM_Levelout = 0
outpin = 0
writeVAR = 0
 
 
def arduinoPinwriteout(outpin, PWM_Levelout):
    global targetpin
    targetpin = outpin
    global writeVAR
    writeVAR = PWM_Levelout
    if outpin == boardPin:
        print writeVAR
    if USE_FIRMATA:
        outpin.write(writeVAR / 255.0)
    elif USE_NANPY:
        Arduino.analogWrite(targetpin, writeVAR)

PWM_min = 100
PWM_max = 255
PWM_level = 255
 
dim_Ontimesecs = 900
dim_Cyclesecs = dim_Ontimesecs/PWM_max
dim_Uptimehr = 8
dim_Downtimehr= 23
#print 'cycle runs 15 minutes either way. Set the two 15 min apart to avoid clipping'
 
 
##only run this when hdmi is connected
#dim_UptimehrOverride = input('Start time (hr)')
#dim_UptimeminOverride = input('Start time (min)')
#dim_DowntimehrOverride = input('End time (hr)')
#dim_DowntimeminOverride = input('End time (min)')
##
 
 
modding = 0

def timestatuscheck():
    return
    global PWM_level
    if modding == 0:
        now = time.localtime()
        if (now.tm_hour < dim_Uptimehr):
            PWM_level = PWM_max
        elif (now.tm_hour >= dim_Uptimehr) and (now.tm_hour <= dim_Downtimehr):
            PWM_level = PWM_min
        elif (now.tm_hour > dim_Downtimehr):
            PWM_level = PWM_max
       
 
def signalmod_PWM(modAmount):
    global PWM_level
    global modding
    if modAmount != 0:
        modding = 1
    else:
        modding = 0
    print "modding %d modAmount %d PWM_level %d pwm_min %d pwm_max %d:" % (modding, modAmount, PWM_level, PWM_min, PWM_max)
    global modTester
    modTester = math.copysign(1, modAmount)
    if modTester == -1:
        if PWM_level <= PWM_min:
            PWM_level = PWM_min
        elif PWM_level > PWM_min:
            PWM_level += (modAmount)
    elif modTester == 1:
        if PWM_level >= PWM_max:
            PWM_level = PWM_max
        elif PWM_level <= PWM_max:
            PWM_level += (modAmount)

sched = Scheduler()
 
sched.add_interval_job(timestatuscheck, seconds = 1)
 
 
sched.add_interval_job(lambda: arduinoPinwriteout(boardPin, PWM_level), seconds = 1)
 
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin1, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin2, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin3, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin4, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin5, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin6, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin7, PWM_level), seconds = 1)
sched.add_interval_job(lambda: arduinoPinwriteout(pwmPin8, PWM_level), seconds = 1)
 
 
 
def testdimCycleUp():
    sched.add_interval_job(lambda: signalmod_PWM(-1), seconds=dim_Cyclesecs, max_runs=(PWM_max-PWM_min) + 1)
   
def testdimCycleDown():
    sched.add_interval_job(lambda: signalmod_PWM(1), seconds=dim_Cyclesecs, max_runs=(PWM_max-PWM_min) + 1)
 
 
sched.add_cron_job(testdimCycleUp,  hour=dim_Uptimehr)
 
sched.add_cron_job(testdimCycleDown,  hour=dim_Downtimehr)
sched.start()
sched.print_jobs()

@route("/")
def default():
    return template("main_template", current_level=PWM_level, modding=modding, dim_time=dim_Ontimesecs)

@route("/turn_on")
def turn_on():
    global PWM_level
    PWM_level = PWM_min
    redirect("/")

@route("/turn_off")
def turn_off():
    global PWM_level
    PWM_level = PWM_max
    redirect("/")

@route("/dim_on")
def dim_on():
    if PWM_level == PWM_max:
        testdimCycleUp()
    redirect("/")

@route("/dim_off")
def dim_off():
    if PWM_level == PWM_min:
        testdimCycleDown()
    redirect("/")

@post("/set_dim")
def set_dim():
    global dim_Ontimesecs, dim_Cyclesecs
    print request.forms.get("dim_time")
    dim_Ontimesecs = int(request.forms.get("dim_time"))
    dim_Cyclesecs = float(dim_Ontimesecs)/(PWM_max - PWM_min)
    redirect("/")

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

run(host="0.0.0.0", port=6767, debug=True)
