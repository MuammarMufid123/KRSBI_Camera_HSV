import numpy as np
import cv2 as cv
import argparse


img = cv.imread("D:/IRIS_HVS/krsbi7.jpg")
img_to_thresh = cv.cvtColor(img, cv.COLOR_BGR2HSV)
thresh = cv.inRange(img_to_thresh, (64, 59, 75), (93, 255, 255))
contours, hierarchy = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

contours = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)
result_flood = np.zeros_like(img)
for contour in contours:
    convexHull = cv.convexHull(contour)
    cv.drawContours(thresh, [convexHull], -1, (255, 0, 0), 2)
    cv.fillPoly(result_flood, [convexHull], color=(255, 255, 255))



result_filly_po = result_flood.copy()
mask = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)

# Choose a seed point outside the filled area
seed_point = (10, 10)

# Run floodFill outside the filled area
kan=cv.floodFill(result_flood, mask, seed_point, newVal=(255,255, 255), loDiff=(20, 20, 20), upDiff=(20, 20, 20))
result_flood_not = cv.bitwise_not(result_flood)

result_or = cv.bitwise_or(result_filly_po, result_flood_not )
result_or_not = cv.bitwise_not(result_or)


result_and = cv.bitwise_and(result_or, img_to_thresh)
result_lapangan = cv.bitwise_or(result_or_not, result_and)

phresh = cv.inRange(result_lapangan, (0, 100, 100), (15, 255, 255))
 
knl = np.ones((5,5),np.uint8)
mas = cv.morphologyEx(phresh, cv.MORPH_OPEN, knl)
mas = cv.morphologyEx(mas, cv.MORPH_CLOSE, knl)
cnts = cv.findContours(mas.copy(), cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[-2]
center = None
        
if len(cnts) > 0:
    c = max(cnts, key=cv.contourArea)
    ((x, y), radius) = cv.minEnclosingCircle(c)
    M = cv.moments(c)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
    if radius > 10:
        cv.circle(img, (int(x), int(y)), int(radius),(0, 255, 255), 2)
        cv.circle(img, center, 3, (0, 0, 255), -1)
        cv.putText(img,"center", (center[0]+10,center[1]), cv.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
        cv.putText(img,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
    

cv.imshow("img", img)
cv.imshow("thresh",thresh)
cv.imshow("result lapangan", result_lapangan)
cv.imshow("phresh",phresh)
cv.waitKey(0)
