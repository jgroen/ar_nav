#!/usr/bin/python

import sys, math, os, string, time, argparse, json, subprocess
import socket, struct
import base64
import StringIO
import glob
import dlib
from skimage import io

try:
    import PIL
    from PIL import Image, ImageChops
except Exception as e:
    print('No PIL, please install "python-imaging-library" if on OpenWrt')
    sys.exit(1)


PORT = 8888


def setupArgParse():
    p = argparse.ArgumentParser(description='Object detection')
    p.add_argument('-m_sec', help='How much time (in ms) to wait between motion images', type=float, default=10.0)
    return p



def detectCP(img1, CP):
    """
            Detects the CP if pressent.
            Arguments:
                    img1 : the image data from the getImage() function
                    CP : the current CP we are looking for
            Returns:
                    None if no img data provided, or if CP is not detected
                    (raw) if CP detection successful
    """
    if(not img1):
        return None

    #Convert to Image so we can compare them using PIL
    try:
        raw1 = Image.open(img1) 
	#or Image.fromstring(mode, size, data) 
	#or Image.frombuffer(mode, size, data)
    except Exception as e:
        print('raw1: %s' % str(e))
        return None

    #Now try and find the CP
    detector = dlib.simple_object_detecotr('cp{}.svm'.format(CP))
    dets = detector(raw1)
    if dets == 0:
	return None
    else:
	return dets


def start_server(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket Created')

    try:
	s.bind((host,PORT))
    except socket.error as msg:
	print('Bind failed. Error Code : {} Messagee {}'.format(str(msg[0]),msg[1])
	sys.exit()

    print('Socket bind complete')

    s.listen(1)
    print('Socket now listening')

    while True:    
	client, addr = s.accept()
    	print('Connected to: {}'.format(addr))



def recieve_img(the_socket):
    #data length is packed into 4 bytes
    total_len=0
    total_data=[]
    size=sys.maxint
    size_data=sock_data=''
    recv_size=8192
    while total_len<size:
        sock_data=the_socket.recv(recv_size)
        if not total_data:
            if len(sock_data)>4:
                size_data+=sock_data
                size=struct.unpack('>i', size_data[:4])[0]
                recv_size=size
                if recv_size>524288:recv_size=524288
                total_data.append(size_data[4:])
            else:
                size_data+=sock_data
        else:
            total_data.append(sock_data)
        total_len=sum([len(i) for i in total_data])
    return ''.join(total_data)
	

def send_size(data):
    client.sendall(struct.pack('>i', len(data))+data)


if(__name__ == "__main__"):
    p = setupArgParse()
    args = p.parse_args()

    m_sec = args.m_sec


    ## Determine IP address
    #######################################################################
    # make sure apr table contains all devices
    # Get the subnet of paradrop
    subnet = ""
    ip = ""
    while(ip == ""):
        try:

            # Get the subnet if haven't yet
            if (subnet == ""):
                cmd = "ifconfig -a | grep 'inet addr:192.168' | awk '{print $2}' | egrep -o '([0-9]+\.){2}[0-9]+'"
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                output, errors = p.communicate()
                if (output != ""):
                    subnet = output.rstrip()

                    # Add a . after 192.168.xxx
                    subnet = subnet + '.'
                    print "subnet: " + subnet

            # Prevent race condition by running this in the loop to put the device on the arp table
            cmd = "echo $(seq 100 200) | xargs -P255 -I% -d' ' ping -W 1 -c 1 " + subnet + "% | grep -E '[0-1].*?:'"
            p2 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            output2, errors2 = p2.communicate()

            # Search arp for leading mac address bits
            cmd="arp -a | grep -e '28:10:7b' -e 'b0:c5:54' -e '01:b0:c5' | awk '{print $2}' | egrep -o '([0-9]+\.){3}[0-9]+'"
            p3 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            output3, errors3 = p3.communicate()

            if (output3 != ""):
                print "output3: '" + output3 + "'"
                ip = output3.rstrip()

                # Set iptables for wan port access
                cmd="iptables -t nat -A PREROUTING -p tcp --dport 81 -j DNAT --to-destination " + ip + ":80"
                print "cmd: " + cmd
                p4 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                output4, errors4 = p4.communicate()
                cmd="iptables -t nat -A POSTROUTING -p tcp -d " + ip + " --dport 81 -j MASQUERADE"
                print "cmd: " + cmd
                p5 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                output5, errors5 = p5.communicate()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print('!! error: %s' % str(e))
            time.sleep(m_sec/1000)

    print("Found IP %s" % ip)

    start_server(ip)

    # Setup while loop requesting images from webcam
    while(True):
        try:

	    img = recieve_img(client)
            
            # Did we get an image?
	    CP = 1  #initial CP we are looking for
	    CP_last = 3 #last CP we need
	    CP_init = False #we have not yet found the first CP
            if(img is None):
                print("** No image discovered")
                time.sleep(m_sec/1000)
                continue
            else:
                found = detectCP(img, CP)
		if (found):
                    print('CP {} found'.format(CP))
                    fileName = "frame{}.png".format(time.time())
                    found.save(fileName)
		    send_size(found)
		    CP_init = True # we have found at least the first CP
		elif CP = CP_last:
		    break
		elif (CP_init):
		    found = detectCP(img, CP+1)
		    if (found)
			print('CP {} found'.format(CP+1))
                    	fileName = "frame{}.png".format(time.time())
                    	found.save(fileName)
		    	send_size(found)
		        CP = CP + 1
        except KeyboardInterrupt:
            break
        except Exception as e:
            print('!! error: %s' % str(e))

