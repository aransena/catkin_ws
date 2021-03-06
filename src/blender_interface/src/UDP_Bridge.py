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

run_avg = 0

def get_udp_msg(data):
    global run_avg
    #print data
    device= data['Device']
    control= data['ControlLevel']
    bezelR = int(data['Clockwise'])
    bezelL = int(data['CounterClockwise'])
    alpha = data['ALPHA']
    beta = data['BETA']
    float_turn = (float(data['Turn'])*300)*-1
    #print turn
    if float_turn == 0:
        run_avg = 0

    max_vel = 100
    if float_turn > max_vel:
        float_turn = max_vel
    elif float_turn < -max_vel:
        float_turn = -max_vel
    prev_run = run_avg
    run_avg = (run_avg*2 + float_turn)/3
    turn = int(round(run_avg))
    #print "\t \t \t \t \t", float_turn, run_avg, prev_run, turn
    #turn = int(round(float_turn))
    mode = int(data['Mode'])
    global heading
    global ring
    direction = 0
    controlLvl = 0

    #print "Gamma: ",data['GAMMA'], "\tAlpha: ",data['ALPHA']
    #gamma = data['GAMMA']


    speed = 0 # default zero speed
    alpha = int(float(alpha))

    if alpha < 5 and alpha > -5:
        if control == 1:
            auto = 0

            if device == "SmartWatch":
                vel = float(beta)*-1
                if vel < 2.5 and vel > -5:
                    vel = 0
                #print vel
                #theta = float(data['ANGLE'])

                if vel == 0:
                    direction = 0
                    heading = 90

                    if bezelL == 1 and mode ==1:
                        if ring>0:
                            ring = 0
                        else:
                            if ring != -80:
                                ring -= 10
                            else:
                                ring = -80
                        heading=90#ring+90
                    elif bezelR == 1 and mode ==1:
                        if ring<0:
                            ring = 0
                        else:
                            if ring != 90:
                                ring += 10
                            else:
                                ring = 90
                        heading=90#ring+90

                    if mode == 2:

                        ring = int(round(turn*2.5))
                        heading = 90#ring+90

                else:
                    if vel > 0:
                        direction = 1
                        ring = 0
                    elif vel < 0:
                        direction = 2
                        ring = 0

                    speed = abs(int((vel/10)*500))

                    if bezelL == 1 and mode ==1:
                        if vel != 0:
                            if heading > 90:
                                heading = 90
                            else:
                                if heading != 10:
                                    heading -= 10
                                else:
                                    heading == 10

                    elif bezelR == 1 and mode == 1:
                        if vel != 0:
                            if heading < 90:
                                heading = 90
                            else:
                                if heading != 170:
                                    heading += 10
                                else:
                                    heading == 170
                    if mode == 2:
                        ring = 0
                        heading = turn + 90
        else:
            #heading = 90
            speed = 0
            if control == 1:
                control = 0
                auto = 0
            elif control ==2:
                controlLvl = control+1
                auto = 1
            elif control ==3:
                controlLvl = control+1
                auto = 1
#            controlLvl = control
	        direction= 0

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
        message = ",0,90,0,0,0,0,"

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
    #print msg

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
        rospy.loginfo("Running blender interface...")
        listener(pub)

    except rospy.ROSInterruptException, e:
        print "failed to launch node - error ", e
        sys.exit()
