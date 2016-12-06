import sys, math, os, string, time, argparse, json, subprocess
import io as baseio
import socket, struct
import base64
import StringIO
import glob
import dlib
from skimage import io
from skimage.draw import polygon_perimeter
import PIL
from PIL import Image, ImageChops
import random
import select


HOST = ''
PORT = 8888
xpoints = ''
ypoints = ''


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


    client, addr = s.accept()
    print('Connected to: {}'.format(addr))
        
    return client


def recieve_img(the_socket):
    total_len = 0
    total_data = []
    print("waiting on image")
    # data length is packed into 4 bytes
    # the_socket.setblocking(0)
    ready = select.select([the_socket],[],[],5)

    size = sys.maxint
    size_data = sock_data = ''
    #Had a couple times where it seemed to miscalculate the size. Might be on the java side, but
    recv_size = 1024
    startTime=int(time.time())

    while total_len < size:
        if (int(time.time() - startTime) > 5):
            return None
        #the_socket.settimeout(5000)
        sock_data = the_socket.recv(recv_size)
        #print("data loop,time {}").format(time.time()-startTime)
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



def detectCP(img1, CP):
    """
            Detects the CP if pressent.
            Arguments:
                    img1 : the image data from the getImage() function
                    CP : the current CP we are looking for
            Returns:
                    None if no img data provided, or if CP is not detected
                    (jpg) if CP detection successful
    """

    #Now try and find the CP
    img = io.imread(img1)
    svm = "cp{}.svm".format(CP)
    detector = dlib.fhog_object_detector(svm)
    dets = detector(img)

    if len(dets) == 0:
        return False
    else:

	for d in dets:
	    left = d.left()
	    top = d.top()
	    right = d.right()
	    bottom = d.bottom()

	ypoints = [top, top, bottom, bottom]
	xpoints = [right, left, left, right]
	
	rr,cc = polygon_perimeter(ypoints, xpoints, shape=img.shape, clip=True)
   	img[rr, cc] = 255

	fileName = "cp{}_{}.jpg".format(CP, time.time())
	io.imsave(fileName, img)
	return True


if (__name__ == "__main__"):
    m_sec=5

    subnet = ""
    ip = ''

    print("Found IP %s" % ip)

    clientConn=start_server(ip)

    while (True):
        try:
            print("starting img loop")
            img = recieve_img(clientConn)


            if (img is None):
                print("** No image discovered")
                #time.sleep(5)

                break
            else:
                bytesIm=baseio.BytesIO(img)
	    # For now I'm just creating a "found" image for all incoming for testing.
                found = Image.open(bytesIm)	   
                fileName = "frame{}.jpg".format(time.time())
                print('image found {}').format(fileName)
                found.save(fileName)

	    	foundCP = detectCP(fileName, 2)
		if (foundCP):
		    print('CP 2 found')
                    outData=""
                    #Android app expects an | delimited list of point pairs with a trailing "|" to make the logic easier
                    #points are separated by a comma, so x1,y1|x2,y2|x3,y3|   etc and it will loop over all sent points
			
                    for i in range(len(xpoints)):                       
			outData=outData+str(xpoints[i])+","+str(ypoints[i])+"|"
                    	outData=outData+"\r"

                    clientConn.sendall(outData)
                    #client.sendall(struct.pack('>i', len(data)) + data)

		else:
		    print('No CP found')
		    #send a null shape
		    outData="0,0|0,0|0,0|0,0|\r"
		    clientConn.sendall(outData)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print('!! error: %s' % str(e))
        
    clientConn.close()

    print('closing connection, no image in timeout period')

    exit()

