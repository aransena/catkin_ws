#!/usr/bin/env python
import rospy
import socket
import sys
import json

heading=90 #default straight
ring = 0
from std_msgs.msg import String as ros_string

class udp_broadcaster:
    def __init__(self, udp_ip, udp_port):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #self.socket.bind((udp_ip, udp_port))
        #self.socket.connect((udp_ip, udp_port))
        rospy.loginfo("udp_listen.py: SUCCESS connecting to IP:%s Port:%d", udp_ip, udp_port)

def get_udp_msg(data):
    #print data
    device= data['Device']
    control= data['ControlLevel']
    bezelR = int(data['Clockwise'])
    bezelL = int(data['CounterClockwise'])
    alpha = data['ALPHA']
    beta = data['BETA']
    global heading
    global ring
    direction = 0
    controlLvl = 0
    #print "Gamma: ",data['GAMMA'], "\tAlpha: ",data['ALPHA']
    #gamma = data['GAMMA']


    speed = 0 # default zero speed
    alpha = int(float(alpha))

    if alpha < 5 and alpha > -5:
        if control == 0:
            auto = 0
            if device == "SmartWatch":
                vel = float(beta)*-1
                if vel < 2 and vel > -2:
                    vel = 0
                #print vel
                #theta = float(data['ANGLE'])

                if vel > 0:
                    direction = 1
                    ring = 0
                elif vel < 0:
                    direction = 2
                    ring = 0
                else:
                    direction = 0
                    heading = 90
                    if bezelL == 1:
                        if ring>0:
                            ring = 0
                        else:
                            if ring != -180:
                                ring -= 10
                            else:
                                ring = -180
                    elif bezelR == 1:
                        if ring<0:
                            ring = 0
                        else:
                            if ring != 180:
                                ring += 10
                            else:
                                ring = 180
                speed = abs(int((vel/10)*500))

                #stop_cmd = data['ControlLevel']

                #swipeL = data['SwipeLeft']
                #swipeR = data['SwipeRight']
                #tap = data['Press']
                #longPress = data['LongHold']
                mode = data['ControlLevel']
                #twist.linear.x = vel*(-1)#twist_mem.linear_x

                if bezelL == 1:
                    if vel != 0:
                        if heading > 90:
                            heading = 90
                        else:
                            if heading != 10:
                                heading -= 10
                            else:
                                heading == 10

                    #twist_mem.angular_z += 0.2
                    #else:
                    #twist_mem.angular_z = 0.7
                    #twist.angular.z = twist_mem.angular_z

                elif bezelR == 1:
                    if vel != 0:
                        if heading < 90:
                            heading = 90
                        else:
                            if heading != 170:
                                heading += 10
                            else:
                                heading == 170
                    #if mode == 1:
                    #twist_mem.angular_z -= 0.2
                    #else:
                    #twist_mem.angular_z = -0.7
                    #twist.angular.z = twist_mem.angular_z


                    #if mode == 1:
                    #twist.angular.z = twist_mem.angular_z
                    #elif mode == 2:
                    #    twist.angular.z = 0
                    #else:
                    #twist.angular.z = 0



        else:
            heading = 90
            speed = 0
            if control == 1:
                control = 0

            controlLvl = control
            auto = 1
    else:
        direction = 0
        heading = 90
        speed = 0
        auto = 0
        controlLvl = 0
        ring = 0

    #print twist
    return direction,heading,speed,auto,controlLvl,ring

def blender_interface(json_str, pub):
    try:
        data = json.loads(json_str.data)
        message = get_udp_msg(data)
    except:
        message = "0,90,0,0,0,0"

    ## Parse json into blender udp message here ##

    #g.values = array.split(",")
    #g.direction = int(g.values[0])     # 0 = still, 1 = forward, 2 = backward
    #g.angle = int(g.values[1])         # 90 = straight, 180 = hard right, >1-10 = hard left
    #g.speed = int(g.values[2])         # 0-500
    #g.auto = int(g.values[3])          # 0 = manual, 1 = auto
    #g.fingerNum = int(g.values[4])     # 0-3 (0 in manual)
    #g.ring = int(g.values[5])          # -180 <-> 180 # Turn on spot
    #message = "0,90,0,0,0,0"

    msg = str(message)[1:-1]
    #msg ="0, 90, 0, 0, 0, 0"
    print msg

    try:

        if not rospy.is_shutdown():
        ## place blender udp message in place of "data" here ##
        # Error 11:55 3rd May: [Errno 89] Destination address required #
            #print "sending hello message"
            pub.socket.sendto(str(msg),(udp_info[0],udp_info[1]))
    except Exception as e:
        print e.args ," - error"
        pass




def listener(pub):
    rospy.init_node('blender_interface', anonymous=True)
    rospy.Subscriber("websocket_server_msgs", ros_string, blender_interface, pub)

    rospy.spin()

if __name__ == "__main__":

    UDP_IP = "127.0.0.1" #<-- Self IP
    UDP_PORT = 21569#<-- Blender port
    udp_info = [UDP_IP,UDP_PORT]
    pub = udp_broadcaster(udp_info[0],udp_info[1])
    try:
        listener(pub)
    except rospy.ROSInterruptException, e:
        print "failed to launch node - error ", e
        sys.exit()
