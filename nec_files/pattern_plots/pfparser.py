#! /usr/bin/env python
# -*- encoding: utf-8; -*-
# Copyright 2016 © Hans Insulander <hans@codium.se>

import os
import sys
import getopt
import struct
import click

out = sys.stdout


# def output(s):
#     global out
#     out.write(s)
#     out.write(os.linesep)


# def parse_planar_cut(descr, unit, data):
#     output('planar cut: %s' % descr)
#     (
#         title_len,
#         env_len,
#         notes_len,
#         frequency,
#         plane,
#         plane_angle,
#         symmetry,
#         number_of_points,
#         first_angle,
#         angular_increment
#     ) = struct.unpack('<BBHfBfBHff', data[0:24])
#     data = data[24:]
#     points = struct.unpack('f' * number_of_points, data[0:4 * number_of_points])
#     data = data[4 * number_of_points:]
#     title = data[0:title_len]
#     data = data[title_len:]
#     env = data[0:env_len]
#     data = data[env_len:]
#     notes = data[0:notes_len]
#     data = data[notes_len:]
#     output('  data len=%d' % len(data))
#     output('  title_len=%d' % title_len)
#     output('  env_len=%d' % env_len)
#     output('  notes_len=%d' % notes_len)
#     output('  frequency=%f' % frequency)
#     output('  plane=%d' % plane)
#     output('  plane_angle=%d' % plane_angle)
#     output('  symmetry=%d' % symmetry)
#     output('  number_of_points=%d' % number_of_points)
#     output('  first_angle=%f' % first_angle)
#     output('  angular_increment=%f' % angular_increment)
#     output('  points len=%d' % len(points))
#     output('  unit:%s' % unit)
#     output('  points:%s' % ', '.join(['%f' % p for p in points]))
#     output('  title=|%s|' % title)
#     output('  env=|%s|' % env)
#     output('  notes=|%s|' % notes)
#     output('  remaining data len=%d' % len(data))


# def parse_absolute_field(descr, unit, data):
#     output('absolute field: %s' % descr)


# BLOCK_TYPES = {
#     0: ['No-Op', '', None],
#     1: ['Total magnitude', 'dBi', parse_planar_cut],
#     2: ['Horizontal magnitude', 'dBi', parse_planar_cut],
#     3: ['Vertical magnitude', 'dBi', parse_planar_cut],
#     4: ['Right-circular magnitude', 'dBic', parse_planar_cut],
#     5: ['Left-circular magnitude', 'dBic', parse_planar_cut],
#     6: ['Major-axis magnitude', 'dBi', parse_planar_cut],
#     7: ['Minor-axis magnitude', 'dBi', parse_planar_cut],
#     8: ['Ellipticity', 'dB', parse_planar_cut],
#     9: ['Total phase', 'degrees', parse_planar_cut],
#     10: ['Horizontal phase', 'degrees', parse_planar_cut],
#     11: ['Vertical phase', 'degrees', parse_planar_cut],
#     12: ['Right-circular phase', 'degrees', parse_planar_cut],
#     13: ['Left-circular phase', 'degrees', parse_planar_cut],
#     14: ['Major-axis phase', 'degrees', parse_planar_cut],
#     15: ['Minor-axis phase', 'degrees', parse_planar_cut],
#     16: ['Polarization tilt', 'degrees', parse_planar_cut],

#     64: ['Power density', 'watts/square-meter', parse_absolute_field],
#     65: ['Peak E magnitude', 'volts/meter', parse_absolute_field],
#     66: ['Peak H magnitude', 'amps/meter', parse_absolute_field],
#     67: ['Px Poynting vector', 'watts/square-meter', parse_absolute_field],
#     68: ['Py Poynting vector', 'watts/square-meter', parse_absolute_field],
#     69: ['Pz Poynting vector', 'watts/square-meter', parse_absolute_field],
#     70: ['Ex magnitude', 'volts/meter', parse_absolute_field],
#     71: ['Ey magnitude', 'volts/meter', parse_absolute_field],
#     72: ['Ez magnitude', 'volts/meter', parse_absolute_field],
#     73: ['Hx magnitude', 'amps/meter', parse_absolute_field],
#     74: ['Hy magnitude', 'amps/meter', parse_absolute_field],
#     75: ['Hz magnitude', 'amps/meter', parse_absolute_field],
#     76: ['Ex phase', 'degrees', parse_absolute_field],
#     77: ['Ey phase', 'degrees', parse_absolute_field],
#     78: ['Ez phase', 'degrees', parse_absolute_field],
#     79: ['Hx phase', 'degrees', parse_absolute_field],
#     80: ['Hy phase', 'degrees', parse_absolute_field],
#     81: ['Hz phase', 'degrees', parse_absolute_field],
#     96: ['E(R) magnitude', 'volts/meter', parse_absolute_field],
#     97: ['E(phi) magnitude', 'volts/meter', parse_absolute_field],
#     98: ['E(theta) magnitude', 'volts/meter', parse_absolute_field],
#     99: ['E(R) phase', 'degrees', parse_absolute_field],
#     100: ['E(phi) phase', ' degrees', parse_absolute_field],
#     101: ['E(theta) phase', ' degrees', parse_absolute_field],
# }


# # def parse_block(data):
# #     type, length = struct.unpack('<BH', data[0:3])
# #     descr, unit, handler = block_types.get(type, ['unknown', '', None])
# #     output('block type=%d (%s) length=%d' % (type, descr, length))
# #     if handler:
# #         handler(descr, unit, data[3:length])
# #     return length


# def parse_header(data):
#     version, header_len, source_len, title_len, env_len, notes_len = struct.unpack('<BHBBBH', data[0:8])
#     data = data[8:]

#     source = data[0:source_len]
#     data = data[source_len:]

#     title = data[0:title_len]
#     data = data[title_len:]

#     env = data[0:env_len]
#     data = data[env_len:]

#     notes = data[0:notes_len]
#     data = data[notes_len:]

#     output('version=%d.%d' % (version >> 4, version & 0xf))
#     output('header len=%d (%d)' % (header_len, source_len + title_len + env_len + notes_len))
#     output('source len=%d' % source_len)
#     output('source=|%s|' % source)
#     output('title len=%d' % title_len)
#     output('title=|%s|' % title)
#     output('env len=%d' % env_len)
#     output('env=|%s|' % env)
#     output('notes len=%d' % notes_len)
#     output('notes=|%s|' % notes)

#     return header_len


# def parse_block(data):
#     block_type, length = struct.unpack('<BH', data[0:3])
#     descr, unit, handler = block_types.get(block_type, ['unknown', '', None])
#     output('block type=%d (%s) length=%d' % (block_type, descr, length))
#     if handler:
#         handler(descr, unit, data[3:length])
#     return length



# def parse(data):
#     n = parse_header(data)
#     data = data[n:]
#     while len(data) > 0:
#         n = parse_block(data)
#         data = data[n:]

# class Header:
#     def __init__(self):
#         pass

#     def load(self, data):
#         version, header_len, source_len, title_len, env_len, notes_len = struct.unpack('<BHBBBH', data[0:8])
#         data = data[8:]

#         source = data[0:source_len]
#         data = data[source_len:]

#         title = data[0:title_len]
#         data = data[title_len:]

#         env = data[0:env_len]
#         data = data[env_len:]

#         notes = data[0:notes_len]
#         data = data[notes_len:]

#         output('version=%d.%d' % (version >> 4, version & 0xf))
#         output('header len=%d (%d)' % (header_len, source_len + title_len + env_len + notes_len))
#         output('source len=%d' % source_len)
#         output('source=|%s|' % source)
#         output('title len=%d' % title_len)
#         output('title=|%s|' % title)
#         output('env len=%d' % env_len)
#         output('env=|%s|' % env)
#         output('notes len=%d' % notes_len)
#         output('notes=|%s|' % notes)

#         return header_len


# class Blocks:
#     def __init__(self):
#         self.block_list = []

#     def load(self, data):
#         remaining_len = parse_header(data)
#         data = data[n:]
#         while len(data) > 0:
#             n = parse_block(data)
#             data = data[n:]


# def load(file_name):
#     with open(file_name, 'rb') as buff:
#         data = buff.read()
#         print(len(data))


class Extractor:
    def __init__(self, data, marker=0):
        self.data = data
        self.marker = marker

    def read_bytes(self, size):
        start, end = self.marker, self.marker + size
        self.marker = end
        return self.data[start:end]

    def read_string(self, size):
        blob = self.read_bytes(size)
        return blob.decode('utf-8')


class Meta:

    def __str__(self):
        return str(self.__dict__)


    def __repr__(self):
        return self.__str__()

    def __get__(self, obj, cls):
        self.obj = obj
        data = obj.data
        marker = 8
        version, header_len, source_len, title_len, env_len, notes_len = struct.unpack('<BHBBBH', data[0:marker])


        setattr(self, 'version', version)
        setattr(self, 'header_len', header_len)
        setattr(self, 'source_len', source_len)
        setattr(self, 'title_len', title_len)
        setattr(self, 'env_len', env_len)
        setattr(self, 'notes_len', notes_len)

        extractor = Extractor(data, marker=marker)

        setattr(self, 'source', extractor.read_string(source_len))
        setattr(self, 'title', extractor.read_string(title_len))
        setattr(self, 'environment', extractor.read_string(env_len))
        setattr(self, 'notes', extractor.read_string(notes_len))


        return self



def get_string(data, start, size):
    return data[start: start + size].decode('utf-8') 















class PF:
    meta = Meta()
    def __init__(self, data):
        self.data = data



    # data = data[8:]

    # source = data[0:source_len]
    # data = data[source_len:]

    # title = data[0:title_len]
    # data = data[title_len:]

    # env = data[0:env_len]
    # data = data[env_len:]

    # notes = data[0:notes_len]
    # data = data[notes_len:]

    # output('version=%d.%d' % (version >> 4, version & 0xf))
    # output('header len=%d (%d)' % (header_len, source_len + title_len + env_len + notes_len))
    # output('source len=%d' % source_len)
    # output('source=|%s|' % source)
    # output('title len=%d' % title_len)
    # output('title=|%s|' % title)
    # output('env len=%d' % env_len)
    # output('env=|%s|' % env)
    # output('notes len=%d' % notes_len)
    # output('notes=|%s|' % notes)

    # return header_len




@click.command()
@click.option('-i', '--input-file', required=True)
def main(input_file):
    with open(input_file, 'rb') as buff:
        data = buff.read()
        pf = PF(data)
        print(pf.meta)



if __name__ == '__main__':
    main()
