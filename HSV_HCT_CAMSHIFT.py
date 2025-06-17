import cv2
import argparse
import numpy as np

def callback(value):
    pass
 
def main():
    camera = cv2.VideoCapture(0)
    dist = lambda x1,y1,x2,y2: (x1-x2)**2+(y1-y2)**2
    PrecCircle = None
    cv2.namedWindow("Trackbars", 0)
    cv2.createTrackbar("L – H", "Trackbars", 0, 179, callback)
    cv2.createTrackbar("U – H", "Trackbars", 179, 179, callback)
    cv2.createTrackbar("L – S", "Trackbars", 0, 255, callback)
    cv2.createTrackbar("U – S", "Trackbars", 255, 255, callback)
    cv2.createTrackbar("L – V", "Trackbars", 0, 255, callback)
    cv2.createTrackbar("U – V", "Trackbars", 255, 255, callback)
 
    while True:
        ret, image = camera.read()
        if not ret:
            break
 
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
 
        L_H = cv2.getTrackbarPos("L – H", "Trackbars")
        L_S = cv2.getTrackbarPos("L – S", "Trackbars")
        L_V = cv2.getTrackbarPos("L – V", "Trackbars")
        U_H = cv2.getTrackbarPos("U – H", "Trackbars")
        U_S = cv2.getTrackbarPos("U – S", "Trackbars")
        U_V = cv2.getTrackbarPos("U – V", "Trackbars")
 
        thresh = cv2.inRange(frame_to_thresh, (L_H, L_S, L_V), (U_H, U_S, U_V))
 
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        blurFrame = cv2.GaussianBlur(mask,(17,17),0)

        circles = cv2.HoughCircles(blurFrame, cv2.HOUGH_GRADIENT,1.2,100,
                              param1=100, param2=30, minRadius=10,maxRadius=400)
        if circles is not None:
            circles = np.uint32(np.around(circles))
            chosen = None
            for i in circles[0,:]:
                if chosen is None: chosen = i
                if PrecCircle is not None:
                    if dist (chosen[0], chosen[1], PrecCircle[0], PrecCircle[1]) <= dist(i[0],i[1],PrecCircle[0],PrecCircle[1]):
                        chosen = i
            
            cv2.circle(image, (chosen[0],chosen[1]), 1, (0,100,100), 3)
            cv2.circle(image, (chosen[0],chosen[1]), chosen[2], (255,0,255),3)
            
        
    
        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)
 
        if cv2.waitKey(1) & 0xFF is ord('q'):
            break
 
 
if __name__ == '__main__':
    main()