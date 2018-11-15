#!/usr/bin/env python

import sys
import os
import re
import pdb
import cv2
import numpy as np
import glob

class CV2Window:
    # CV2 named window rapper.
    
    def __init__(self, _name):
        self.name = _name
        
        cv2.namedWindow(self.name)

    def imshow(self, img, wait=False):
        cv2.imshow(self.name, img)
        if wait:
            cv2.waitKey(0)

    def close(self):
        cv2.destroyWindow(self.name)
        
def main():
    parentdir = "../images"
    dirnames = ["_pfu", "_pfur", "_pgin", "_phi", "_phir", "_pka", "_pkaku", "_pkakur", "_pkar", "_pkei", "_pkeir", "_pkin", "_po", "por"]

    for dirname in dirnames:
        images = sorted(glob.glob("%s/%s/*.png" % (parentdir, dirname)))

        savedirname = re.sub('^_p', '_n', dirname)
        for image in images:
            imagename = os.path.basename(image)
            saveimagepath = "%s/%s/%s" % (parentdir, savedirname, imagename)

            img = cv2.imread(image)
            transimg = cv2.flip(img, -1)

            cv2.imwrite(saveimagepath, transimg)
            

if __name__ == '__main__':
    main()
