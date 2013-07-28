#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Copyright 2013 Alexandre Bulté <alexandre[at]bulte[dot]net>
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import gpxpy
import gpxpy.gpx
import requests
import math
import pickle
import hashlib
import os

ge_params = {
    'sensor': 'false',
    'path': '',
    'samples': 0
}

GE_API_ENDPOINT = 'http://maps.googleapis.com/maps/api/elevation/json'
GE_URL = '%s?sensor=%s&path=' % (GE_API_ENDPOINT, ge_params['sensor'])

def _get_points(gpx):
    for track in gpx.tracks:
        for segment in track.segments:
            return segment.points
    return []

def _get_data(points, url):
    for point in points:
        url += '%s,%s' % (point.latitude, point.longitude)
        # %7C is |
        url += "%7C"
    # remove last pipe
    url = url[:-3]
    url += '&samples=%s' % len(points)
    r = requests.get(url)
    if r.status_code != 200:
        return '/!\ Something bad happened when requesting GE : %s' % r.text, 'KO'
    res = r.json()
    return res['results']


def _res(line):
    return line + '\n'

def make_profile(gpx_file, width=80):
    gpx_md5 = hashlib.md5(gpx_file.read()).hexdigest()
    gpx_file.seek(0)

    points = _get_points(gpxpy.parse(gpx_file))
    if len(points) == 0:
        return '/!\ No points', 'KO'


    if not os.path.isfile('%s.pkl' % gpx_md5):
        # limit is 2048 chars - 13 for &samples=XXX
        # a couple of lat long is 19 char max. Pipe adds 3 char.
        # calculate number of points that can be encoded
        available_size = 2048 - 13 - len(GE_URL)
        available_points = math.trunc(available_size/(19+3))
        nb_loop_needed = int(math.ceil(float(len(points)) / available_points))

        results = []
        start = 0
        stop = available_points
        for i in range(nb_loop_needed):
            # print "calling for %s..%s" % (start, stop)
            results += _get_data(points[start:stop], GE_URL)
            start = stop
            stop += available_points
        output = open('%s.pkl' % gpx_md5, 'wb')
        pickle.dump(results, output, 0)
        output.close()
    else:
        pinput = open('%s.pkl' % gpx_md5, 'r')
        results = pickle.load(pinput)
        pinput.close()

    elevations = [round(r.get('elevation'), 2) for r in results]
    emin = min(elevations)
    emax = max(elevations)

    res = ''
    res += _res("MIN : %s" % emin)
    res += _res("MAX : %s" % emax)
    res += _res("TOTAL : %s" % (emax - emin))

    d_pos = d_neg = 0
    alt_prev = elevations[0]
    for e in elevations:
        if e - alt_prev > 0:
            d_pos += (e - alt_prev)
        elif e - alt_prev < 0:
            d_neg += (e - alt_prev)
        alt_prev = e

    res += _res("POSITIF CUM. : %s" % d_pos)
    res += _res("NEGATIF CUM. : %s" % d_neg)

    # get a sampling for chart
    # take average elevation for one split ?
    # chart is 80* large max et 50* high max
    # -5 is for altitude show (4 figures + space)
    if not isinstance(width, int):
        width = 80
    HEIGHT = 50
    if len(results) > (width-5):
        split_size = len(results) / (width-5)
    else:
        split_size = 1
    scale = emax / HEIGHT

    res += _res('One * is %s meters.' % scale)
    scaled_means = []
    for i in xrange(0, len(elevations), split_size):
        if i + split_size <= len(elevations):
            mean = sum(elevations[i:i+split_size]) / float(split_size)
        else:
            mean = sum(elevations[i:len(elevations)]) / float(len(elevations) - i)
        scaled_means.append(int(mean/scale))

    matrix = []
    first_line = [('%s'%int(x * scale)).ljust(5) for x in range(HEIGHT)]
    matrix.append(first_line)

    for sm in scaled_means:
        line = []
        for x in range(HEIGHT):
            if x <= sm:
                line.append('*')
            else:
                line.append(' ')
        matrix.append(line)

    # turn rows into columns and reverse
    nmatrix = zip(*matrix)
    nmatrix.reverse()

    for m in nmatrix:
        res += _res(''.join(m))

    return res, 'OK'

if __name__ == '__main__':
    # gpx_file = open('/Users/alexandre/Dropbox/_Home_/Cartes et circuits/boucle-vtt.gpx', 'r')
    gpx_file = open('/Users/alexandre/Dropbox/_Home_/Cartes et circuits/Circuits/Montagne/exp_Jausiers Larche 1-3 VTT.gpx', 'r')
    # gpx_file = open('/Users/alexandre/Dropbox/_Home_/Cartes et circuits/Circuits/CAP/trail-corn-16k.gpx', 'r')
    res, status = make_profile(gpx_file)
    print res
