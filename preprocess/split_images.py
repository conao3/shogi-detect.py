#!/usr/bin/env python

import cv2
import numpy as np
import itertools
import glob

def fit_size(img, h, w):
    size = img.shape[:2]
    f = min(h / size[0], w / size[1])
    return cv2.resize(img, (int(size[1] * f), int(size[0] * f)), interpolation=cv2.INTER_AREA)

def main():
    files = sorted(glob.glob('../images/raw/*'))
    print(len(files), "files")
    
    raw_imgs = [cv2.imread(f) for f in files]
    imgs = [fit_size(img, 500, 500) for img in raw_imgs]
    raw_img = raw_imgs[1]
    img = imgs[1]
    cv2.imshow('img', img)

if __name__ == '__main__':
    main()
