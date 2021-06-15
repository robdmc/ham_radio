#!/usr/bin/python
# -*- encoding: utf-8; -*-
# Copyright 2016 © Hans Insulander <hans@codium.se>

import struct, sys, getopt, os

out = sys.stdout
def output(s):
    global out
    out.write(s)
    out.write(os.linesep)

def parse_planar_cut(descr, unit, data):
    output('planar cut: %s'%descr)
    title_len, env_len, notes_len, frequency, plane, plane_angle, symmetry, number_of_points, first_angle, angular_increment = struct.unpack('<BBHfBfBHff', data[0:24])
    data = data[24:]
    points = struct.unpack('f'*number_of_points, data[0:4*number_of_points])
    data = data[4*number_of_points:]
    title = data[0:title_len]
    data = data[title_len:]
    env = data[0:env_len]
    data = data[env_len:]
    notes = data[0:notes_len]
    data = data[notes_len:]
    output('  data len=%d'%len(data))
    output('  title_len=%d'%title_len)
    output('  env_len=%d'%env_len)
    output('  notes_len=%d'%notes_len)
    output('  frequency=%f'%frequency)
    output('  plane=%d'%plane)
    output('  plane_angle=%d'%plane_angle)
    output('  symmetry=%d'%symmetry)
    output('  number_of_points=%d'%number_of_points)
    output('  first_angle=%f'%first_angle)
    output('  angular_increment=%f'%angular_increment)
    output('  points len=%d'%len(points))
    output('  unit:%s'%unit)
    output('  points:%s'%', '.join(['%f'%p for p in points]))
    output('  title=|%s|'%title)
    output('  env=|%s|'%env)
    output('  notes=|%s|'%notes)
    output('  remaining data len=%d'%len(data))

def parse_absolute_field(descr, unit, data):
    output('absolute field: %s'%descr)

block_types = {
    0: ['No-Op', '', None],
    1: ['Total magnitude', 'dBi', parse_planar_cut],
    2: ['Horizontal magnitude', 'dBi', parse_planar_cut],
    3: ['Vertical magnitude', 'dBi', parse_planar_cut],
    4: ['Right-circular magnitude', 'dBic', parse_planar_cut],
    5: ['Left-circular magnitude', 'dBic', parse_planar_cut],
    6: ['Major-axis magnitude', 'dBi', parse_planar_cut],
    7: ['Minor-axis magnitude', 'dBi', parse_planar_cut],
    8: ['Ellipticity', 'dB', parse_planar_cut],
    9: ['Total phase', 'degrees', parse_planar_cut],
    10: ['Horizontal phase', 'degrees', parse_planar_cut],
    11: ['Vertical phase', 'degrees', parse_planar_cut],
    12: ['Right-circular phase', 'degrees', parse_planar_cut],
    13: ['Left-circular phase', 'degrees', parse_planar_cut],
    14: ['Major-axis phase', 'degrees', parse_planar_cut],
    15: ['Minor-axis phase', 'degrees', parse_planar_cut],
    16: ['Polarization tilt', 'degrees', parse_planar_cut],

    64: ['Power density', 'watts/square-meter', parse_absolute_field],
    65: ['Peak E magnitude', 'volts/meter', parse_absolute_field],
    66: ['Peak H magnitude', 'amps/meter', parse_absolute_field],
    67: ['Px Poynting vector', 'watts/square-meter', parse_absolute_field],
    68: ['Py Poynting vector', 'watts/square-meter', parse_absolute_field],
    69: ['Pz Poynting vector', 'watts/square-meter', parse_absolute_field],
    70: ['Ex magnitude', 'volts/meter', parse_absolute_field],
    71: ['Ey magnitude', 'volts/meter', parse_absolute_field],
    72: ['Ez magnitude', 'volts/meter', parse_absolute_field],
    73: ['Hx magnitude', 'amps/meter', parse_absolute_field],
    74: ['Hy magnitude', 'amps/meter', parse_absolute_field],
    75: ['Hz magnitude', 'amps/meter', parse_absolute_field],
    76: ['Ex phase', 'degrees', parse_absolute_field],
    77: ['Ey phase', 'degrees', parse_absolute_field],
    78: ['Ez phase', 'degrees', parse_absolute_field],
    79: ['Hx phase', 'degrees', parse_absolute_field],
    80: ['Hy phase', 'degrees', parse_absolute_field],
    81: ['Hz phase', 'degrees', parse_absolute_field],
    96: ['E(R) magnitude', 'volts/meter', parse_absolute_field],
    97: ['E(phi) magnitude', 'volts/meter', parse_absolute_field],
    98: ['E(theta) magnitude', 'volts/meter', parse_absolute_field],
    99: ['E(R) phase', 'degrees', parse_absolute_field],
    100: ['E(phi) phase', ' degrees', parse_absolute_field],
    101: ['E(theta) phase', ' degrees', parse_absolute_field],
}

def parse_block(data):
    type, length = struct.unpack('<BH', data[0:3])
    descr, unit, handler = block_types.get(type, ['unknown', '', None])
    output('block type=%d (%s) length=%d'%(type, descr, length))
    if handler:
        handler(descr, unit, data[3:length])
    return length

def parse_header(data):
    version, header_len, source_len, title_len, env_len, notes_len = struct.unpack('<BHBBBH', data[0:8])
    data = data[8:]

    source = data[0:source_len]
    data = data[source_len:]

    title = data[0:title_len]
    data = data[title_len:]

    env = data[0:env_len]
    data = data[env_len:]

    notes = data[0:notes_len]
    data = data[notes_len:]

    output('version=%d.%d'%(version >> 4, version&0xf))
    output('header len=%d (%d)'%(header_len, source_len+title_len+env_len+notes_len))
    output('source len=%d'%source_len)
    output('source=|%s|'%source)
    output('title len=%d'%title_len)
    output('title=|%s|'%title)
    output('env len=%d'%env_len)
    output('env=|%s|'%env)
    output('notes len=%d'%notes_len)
    output('notes=|%s|'%notes)

    return header_len

def parse(data):
    n = parse_header(data)
    data = data[n:]
    while len(data) > 0:
        n = parse_block(data)
        data = data[n:]

HELP = "Usage: python %s [-o <outfile>] <infile>" % sys.argv[0]
def main(argv):
    global out
    try:
        opts, args = getopt.getopt(argv[1:], "ho:", [])

        for opt, arg in opts:
            if opt == '-h':
                print HELP
                sys.exit(0)
            elif opt == '-o':
                out = open(arg, 'w')

        with open(args[0], 'rb') as f:
            data = f.read()
            parse(data)
    except getopt.GetoptError:
        print HELP

if __name__ == '__main__':
    sys.exit(main(sys.argv))
