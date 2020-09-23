from time import sleep
import random
import imager2 as IMR
from reflectance_sensors import ReflectanceSensors
from camera import Camera
from motors import Motors
from ultrasonic import Ultrasonic
from zumo_button import ZumoButton
from irproximity_sensor import IRProximitySensor
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import ImageStat
from PIL import ImageDraw
from PIL import ImageOps
import os

## Passord: Tokstad34

##Skifte endel fra å gjøre ting i behavior til å gjøre ting i arbitrator, velge ting her

#******** BBCON class **********
class BBCON():

    def __init__(self,behaviors, active_behaviors, sensobs, motobs, arbitrator):
        self.behaviors = behaviors
        self.active_behaviors = active_behaviors
        self.sensobs = sensobs
        self.motobs = motobs
        self.arbitrator = arbitrator

    def add_Behavior(self, behavior):
        self.behaviors.append(behavior)

    def add_sensob(self, sensob):
        self.sensobs.append(sensob)
    
    def remove_sensob(self, sensob):
      	self.sensobs.remove(sensob)

    def activate_behavior(self, behavior):
        if len(self.active_behaviors) < 3:
            if behavior in self.behaviors:
                self.active_behaviors.append(behavior)
                print(behavior, "activating behavior")
    
    def deactivate_behavior(self, behavior):
        if behavior in self.active_behaviors:
            self.active_behaviors.remove(behavior)
            print(behavior, "Deactivating behavior")
    
    def run_one_timestep(self):
        for i in self.behaviors:
            i.updateBehaviors()
            if i.active_flag == False and i in self.active_behaviors:
                    self.deactivate_behavior(i)
            if i.active_flag == True and i not in self.active_behaviors:
                    self.activate_behavior(i)
        action, halted = self.arbitrator.choose_action(self.active_behaviors) # Motor rec.
        if halted == True:
            print("Backing up!")
            self.motobs.updateMotobRecommendation("Back")
            self.motobs.updateMotobSetting()
        else:
            mr = action.motor_recommendation[0]
            self.motobs.updateMotobRecommendation(mr)
            self.motobs.updateMotobSetting()


#******** Sensob class ***********@
class sensob(Ultrasonic, ReflectanceSensors, Camera, IRProximitySensor):

    sensors = list()
    sensor_value = dict()

    def __init__(self, sensors, sensortype):
        self.sensors = sensors
        self.sensortype = sensortype

    def updateSensob(self):
        if self.sensortype == 3: #Camera
            for i in self.sensors:
                i.update()
            distance = self.sensors[0].get_value()
            picture = self.sensors[1].get_value()
            self.sensor_value = {'distance': distance, 'picture': picture}
        elif self.sensortype == 2: #Distance
            self.sensors[0].update()
            distance = self.sensors[0].get_value()
            self.sensor_value = {'distance': distance}
        else:
            self.sensors[0].update() #Side
            Right, Left = self.sensors[0].get_value()
            self.sensor_value = {'Right': Right, 'Left': Left}
        
                
    def getSensobValue(self):
        self.updateSensob()
        return self.sensor_value
    
    def resetSensob(self):
        for i in self.sensors:
            i.reset()
            self.sensor_value = None

# ******* Motob class **********@@         
class Imotob():
    MR = "Straight" #Motor recommendation
    MS = "Straight" #Motor setting
    #M = Motors()
    duration = 0.5
    turn_duration = 0.5
    swing_duration = 0.5
    speed_forward = .5
    turn_speed = .5
    swing_speed = .5
    def __init__(self, MR, MS, M):
        self.MR = MR
        self.MS = MS
        self.M = M

    def updateMotobRecommendation(self, MR):
        #n = 0
        #if n != 1:
        #    self.M.forward(speed=.5, dur=1)
        #    self.M.set_value([1, .1], 1)
        #    n = 1
        self.MR = MR
    
    def updateMotobSetting(self):
        if self.MR == "Right":
            self.MS = "Right"
        elif self.MR == "Left":
            self.MS = "Left"
        elif self.MR == "Forward":
            self.MS = "Forward"
        elif self.MR == "Back":
            self.MS = "Back"
        elif self.MR == "Turn_Right":
            self.MS = "Turn_Right"
        elif self.MR == "Turn_Left":
            self.MS = "Turn_Left"
        print (self.MS, "Motor Setting")
        self.updateMotor()

    def updateMotor(self):
        print("Running motors!")
        if self.MS == "Right":
            self.M.right(speed=self.swing_speed, dur=self.swing_duration)
        elif self.MS == "Left":
            self.M.left(speed=self.swing_speed, dur=self.swing_duration)
        elif self.MS == "Forward":
            self.M.forward(speed=self.speed_forward, dur=self.duration)
        elif self.MS == "Back":
            self.M.backward(speed=self.speed_forward, dur=.3)
        elif self.MS == "Turn_Right":
            print("Right")
            self.M.set_value([self.swing_speed, -self.swing_speed], self.turn_duration)
        elif self.MS == "Turn_Left":
            print("Left")
            self.M.set_value([-self.swing_speed, self.swing_speed], self.turn_duration)
        else:
            print("Exception!!!!")
            self.M.stop()

#********* Behavior class ************  
class Behavior():
  
    def __init__(self, sensobs, priority):
        self.sensobs = sensobs
        self.motor_recommendation = list()
        self.motor_recommendation.append("Forward")

        self.active_flag = True
        if priority == 3:
            self.active_flag = False
        self.halt_request = False
        self.priority = priority
        self.match_degree = 1
        self.weight = self.priority * self.match_degree
        #self.weights = [0, 0, 0]

    def haltRequest(self):
        if self.priority == 2: #Distansebehavior front
            distance = self.sensobs.getSensobValue()
            if distance['distance'] <= 4:
                self.halt_request = True
            else:
                self.halt_request = False
        if self.priority == 3: #Camera
            distance_camera = self.sensobs.getSensobValue() #Camera behavior, distance sensor
            if distance_camera['distance'] <= 4:
                self.halt_request = True
            else:
                self.halt_request = False
        

    def consider_deactivation(self):
        if self.priority == 3: #Camera Behaviour
            self.sensobs.sensors[0].update() #distancesensor
            distance_camera = self.sensobs.getSensobValue() #gets dict values
            if distance_camera['distance'] > 10: #dictkey distance 
                self.active_flag = False
                self.match_degree = 0
            
    def updateWeight(self):
        if self.priority == 1: #Sidebehavior
            Sides = self.sensobs.getSensobValue()
            if (Sides['Right'] == True or Sides['Left'] == True):
                self.match_degree = 2
                self.weight = self.priority * self.match_degree
                print (self.weight, "side weight")
            else:
                self.match_degree = 0
                self.weight = self.priority * self.match_degree
                print (self.weight, "side weight")
        if self.priority == 2: #distancebehavior
            distance = self.sensobs.getSensobValue()
            if (distance['distance'] < 6):
                self.match_degree = 1
                self.weight = self.priority * self.match_degree
                print (self.weight, "Distance weight")
            if (distance['distance'] <= 4):
                self.match_degree = 2
                self.weight = self.priority * self.match_degree
            else:
                self.match_degree = 0
                self.weight = self.priority * self.match_degree
                print (self.weight, "Distance weight")
        if self.priority == 3: #camerabehavior
            distance_camera = self.sensobs.getSensobValue()
            if distance_camera['distance'] < 10:
                self.match_degree = 1
                self.weight = self.priority * self.match_degree
                print (self.weight, "Camera distance weight")
            else:
                self.match_degree = 0
                self.weight = self.priority * self.match_degree
                print (self.weight, "Camera distance weight")

    def consider_activation(self):
        if self.priority == 3: #Camera behaviour
            self.sensobs.sensors[0].update() #Camerasensob, distance sensor update
            distance_camera = self.sensobs.getSensobValue()
            if distance_camera['distance'] < 10:
                self.active_flag = True
                self.match_degree = 1

    def sense_and_act(self):
        if self.priority == 1: #Avstandsbehavior side
            Sides = self.sensobs.getSensobValue()
            if Sides['Right'] == False and Sides['Left'] == False:
                self.motor_recommendation[0] = "Forward"
                print("Whyyy fail sense and act sides")
            elif Sides['Right'] == True:
                self.motor_recommendation[0] = "Right"
            else:
                self.motor_recommendation[0] = "Left"
        if self.priority == 2: #Distansebehavior front
              distance = self.sensobs.getSensobValue()
              if distance['distance'] < 4:
                  self.motor_recommendation[0]= "Back"
              else:
                   self.motor_recommendation[0] = "Forward"
        if self.priority == 3: #Camerabehavior
            distance_camera = self.sensobs.getSensobValue() #Updates and gets sensobvalue
            if distance_camera['distance'] <= 10:
                self.sensobs.updateSensob()
                pic = Imager(fname="image", dir="/home/robot/", ext="png") #Legger bilde i imager
                wtapic = pic.map_color_wta() #Winner takes all
                #wtapic.dump_image("wta", dir="/home/robot/", ext="png") #saver bilde til robot
                scaledpic = wtapic.scale_colors(image=False, degree=100) #scaler bilde for å øke fargeverdiene
                #scaledpic.dump_image("scaled", dir="/home/robot/", ext="png")
                pixel = scaledpic.get_pixel(80,50) #henter pixel ca midt fra bilde 
                print(pixel)
                color = wtapic.get_color_rgb(pixel) #finner ut hvilken farge denne har utifra pixel rgb verdien
                print (color)
                if color == 'green':
                    self.motor_recommendation[0] = "Turn_Left"
                elif color == 'red':
                    self.motor_recommendation[0] = "Turn_Right"
                elif color == 'blue':
                    self.motor_recommendation[0] = "Stop"
                else:
                    self.motor_recommendation[0] = "Forward"
            else:
                self.motor_recommendation[0] = "Forward"

    def updateBehaviors(self):
        self.consider_deactivation()
        self.consider_activation()
      
    def update(self):
        self.sense_and_act()

#********* Arbitrator class ************
class Arbitrator(Behavior):
  weights = [0, 0, 0]
  priority = None

  def __init__(self, behaviors):
        self.behaviors = behaviors

  def choose_action(self, behaviors):
    action_behavior = None
    self.behaviors = behaviors
    for b in self.behaviors: #Oppdaterer vektingen til alle behaviors
        b.updateWeight() 
        self.weights[b.priority - 1] = b.weight
        if len(self.behaviors) < 3:
            self.weights[2] = 0
    maxchoice = max(self.weights)
    choice = self.weights.index(maxchoice)
    if maxchoice == 0: #hvis vekting lik for alle behaviors
        self.priority = 2 
        for b in self.behaviors:
            b.haltRequest()
            halt = b.halt_request
            if halt == True:
                halted = True
            else:
                halted = False
            if b.priority == 2:
                action_behavior = b #Alltid velg distance om vekting er lik
    else: #Hvis vekting ulik
        for b in self.behaviors:
            b.haltRequest()
            halt = b.halt_request
            if halt == True:
                halted = True
            else:
                halted = False
            if b.priority == choice + 1:
                self.priority = b.priority
                print(choice + 1, "choice", b.priority, "Behavior priority", self.priority, "Actual priority set")
                action_behavior = b
    if action_behavior == None:
        action_behavior = self.behaviors[1]        
    action_behavior.update()
    if halted == True:
        action_behavior.motor_recommendation[0] = "Back"
    print(self.weights, "weights")
    print(action_behavior.priority, "Priority value")
    return (action_behavior,halted)


class Imager():
    _pixel_colors_ = {(255, 0, 0):'red' , (0, 255, 0): 'green', (0, 0, 255):'blue' , 'white': (255, 255, 255),
                      'black': (0, 0, 0)}
    _image_dir_ = "images/"
    _image_ext_ = "jpeg"

    def __init__(self, fname=False, dir=None, ext=None, image=False, width=100, height=100, background='black',
                 mode='RGB'):
        self.init_file_info(fname, dir, ext)
        self.image = image  # A PIL image object
        self.xmax = width;
        self.ymax = height  # These can change if there's an input image or file
        self.mode = mode
        self.init_image(background=background)

    def init_file_info(self, fname=None, dir=None, ext=None):
        self.dir = dir if dir else self._image_dir_
        self.ext = ext if ext else self._image_ext_
        self.fid = self.gen_fid(fname) if fname else None

    def gen_fid(self, fname, dir=None, ext=None):
        dir = dir if dir else self.dir
        ext = ext if ext else self.ext
        return dir + fname + "." + ext

    def init_image(self, background='black'):
        if self.fid: self.load_image()
        if self.image:
            self.get_image_dims()
        else:
            self.image = self.gen_plain_image(self.xmax, self.ymax, background)

    # Load image from file
    def load_image(self):
        self.image = Image.open(self.fid)  # the image is actually loaded as needed (automatically by PIL)
        if self.image.mode != self.mode:
            self.image = self.image.convert(self.mode)

    # Save image to a file.  Only if fid has no extension is the type argument used.  When writing to a JPEG
    # file, use the extension JPEG, not JPG, which seems to cause some problems.
    def dump_image(self, fname, dir=None, ext=None):
        self.image.save(self.gen_fid(fname, dir=dir, ext=ext))

    def get_image(self):
        return self.image

    def set_image(self, im):
        self.image = im

    def display(self):
        self.image.show()

    def get_image_dims(self):
        self.xmax = self.image.size[0]
        self.ymax = self.image.size[1]

    def copy_image_dims(self, im2):
        im2.xmax = self.xmax;
        im2.ymax = self.ymax

    def gen_plain_image(self, x, y, color, mode=None):
        m = mode if mode else self.mode
        return Image.new(m, (x, y), self.get_color_rgb(color))

    def get_color_rgb(self, colorname):
        return Imager._pixel_colors_[colorname]

    # This returns a resized copy of the image
    def resize(self, new_width, new_height, image=False):
        image = image if image else self.image
        return Imager(image=image.resize((new_width, new_height)))

    def scale(self, xfactor, yfactor):
        return self.resize(round(xfactor * self.xmax), round(yfactor * self.ymax))

    def get_pixel(self, x, y):
        return self.image.getpixel((x, y))

    def set_pixel(self, x, y, rgb):
        self.image.putpixel((x, y), rgb)

    def combine_pixels(self, p1, p2, alpha=0.5):
        return tuple([round(alpha * p1[i] + (1 - alpha) * p2[i]) for i in range(3)])

    # The use of Image.eval applies the func to each BAND, independently, if image pixels are RGB tuples.
    def map_image(self, func, image=False):
        # "Apply func to each pixel of the image, returning a new image"
        image = image if image else self.image
        return Imager(image=Image.eval(image, func))  # Eval creates a new image, so no need for me to do a copy.

    # This applies the function to each RGB TUPLE, returning a new tuple to appear in the new image.  So func
    # must return a 3-tuple if the image has RGB pixels.

    def map_image2(self, func, image=False):
        im2 = image.copy() if image else self.image.copy()
        for i in range(self.xmax):
            for j in range(self.ymax):
                im2.putpixel((i, j), func(im2.getpixel((i, j))))
        return Imager(image=im2)

    # WTA = winner take all: The dominant color becomes the ONLY color in each pixel.  However, the winner must
    # dominate by having at least thresh fraction of the total.
    def map_color_wta(self, image=False, thresh=0.1):
        image = image if image else self.image

        def wta(p):
            s = sum(p);
            w = max(p)
            if s > 0 and w / s >= thresh:
                return tuple([(x if x == w else 0) for x in p])
            else:
                return (0, 0, 0)

        return self.map_image2(wta, image)


    def scale_colors(self, image=False, degree=0.5):
        image = image if image else self.image
        return Imager(image=ImageEnhance.Color(image).enhance(degree))

    def paste(self, im2, x0=0, y0=0):
        self.get_image().paste(im2.get_image(), (x0, y0, x0 + im2.xmax, y0 + im2.ymax))

    def reformat(self, fname, dir=None, ext='jpeg', scalex=1.0, scaley=1.0):
        im = self.scale(scalex, scaley)
        im.dump_image(fname, dir=dir, ext=ext)

        
#********** run_maze class ***************
def main():
    M = Motors()
    sensor1 = IRProximitySensor()
    sensor2 = Ultrasonic()
    sensor3 = Camera()
    
    sensorsCamera = list()
    sensorsCamera.append(sensor2)
    sensorsCamera.append(sensor3)
    sensorsDistance = list()
    sensorsDistance.append(sensor2)
    sensorsSides = list()
    sensorsSides.append(sensor1)
    sensobCamera = sensob(sensorsCamera, 3)
    sensobDistance = sensob(sensorsDistance, 2)
    sensobSides = sensob(sensorsSides, 1)
    
    sensobs = list()
    sensobs.append(sensobCamera)
    sensobs.append(sensobDistance)
    sensobs.append(sensobSides)
    
    behaviors = []
    behavior1 = Behavior(sensobSides, 1) 
    behavior2 = Behavior(sensobDistance , 2)
    behavior3 = Behavior(sensobCamera, 3)
    
    active_behaviors = list()
    active_behaviors.append(behavior1)
    active_behaviors.append(behavior2)
    
    behaviors.append(behavior1)
    behaviors.append(behavior2)
    behaviors.append(behavior3)
    
    imotobo = Imotob("Straight", "Straight", M)
    #motobs = list()
    #motobs.append(imotobo)
    arbitrator = Arbitrator(behaviors)
    bbcon = BBCON(behaviors, active_behaviors, sensobs, imotobo, arbitrator)
    ZumoButton().wait_for_press()
    i = 0
    while (i < 8):
        bbcon.run_one_timestep()
        i += 1

if __name__ == "__main__":
    main()


