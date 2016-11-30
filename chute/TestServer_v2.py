import sys, math, os, string, time, argparse, json, subprocess
import io
import socket, struct
import base64
import StringIO
import glob
#import dlib
#from skimage import io
import PIL
from PIL import Image, ImageChops
import random

# Sets up an echo socket on the noted port. Written by William Seale based on internet documentation


HOST = ''
PORT = 8888


def start_server(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket Created')

    try:
        s.bind((host, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : {} Message {}'.format(str(msg[0]), msg[1]))
        sys.exit()

    print('Socket bind complete')

    s.listen(1)
    print('Socket now listening')

    while True:
        client, addr = s.accept()
        print('Connected to: {}'.format(addr))
        while (True):
            try:
                print("starting img loop")
                img = recieve_img(client)


                if (img is None):
                    print("** No image discovered")
                    time.sleep(m_sec / 1000)
                    continue
                else:
                    bytesIm=io.BytesIO(img)
                    # For now I'm just creating a "found" image for all incoming for testing.
                    found = Image.open(bytesIm)


                    fileName = "frame{}.jpg".format(time.time())
                    print('image found {}').format(fileName)
                    found.save(fileName)

                    outData=""
                    #Android app expects an | delimited list of point pairs with a trailing "|" to make the logic easier
                    #points are separated by a comma, so x1,y1|x2,y2|x3,y3|   etc and it will loop over all sent points
                    #this just generates four random
                    for i in range(0,3):
                        randX=random.randint(0,300)
                        randY=random.randint(0,300)
                        outData=outData+str(randX)+","+str(randY)+"|"
                    outData=outData+"\r"

                    client.sendall(outData)
                    #client.sendall(struct.pack('>i', len(data)) + data)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print('!! error: %s' % str(e))
    return client


def recieve_img(the_socket):
    print("waiting on image")
    # data length is packed into 4 bytes
    total_len = 0
    total_data = []
    size = sys.maxint
    size_data = sock_data = ''
    #Had a couple times where it seemed to miscalculate the size. Might be on the java side, but
    recv_size = 1024
    while total_len < size:
        sock_data = the_socket.recv(recv_size)
        #print("got initial data")
        if not total_data:
            if len(sock_data) > 4:
                size_data += sock_data
                size = struct.unpack('>i', size_data[:4])[0]
                recv_size = size
                print("size: {}").format(recv_size)
                if recv_size > 524288: recv_size = 524288
                total_data.append(size_data[4:])
            else:
                size_data += sock_data
        else:
            total_data.append(sock_data)
        total_len = sum([len(i) for i in total_data])
    print("final size: {}").format(recv_size)
    return ''.join(total_data)

if (__name__ == "__main__"):
    m_sec=5

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

        except KeyboardInterrupt:
            break
        except Exception as e:
            print('!! error: %s' % str(e))
            time.sleep(m_sec)

    print("Found IP %s" % ip)


    clientConn=start_server(ip)
    
    exit()


