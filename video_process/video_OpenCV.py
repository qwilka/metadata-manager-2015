"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
# Required: Python 3.4 and OpenCV 3.0
import logging
logger = logging.getLogger(__name__)
import decimal 
import os
import sys
import time

import cv2
import numpy as np


LMOUSECLICK = False
def onLeftMouseClick(event, x, y, flags, param):   
    global LMOUSECLICK
    if event == cv2.EVENT_LBUTTONUP:
        LMOUSECLICK = True


def get_video_property(vidCap, property_name):
    if property_name == 'fps':
        return vidCap.get(cv2.CAP_PROP_FPS)
    elif property_name == 'size':
        return ( vidCap.get(cv2.CAP_PROP_FRAME_WIDTH), 
                vidCap.get(cv2.CAP_PROP_FRAME_HEIGHT)  )

def round_halfup(ip):
    op = decimal.Decimal(ip).quantize(1,rounding=decimal.ROUND_HALF_UP)
    return int(op)
    


def video_join_row(filelist, op_file, bbox=None, scale=1, vidCodec='H264',
                   tstartend=None, showvid=False):
    if not isinstance(filelist, (list, tuple)):
        raise TypeError("argument 'filelist' must be list or tuple; %s" % (filelist,))
    vidCapList = []
    fps = None
    fsize = [0,0]  # NOTE: fsize is [height, width]
    for vidfile in filelist:
        if not os.path.isfile(vidfile):
            raise ValueError("cannot find file %s" % (vidfile,) )
        vidCap = cv2.VideoCapture(vidfile)
        _fps = vidCap.get(cv2.CAP_PROP_FPS)
        if fps and fps != _fps:
            raise ValueError("inconsistency in video frame rates %s %d %d" % (vidfile, fps,_fps) )
        fps = _fps 
        _size = (int(vidCap.get(cv2.CAP_PROP_FRAME_HEIGHT)),  
                int(vidCap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        if _size[0] > fsize[0]: fsize[0] = _size[0]
        if _size[1] > fsize[1]: fsize[1] = _size[1]
        #if tstart:
        #    vidCap.set(cv2.CAP_PROP_POS_MSEC, tstart*1000)
        vidCapList.append(vidCap)
    fstart = int(vidCap.get(cv2.CAP_PROP_POS_FRAMES))
    ftotal = int(vidCap.get(cv2.CAP_PROP_FRAME_COUNT))
    tinterval = 1/fps
    #if tend:
    #    fend = int(tend * fps)
    #else:
    #    fend = ftotal
    if os.path.isfile(op_file):
        os.unlink(op_file)
    if bbox:
        x1 = bbox[0]
        y1 = bbox[1]
        x2 = bbox[2]
        y2 = bbox[3]
    else:
        x1 = 0
        y1 = 0
        x2 = fsize[1]
        y2 = fsize[0]      
    w = x2 - x1
    h = y2 - y1
    # note that fsize_scaled is (width, height), as required by cv2.VideoWriter
    fsize_scaled = round_halfup(w*scale)*len(vidCapList), round_halfup(h*scale)
    logger.info("Setting output video %s size (w,h) to %s" % (op_file, fsize_scaled))
    fourcc = cv2.VideoWriter_fourcc(*vidCodec)   
    vidWriter = cv2.VideoWriter()
    vidWriter.open(op_file, fourcc, fps, fsize_scaled, True)
    if showvid:
        cv2.namedWindow('ProcessVideo')
        cv2.setMouseCallback('ProcessVideo', onLeftMouseClick) 
    if not tstartend:
        tstartend = (0, (ftotal-1)*tinterval)
    it = iter(tstartend)
    for tstart, tend in zip(it, it):
        for vidCap in vidCapList:
            vidCap.set(cv2.CAP_PROP_POS_MSEC, tstart*1000)
        fstart = int(vidCap.get(cv2.CAP_PROP_POS_FRAMES))
        fend = int(tend * fps)
        for fcount in range(fstart, fend+1):
            sys.stdout.write("\rtime=%.3f, frame=%d" % (fcount*tinterval, fcount))
            for ii, vidCap in enumerate(vidCapList):
                try:
                    success, frame = vidCap.read()
                    if frame.shape[0:2] != tuple(fsize): 
                        logger.warning("Warning: FRAME sizes not equal, padding out %s" % (frame.shape[0:2],))
                        newframe = np.zeros((fsize[0], fsize[1], 3), dtype=np.uint8)
                        newframe[:frame.shape[0],:frame.shape[1]] = frame
                        frame = newframe
                except:
                    frame = np.ones((fsize[0], fsize[1], 3), dtype=np.uint8)
                if bbox:
                    frame = frame[y1:y2, x1:x2]
                if ii==0:   
                    vidcombined = frame  
                else:
                    vidcombined = np.concatenate((vidcombined, frame), axis=1)
            vidcombined = cv2.resize(vidcombined, (0,0), fx=scale, fy=scale)
            vidWriter.write(vidcombined)
            if showvid:
                #if cv2.waitKey(1) != -1 or LMOUSECLICK:
                waitkey = cv2.waitKey(1)  
                if waitkey == 81 or waitkey == 113: # press 'q' key to quit
                    break
                cv2.imshow('ProcessVideo', vidcombined)
    vidWriter.release()
    if showvid:
        cv2.destroyWindow('ProcessVideo')
    sys.stdout.write("\nCompleted time=%.3f, frame=%d\n" % (fcount*tinterval, fcount))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    op_file = 'output.avi'
    data_dir = '/home/develop/Downloads/MBES_data/18-F-2824 (SKL22)/VISUALWORKS/VisualworksReports/Projects/9821/DATA_201401091537060'
    filelist = [ os.path.join(data_dir, 'VIDEO_201401091537060@Stbd.mpg' ) ,
     os.path.join(data_dir, 'VIDEO_201401091537060@Centre.mpg' ) ,
     os.path.join(data_dir, 'VIDEO_201401091537060@Port.mpg' ) ]
    #video_join_row(filelist, op_file, tend=10, scale=0.5, showvid=True)
    video_join_row(filelist, op_file, bbox=(20,125, 700,500),
                   tstartend=(1,5, 200,205, 300,305), scale=0.5, showvid=True)
    