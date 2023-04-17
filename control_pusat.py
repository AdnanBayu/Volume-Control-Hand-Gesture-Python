from main import HandDetection
import cv2
import math
import numpy as np
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

handDetection = HandDetection(min_detection_confidence=0.5,min_tracking_confidence=0.5)

webcam = cv2.VideoCapture()
webcam.open(0, cv2.CAP_DSHOW)

min_dest,max_dest = 16,190

#set the pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


while True:
    #set webcam
    status, frame = webcam.read()
    frame = cv2.flip(frame,1)

    handLandmarks = handDetection.findHandsLandMarks(image=frame, draw=True)

    if len(handLandmarks)!=0:
        x4,y4 = handLandmarks[4][1], handLandmarks[4][2]    #thumb tip position
        x8,y8 = handLandmarks[8][1], handLandmarks[8][2]    #index finger tip position

        #draw circle in both finger
        cv2.circle(frame, (x4,y4),10,(255,255,0),cv2.FILLED)
        cv2.circle(frame, (x8,y8),10,(255,255,0),cv2.FILLED)
        xTengah, yTengah = int((x4+x8)/2), int((y4+y8)/2)
        cv2.circle(frame, (xTengah,yTengah),6,(255,255,0),cv2.FILLED)   #middle circle between two finger
        cv2.line(frame,(x4,y4),(x8,y8),(255,255,0),3)                   #draw line connecting two finger

        #volume bar
        length = math.hypot(x4-x8,y4-y8)
        # print(str(length))         #data check for mapping volume
        
        #mapping volume value
        vol_bar = np.interp(length,[min_dest,max_dest],[340,143])
        vol_persen = np.interp(length,[min_dest,max_dest],[0,100])
        
        cv2.rectangle(frame,(55,140),(85,340),(0,0,0),3)                            #volume bar frame
        cv2.rectangle(frame,(58,int(vol_bar)),(82,337),(150,150,0),cv2.FILLED)      #vol bar fill

        cv2.putText(frame, f'Vol = {int(vol_persen)} %', (18,380), cv2.FONT_HERSHEY_COMPLEX, 0.6,(150,150,0),2)

        #data check finger position
        #print(x4,y4)

        # set the system volume
        volume.SetMasterVolumeLevelScalar(vol_persen / 100, None)

    cv2.imshow("hand landmark", frame)

    if cv2.waitKey(1)==ord('a'):        #to exit from the program loop press 'a'
        break

cv2.destroyAllWindows()
webcam.release()