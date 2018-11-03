#!/usr/bin/env python

import cv2
import numpy as np
import itertools
import glob

class CV2Window:
    def __init__(self, _name):
        self.name = _name
        
        cv2.namedWindow(self.name)

    def imgshow(self, img, wait=False):
        cv2.imshow(self.name, img)
        if wait:
            cv2.waitKey(0)

    def close(self):
        cv2.destroyWindow(self.name)

def fit_size(img, h, w):
    size = img.shape[:2]
    f = min(h / size[0], w / size[1])
    return cv2.resize(img, (int(size[1] * f), int(size[0] * f)), interpolation=cv2.INTER_AREA)

def get_edges(img, show=True):
    # Edge detection by canny edge detection.
    # IMG required to be a color numpy image data.
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    if show:
        window = CV2Window('edge detection')
        window.imgshow(edges)
        
    return edges

def get_lines(img, show=True, threshold=80, minLineLength=50, maxLineGap=5):
    # Line detection by stochastic Hough transform
    # IMG required to be a color numpy image data.
    
    edges = get_edges(img, show)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold, minLineLength, maxLineGap)
    if show:
        window = CV2Window('line detection')
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
            
        window.imgshow(img)
    return lines

def get_board_point(raw_img, show=True):
    # Get range of shogi board as 2Dpoint (x1,y1), (x2,y2).
    # IMG required to be a color numpy image data.

    # resize
    img = fit_size(raw_img, 500, 500)

    if show:
        rawImgWindow = CV2Window('raw image')
        rawImgWindow.imgshow(img)

    # line detection
    lines = get_lines(img, show)

    
def main():
    imgpaths = sorted(glob.glob('../images/raw/*.png'))

    points = [get_board_point(cv2.imread(imgpath), False) for imgpath in imgpaths]
    
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
