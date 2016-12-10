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


    startInst=datetime.now()

    subnet = ""
    ip = ''

    clientConn=start_server(ip)

    CP = 1 #initial CP we are looking for
    CP_last = 3 #last CP we need
    CP_init = False  #we have not yet found a CP

    #retImHandler = open('placeholder.png', 'rb')
    #returnIm = retImHandler.read()
    #retImHandler.close()
    #retImBytesSize= len(returnIm)

    while (True):
        try:
            img = recieve_img(clientConn)
            startImgProcessing=datetime.now()
            if (img is None):
                print("** No image discovered")
                break

            else:
                bytesIm=baseio.BytesIO(img)
                # For now I'm just creating a "found" image for all incoming for testing.
                imFromClient = Image.open(bytesIm)
                fileName = "frame{}.jpg".format(CP)
                imFromClient.save(fileName)
                #change this to True if we want to send an image back
                returnImage = False
                outData = []
                #print('looking for CP{}').format(CP)
                foundCP, xp, yp = detectCP(fileName, CP)
                if (foundCP):
                    CP_init = True # we have found at least one CP
                    print('CP{} found').format(CP)

                    #Updated android apk looked for 8 total packed integers x y x y x y x y

                    for i in range(0,4):
                        outData.append(xp[i])
                        outData.append(yp[i])
                        #outData=outData+str(4*xp[i])+","+str(4*yp[i])+"|"
                    #outData=outData+"\r"
                    #clientConn.sendall(outData)
                    #client.sendall(struct.pack('>i', len(data)) + data)
                
                elif (CP == 3):
                    print('Reached Destination')
                    #send a null shape
                    #outData="0,0|0,0|0,0|0,0|\r"
                    #clientConn.sendall(outData)
                    outData=[0, 0, 0, 0, 0, 0, 0, 0]

                elif (CP_init):
                    foundCP, xp, yp = detectCP(fileName, CP+1)
                    if (foundCP):
                        CP = CP + 1
                        print('CP{} found').format(CP)
                        #outData=""
                        for i in range(0,4):
                            outData.append(xp[i])
                            outData.append(yp[i])
                            #outData=outData+str(4*xp[i])+","+str(4*yp[i])+"|"
                        #outData=outData+"\r"
                        #clientConn.sendall(outData)
                    else:
                        #send a null shape
                        #outData="0,0|0,0|0,0|0,0|\r"
                        #clientConn.sendall(outData)
                        outData = [0, 0, 0, 0, 0, 0, 0, 0]

                else:
                    print('No CP found')
                    #send a null shape
                    #outData="0,0|0,0|0,0|0,0|\r"
                    #clientConn.sendall(outData)
                    outData = [0, 0, 0, 0, 0, 0, 0, 0]
                    #Testing - will return placeholder:
                    returnImage=True


                # 9th int position is int 0 for 'no image returned' or 1 for 'image being sent back'
                #10th int position is similar, but for how many debug characters are being sent
                #   11th int position is int byte size for image (if being sent)
                #   11+ are the bytes of the image
                if (returnImage):
                    outData.append(1)
                else:
                    outData.append(0)
                    # also need to do a second sendall with the encoded image data

                debugBytes=[]
                debugStr=""
                debugLine=True
                startTransmit=datetime.now()
                if (debugLine):
                    t1=startImgProcessing-startInst
                    t2=startTransmit-startImgProcessing
                    g1=int(t1.total_seconds()*1000)
                    g2=int(t2.total_seconds()*1000)
                    debugStr="recieve time: {}ms,  processing time: {}ms".format(g1,g2)
                    debugBytes=debugStr.encode('utf-8')
                    outData.append(len(debugBytes))
                else:
                    outData.append(0)

                clientConn.sendall(struct.pack('>10i', *outData))
                if debugLine:
                    clientConn.sendall(debugBytes)
                if returnImage:
                    clientConn.sendall(struct.pack('>i', retImBytesSize))
                    clientConn.sendall(returnIm)


        except KeyboardInterrupt:
            break
        except Exception as e:
            print('!! error: %s' % str(e))
        
    clientConn.close()

    print('closing connection, no image in timeout period')

    exit()


