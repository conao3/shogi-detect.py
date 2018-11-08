#!/usr/bin/env python

import sys
import os
import re
import cv2
import numpy as np
import scipy.stats
import itertools
import glob

class Point:
    # 2D point (x,y).
    def __init__(self, _x=0, _y=0):
        self.x = _x
        self.y = _y

class Range:
    # 2D range p1 to p2.
    
    def __init__(self, _p1=Point(), _p2=Point()):
        self.p1 = _p1
        self.p2 = _p2
        
class CV2Window:
    # CV2 named window rapper.
    
    def __init__(self, _name):
        self.name = _name
        
        cv2.namedWindow(self.name)

    def imgshow(self, img, wait=False):
        cv2.imshow(self.name, img)
        if wait:
            cv2.waitKey(0)

    def close(self):
        cv2.destroyWindow(self.name)

def fit_size(raw_img, show=True, h=500, w=500):
    # Resize numpy image data fit to h, w. Contain aspect ratio.
    # IMG required to be a color numpy image data.
    # H is height, W is width as integer.
    
    size = raw_img.shape[:2]
    f = min(h / size[0], w / size[1])
    img = cv2.resize(raw_img, (int(size[1] * f), int(size[0] * f)), interpolation=cv2.INTER_AREA)
    if show:
        window = CV2Window('raw image')
        window.imgshow(img)
        
    return img

def get_edges(img, show=True):
    # Edge detection by 'canny edge detection'.
    # IMG required to be a color numpy image data.
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    if show:
        window = CV2Window('edge detection')
        window.imgshow(edges)
        
    return edges

def get_lines(img, show=True, threshold=80, minLineLength=50, maxLineGap=5):
    # Line detection by 'stochastic hough transform'.
    # IMG required to be a color numpy image data.
    
    edges = get_edges(img, show)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold, minLineLength, maxLineGap)
    if show:
        window = CV2Window('line detection')
        tmpimg = np.copy(img)
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(tmpimg, (x1,y1), (x2,y2), (0,255,0), 2)
            
        window.imgshow(tmpimg)
    return lines

def get_contours(img, show=True):
    # Extract contours.
    # IMG required to be a color numpy image data.
    
    edges = get_edges(img, show)
    contours = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]

    # remove too small contours
    min_area = img.shape[0] * img.shape[1] * 0.2
    large_contours = [c for c in contours if cv2.contourArea(c) > min_area]

    if show:
        window = CV2Window('contour detection (raw)')
        tmpimg = np.copy(img)
        cv2.drawContours(tmpimg, contours, -1, (0,255,0), 3)
        window.imgshow(tmpimg)
        
    return large_contours

def get_convexes(img, show=True):
    # Get convex hull(凸包) as expansion small lak.
    # IMG required to be a color numpy image data.
    
    contours = get_contours(img, show)
    convexes = [cv2.convexHull(cont) for cont in contours]
    
    if show:
        window = CV2Window('contour detection (convex hull)')
        tmpimg = np.copy(img)
        cv2.drawContours(tmpimg, convexes, -1, (0,255,0), 2)
        window.imgshow(tmpimg)
        
    return convexes

def get_convex_poly(img, show=True):
    # Get convex polygon as linear approximation of contour.
    # IMG required to be a color numpy image data.
    
    contours = get_convexes(img, show)
    polies = [cv2.approxPolyDP(cont, 0.02*cv2.arcLength(cont,True), True) for cont in contours]

    if show:
        window = CV2Window('contour detection (linear approx)')
        tmpimg = np.copy(img)
        cv2.drawContours(tmpimg, polies, -1, (0,255,0), 2)
        window.imgshow(tmpimg)
        
    return polies

def get_best_poly(img, show=True):
    # Get best appropriate (closest to the square) polygon.
    # POLIES is 2D polygon array data obtained by get_converx_poly.

    # calc score
    def calc_score(poly):
        arclen = cv2.arcLength(poly, True)
        edge_lens = [np.linalg.norm(poly[i] - poly[(i+1) % 4]) for i in range(4)]
        score = 1 / (sum([abs(arclen/4 - edge_len) for edge_len in edge_lens]) + 1)    # avoid devide by zero
        return score

    # get all polygons
    polies = get_convex_poly(img, show)

    # exclude polygons other than 4 corners
    targetPolies = [poly for poly in polies if poly.shape[0] == 4]

    scores = [calc_score(poly) for poly in targetPolies]
    best_poly = targetPolies[scores.index(max(scores))]

    if show:
        window = CV2Window('contour detection (closest square)')
        tmpimg = np.copy(img)
        cv2.drawContours(tmpimg, [best_poly], 0, (0,255,0), 2)
        window.imgshow(tmpimg)
        
    return best_poly

def makeExactlyPoly(poly):
    def retPoint(xrank, yrank):
        if xrank == 1 or xrank == 2:
            if yrank == 1 or yrank == 2:
                result = [0, 0]
            else:
                result = [0, 300]
        else:
            if yrank == 1 or yrank == 2:
                result = [300, 0]
            else:
                result = [300, 300]
        return result
    
    tpoly = poly[:,0]
    xpoint = tpoly[:,0]
    ypoint = tpoly[:,1]
    xrank = scipy.stats.rankdata(xpoint, method='ordinal')
    yrank = scipy.stats.rankdata(ypoint, method='ordinal')

    result = [retPoint(xrank[i], yrank[i]) for i in range(4)]
    return result
    
def trans_square(img, poly, show=True):
    # transform to right square
    # IMG required to be a color numpy image data.
    # POLY is best fitted to board polygon

    srcPoly = np.float32(poly)
    transPoly = np.float32(np.array(makeExactlyPoly(srcPoly)))

    M = cv2.getPerspectiveTransform(srcPoly, transPoly)
    transImg = cv2.warpPerspective(img, M, (300, 300))

    if show:
        window = CV2Window('trans square')
        window.imgshow(transImg)

    return transImg
    
def cut_piecies(img, poly, filepath, show=True):
    # Cut each piecies.
    # IMG required to be a color numpy image data.
    # POLY is best fitted to board polygon

    # transform to right square
    transimg = trans_square(img, poly, show)

    diffx = transimg.shape[0]/9
    diffy = transimg.shape[1]/9
    for xindex in range(9):
        for yindex in range(9):
            currentx = diffx * xindex
            currenty = diffy * yindex
            dstimg = transimg[(int)(currentx):(int)(currentx+diffx), (int)(currenty):(int)(currenty+diffy)]

            dirpath, basename = os.path.split(filepath)
            _, exttype = os.path.splitext(filepath)
            
            dirpath = dirpath.replace('raw', 'piecies')
            retmp = re.match(r"([0-9]*).(.*)", basename)
            imgnum = retmp[1]
            
            graylevel = "%04d" % (int)(cv2.cvtColor(dstimg, cv2.COLOR_RGB2GRAY).sum()/(255*33*33)*10000)
            dstimgpath = "%s/%s-%s-(%s-%s)%s" % (dirpath, graylevel, imgnum, xindex+1, yindex+1, exttype)

            cv2.imwrite(dstimgpath, dstimg)

    dstimgpath = filepath.replace('raw', 'board')
    cv2.imwrite(dstimgpath, transimg)
    
def get_board_corners(raw_img, filepath, show=True):
    # Get range of shogi board as 2Dpoint (x1,y1), (x2,y2).
    # IMG required to be a color numpy image data.

    # resize
    img = fit_size(raw_img, show, 500, 500)

    # choose best fit polygon detection
    poly = get_best_poly(img, show)

    # cut piecies
    cut_piecies(img, poly, filepath, show)
    
def main():
    if (len(sys.argv) == 0):
        frgdebug = False
    else:
        frgdebug = True
        
    imgpaths = sorted(glob.glob('../images/raw/*.png'))

    for imgpath in imgpaths:
        try:
            print("processing...: %s" % os.path.basename(imgpath))
            get_board_corners(cv2.imread(imgpath), imgpath, False)
            if frgdebug:
                cv2.waitKey(0)
        except:
            print("error: %s" % os.path.basename(imgpath))
    

if __name__ == '__main__':
    main()
