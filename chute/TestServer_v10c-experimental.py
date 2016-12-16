import sys, math, os, string, time, argparse, json, subprocess
import io as baseio
import socket, struct
import base64
import StringIO
import glob
import dlib
from skimage import io
from skimage import draw
import PIL
from PIL import Image, ImageChops
import random
import select
from datetime import datetime


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
    global startInst
    total_len = 0
    total_data = []
    # data length is packed into 4 bytes
    # the_socket.setblocking(0)
    ready = select.select([the_socket],[],[],5)

    size = sys.maxint
    size_data = sock_data = ''
    #Had a couple times where it seemed to miscalculate the size. Might be on the java side, but
    recv_size = 1024
    startTime=int(time.time())
    startInst=datetime.now()

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
                if recv_size > 524288: recv_size = 524288
                total_data.append(size_data[4:])
            else:
                size_data += sock_data
        else:
            total_data.append(sock_data)
        total_len = sum([len(i) for i in total_data])

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
        return False, False, False
    else:

        for d in dets:
            left = d.left()
            top = d.top()
            right = d.right()
            bottom = d.bottom()

        ypoints = [top, top, bottom, bottom]
        xpoints = [right, left, left, right]
        rr,cc = draw.polygon_perimeter(ypoints, xpoints, shape=img.shape, clip=True)
        img[rr, cc] = 255

        fileName = "cp{}.jpg".format(CP)
        io.imsave(fileName, img)
        return True, xpoints, ypoints


if (__name__ == "__main__"):

    #useImageReturn=False #enables or disables image block globally
    useImageReturn=True
    debugLine = True
    startInst=datetime.now()

    subnet = ""
    ip = ''

    clientConn=start_server(ip)

    CP = 1 #initial CP we are looking for
    CP_last = 3 #last CP we need
    CP_init = False  #we have not yet found a CP

    if useImageReturn:
        #retImHandler = open('dogIm20k.jpg', 'rb')
        #retImHandler = open('dogIm.png', 'rb')
        #retImHandler = open('placeholder.png', 'rb')
        #retImHandler = open('dogImTiny.png', 'rb')
        retImHandler = open('dogImTinyGreen.jpg', 'rb')
        returnIm = retImHandler.read()
        retImHandler.close()
        retImBytesSize= len(returnIm)
        returnPlacement = [0, 0] #default
        checkIO=baseio.BytesIO(returnIm)
        retImCheck=Image.open(checkIO)

    while (True):
        try:
            img = recieve_img(clientConn)
            startImgProcessing=datetime.now()
            returnImage = False #set to True in appropriate block below to return an image in that case
            if (img is None):
                print("** No image discovered")
                break

            else:
                bytesIm=baseio.BytesIO(img)
                # For now I'm just creating a "found" image for all incoming for testing.
                imFromClient = Image.open(bytesIm)
                fileName = "frame{}.jpg".format(CP)
                imFromClient.save(fileName)
                outData = []
                #print('looking for CP{}').format(CP)
                foundCP, xp, yp = detectCP(fileName, CP)
                if (foundCP):
                    CP_init = True # we have found at least one CP
                    print('CP{} found').format(CP)

                    for i in range(0,4):
                        outData.append(xp[i])
                        outData.append(yp[i])
                    if useImageReturn:
                        returnImage = True
                        midX=(max(xp)+min(xp)) / 2
                        midY = (max(yp) + min(yp)) / 2
                        returnPlacement = [midX, midY]

                # elif (CP == 3):
                #     print('Reached Destination')
                #     #send a null shape
                #     outData=[0, 0, 0, 0, 0, 0, 0, 0]

                elif (CP_init):
                    foundCP, xp, yp = detectCP(fileName, CP+1)
                    if (foundCP):
                        CP = CP + 1
                        print('CP{} found').format(CP)
                        for i in range(0,4):
                            outData.append(xp[i])
                            outData.append(yp[i])

                    else:
                        #send a null shape
                        outData = [0, 0, 0, 0, 0, 0, 0, 0]

                else:
                    print('No CP found')
                    #send a generic rect for testing
                    outData = [45, 45, 65, 65, 45, 95, 25, 65]
                    #Testing - will return the placeholder:
                    # if useImageReturn:
                    #     returnImage=True
                    #     returnPlacement=[0, 0]

                # 9th int position is int 0 for 'no image returned' or 1 for 'image being sent back'
                #10th int position is similar, but for how many debug character bytes are being sent (D)
                #11+D are the debug bytes (if being sent)
                #12 (aka 11+D) starts with 3 integers (image size, X, Y) then the image bytes
                #i.e. 00 means we're just sending the points. 01 means points plus debug. 10 means points plus image.
                if (useImageReturn and returnImage):
                    outData.append(1)
                else:
                    outData.append(0)
                    # also need to do a second sendall with the encoded image data

                debugBytes=[]
                debugStr=""

                startTransmit=datetime.now()
                if (debugLine):
                    t1=startImgProcessing-startInst
                    t2=startTransmit-startInst
                    g1=int(t1.total_seconds()*1000)
                    g2=int(t2.total_seconds()*1000)
                    debugStr="recieve time: {}ms,  total time: {}ms".format(g1,g2)
                    debugBytes=debugStr.encode('utf-8')
                    outData.append(len(debugBytes))
                else:
                    outData.append(0)

                outBytes=struct.pack('>10i', *outData)
                if debugLine:
                    outBytes+=debugBytes
                if useImageReturn and returnImage:
                    outBytes+=struct.pack('>i', retImBytesSize)
                    outBytes+=struct.pack('>2i', *returnPlacement)
                    outBytes+=returnIm

                clientConn.sendall(outBytes)

                # clientConn.sendall(struct.pack('>10i', *outData))
                # if debugLine:
                #     clientConn.sendall(debugBytes)
                # if useImageReturn and returnImage:
                #     clientConn.sendall(struct.pack('>i', retImBytesSize))
                #     clientConn.sendall(struct.pack('>2i', *returnPlacement)) #x y coords of image returned
                #     clientConn.sendall(returnIm)


        except KeyboardInterrupt:
            break
        except Exception as e:
            print('!! error: %s' % str(e))
        
    clientConn.close()

    print('closing connection, no image in timeout period')

    exit()



