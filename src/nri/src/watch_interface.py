#!/usr/bin/env python

import roslib
import rospy

from geometry_msgs.msg import Twist


# from std_msgs.msg import Int8 as Int

def talker():
	pub = rospy.Publisher('cmd_vel', Twist)
	# pub2 = rospy.Publisher('int', Int)
	rospy.init_node('watch_interface', anonymous=True)

	twist = Twist()
	twist.linear.x = 1
	twist.angular.z = 0

	twist.linear.y = 0
	twist.linear.z = 0
	twist.angular.x = 0
	twist.angular.y = 0

	rate = rospy.Rate(10)  # 10hz
	while not rospy.is_shutdown():
		notice_str = "watch_interface: Sending cmd_vel %s" % rospy.get_time()
		rospy.loginfo(notice_str)
		pub.publish(twist)
		# pub2.publish(0)
		rate.sleep()

	## code to stop
	# twist=Twist()
	# rospy.loginfo("watch_interface: Stopping")
	# p.publish(twist)


if __name__ == "__main__":

	try:
		talker()
	except rospy.ROSInterruptException:
		pass
