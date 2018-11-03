#!/usr/bin/env python

import cv2
import numpy as np
import itertools
import glob

class CV2Window:
    def __init__(self, _name):
        self.name = _name
        
        cv2.namedWindow(self.name)

    def imgshow(self, img, wait=True):
        cv2.imshow(self.name, img)
        if wait:
            cv2.waitKey(0)

def fit_size(img, h, w):
    size = img.shape[:2]
    f = min(h / size[0], w / size[1])
    return cv2.resize(img, (int(size[1] * f), int(size[0] * f)), interpolation=cv2.INTER_AREA)

def main():
    mainWindow = CV2Window('main')
    
    files = sorted(glob.glob('../images/raw/*'))
    print(len(files), "files")
    
    raw_imgs = [cv2.imread(f) for f in files]
    imgs = [fit_size(img, 500, 500) for img in raw_imgs]
    raw_img = raw_imgs[1]
    img = imgs[1]
    mainWindow.imgshow(img)


if __name__ == '__main__':
    main()
