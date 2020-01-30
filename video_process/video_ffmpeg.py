"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
# https://trac.ffmpeg.org/wiki/Create%20a%20mosaic%20out%20of%20several%20input%20videos
'''
ffmpeg \
	-i VIDEO_201401091537060@Stbd.mpg -i VIDEO_201401091537060@Centre.mpg -i VIDEO_201401091537060@Port.mpg \
	-filter_complex "
		nullsrc=size=576x144 [base];
		[0:v] setpts=PTS-STARTPTS, scale=192x144 [port];
		[1:v] setpts=PTS-STARTPTS, scale=192x144 [centre];
		[2:v] setpts=PTS-STARTPTS, scale=192x144 [starboard];
		[base][port] overlay=shortest=1 [tmp1];
		[tmp1][centre] overlay=shortest=1:x=192 [tmp2];
		[tmp2][starboard] overlay=shortest=1:x=384
	" \
	-c:v libx264 output.mkv
'''
import decimal 
import json
import logging
import os
#import shlex
import subprocess
import sys
logger = logging.getLogger(__name__)



def video_join_row(filelist, opfile='output.mkv', scale=1, vidlib='ff',
                    dryrun=False):
    if vidlib.lower().startswith('ff'):
        converter = 'ffmpeg'
        probe = 'ffprobe'
    else:
        converter = 'avconv'
        probe = 'avprobe'
    encodecmd = [converter]  
    w = 0
    h = 0    
    for ii, vid in enumerate(filelist):
        probecmd = [probe, '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', vid]
        _op = subprocess.check_output(probecmd)
        _op = _op.decode(encoding='UTF-8').strip()
        _dict = json.loads(_op)
        _w = _dict['streams'][0]['width']
        _wscale = round_halfup(_w*scale)
        if _w > w:
            w = _w
        _h = _dict['streams'][0]['height']
        _hscale = round_halfup(_h*scale)
        if _h > h:
            h = _h
        #encodecmd.extend(['-i', shlex.quote(vid)])
        encodecmd.extend(['-i', vid])
    wscale = round_halfup(w*scale)
    hscale = round_halfup(h*scale)
    wtotal = wscale*len(filelist)
    htotal = hscale
    print(w, h)
    print(wtotal, htotal)
    #print(arglist1)
    filterstr1 = 'nullsrc=size={0:d}x{1:d} [base]; '.format(wtotal, htotal)
    for ii, vid in enumerate(filelist):
        filterstr1 = filterstr1 + \
        ' [{0:d}:v] setpts=PTS-STARTPTS, scale={1:d}x{2:d} [ipvid{0:d}]; '.format(ii, _wscale, _hscale)
        if ii==0:
            filterstr2 = ' [base][ipvid{0:d}] overlay=shortest=1'.format(ii)
        else:
            filterstr2 = filterstr2 + \
          ' [tmp{0:d}][ipvid{1:d}] overlay=shortest=1:x={2:d}'.format(ii-1, ii, wscale*ii)
        if ii < len(filelist)-1:  # add to filterstr2, except last item
            filterstr2 = filterstr2 + ' [tmp{0:d}];'.format(ii) 
    #filterstr2 = filterstr2[:-1]    # remove the last semi-colon
    #filterstr2 = filterstr2 + '"'
    encodecmd.extend(['-filter_complex', filterstr1+filterstr2, '-c:v', 'libx264', opfile])
    if dryrun:
        return ' '.join(encodecmd)
    _op = subprocess.check_output(encodecmd)
    _op = _op.decode(encoding='UTF-8').strip()
    return _op

def round_halfup(ip):
    op = decimal.Decimal(ip).quantize(1,rounding=decimal.ROUND_HALF_UP)
    return int(op)


def video_crop_join_row(filelist, opfile='output.mkv', scale=1, vidlib='ff',
                    dryrun=False, cropbbox=None):
    if vidlib.lower().startswith('ff'):
        converter = 'ffmpeg'
        probe = 'ffprobe'
    else:
        converter = 'avconv'
        probe = 'avprobe'
    encodecmd = [converter]  
    w = 0
    h = 0    
    for ii, vid in enumerate(filelist):
        probecmd = [probe, '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', vid]
        _op = subprocess.check_output(probecmd)
        _op = _op.decode(encoding='UTF-8').strip()
        _dict = json.loads(_op)
        _w = _dict['streams'][0]['width']
        _wscale = round_halfup(_w*scale)
        if _w > w:
            w = _w
        _h = _dict['streams'][0]['height']
        _hscale = round_halfup(_h*scale)
        if _h > h:
            h = _h
        #encodecmd.extend(['-i', shlex.quote(vid)])
        encodecmd.extend(['-i', vid])
    #wscale = round_halfup(w*scale)
    #hscale = round_halfup(h*scale)
    if not cropbbox:
        cropbbox = [0, 0, w, h]
    x1crop = round_halfup(cropbbox[0]*scale)
    y1crop = round_halfup(cropbbox[1]*scale)
    wcrop  = round_halfup((cropbbox[2]-cropbbox[0])*scale)
    hcrop  = round_halfup((cropbbox[3]-cropbbox[1])*scale)
    wtotal = wcrop*len(filelist)
    htotal = hcrop
    filterstr1 = 'nullsrc=size={0:d}x{1:d} [base]; '.format(wtotal, htotal)
    for ii, vid in enumerate(filelist):
        filterstr1 = filterstr1 + \
        ' [{ii:d}:v] setpts=PTS-STARTPTS, scale={ws:d}x{hs:d}, crop={wc:d}:{hc:d}:{x1crop:d}:{y1crop:d} [ipvid{ii:d}]; '.format(ii=ii, ws=_wscale, hs=_hscale, wc=wcrop, hc=hcrop, x1crop=x1crop, y1crop=y1crop)
        if ii==0:
            filterstr2 = ' [base][ipvid{0:d}] overlay=shortest=1'.format(ii)
        else:
            filterstr2 = filterstr2 + \
          ' [tmp{0:d}][ipvid{1:d}] overlay=shortest=1:x={2:d}'.format(ii-1, ii, wcrop*ii)  # wscale*ii
        if ii < len(filelist)-1:  # add to filterstr2, except last item
            filterstr2 = filterstr2 + ' [tmp{0:d}];'.format(ii) 
    encodecmd.extend(['-filter_complex', filterstr1+filterstr2, '-c:v', 'libx264', opfile])
    if dryrun:
        return ' '.join(encodecmd)
    _op = subprocess.check_output(encodecmd)
    _op = _op.decode(encoding='UTF-8').strip()
    return _op



if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    op_file = 'output.avi'
    if False:
        data_dir = '/home/develop/Downloads/MBES_data/18-F-2824 (SKL22)/VISUALWORKS/VisualworksReports/Projects/9821/DATA_201401091537060'
        filelist = [ os.path.join(data_dir, 'VIDEO_201401091537060@Stbd.mpg' ) ,
         os.path.join(data_dir, 'VIDEO_201401091537060@Centre.mpg' ) ,
         os.path.join(data_dir, 'VIDEO_201401091537060@Port.mpg' ) ]
        op = video_join_row(filelist, vidlib='ff', scale=0.25, dryrun=True)
        #print(_dict['streams'][0]['width'], _dict['streams'][0]['height'])
        print(op)
    if True:
        data_dir = '/media/develop/Windows/Users/Stephen/Documents/2011_survey/L51/2010-08-10_L51_as-laid_survey/DATA_20100810042322358'
        filelist = [ os.path.join(data_dir, '20100810042322650@HERC4_Ch3.mpg' ) ,
         os.path.join(data_dir, '20100810042322358@HERC4_Ch1.mpg' ) ,
         os.path.join(data_dir, '20100810042322741@HERC4_Ch2.mpg' ) ]
        op = video_crop_join_row(filelist, vidlib='ff', scale=0.25, dryrun=False, cropbbox=(20,125, 700,500))
        print(op)    
    #http://askubuntu.com/questions/59383/extract-part-of-a-video-with-a-one-line-command
    # ffmpeg -ss 00:00:00 -i output.mkv -t 00:00:20 -vcodec copy -an ttemp.mkv # tstartend=(0, 18, 35,52, 74, 98)
    # ffmpeg -ss 40 -i output.mkv -t 10 -vcodec copy -an ttemp.mkv
    #http://www.bogotobogo.com/FFMpeg/ffmpeg_seeking_ss_option_cutting_section_video_image.php
    
    
