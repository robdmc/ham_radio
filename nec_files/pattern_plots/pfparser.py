#! /usr/bin/env python
# -*- encoding: utf-8; -*-
# Copyright 2016 © Hans Insulander <hans@codium.se>

import os
import sys
import getopt
import struct
import click
import numpy as np
import pandas as pd
import easier as ezr


class Block:
    LOOKUP = {
        0: 'No-Op',
        1: 'Total magnitude',
        2: 'Horizontal magnitude',
        3: 'Vertical magnitude',
        4: 'Right-circular magnitude',
        5: 'Left-circular magnitude',
        6: 'Major-axis magnitude',
        7: 'Minor-axis magnitude',
        8: 'Ellipticity',
        9: 'Total phase',
        10: 'Horizontal phase',
        11: 'Vertical phase',
        12: 'Right-circular phase',
        13: 'Left-circular phase',
        14: 'Major-axis phase',
        15: 'Minor-axis phase',
        16: 'Polarization tilt',
    }
    block_type = None
    block_len = None
    title_len = None
    environment_len = None
    notes_len = None
    freq = None
    plane = None
    plane_angle = None
    symmetry = None
    num_points = None
    first_angle = None
    angle_delta = None
    points = None
    title = None
    environment = None
    notes = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return f'Block({self.LOOKUP[self.block_type]} theta={self.plane_angle})'

    @property
    def quantity(self):
        return self.LOOKUP[self.block_type]
       
    def __repr__(self):
        return self.__str__()

    @property
    def az_angles(self):
        return self.first_angle + self.angle_delta * np.arange(self.num_points)



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

    def read_byte(self):
        marker = self.marker
        self.marker += 1
        return  struct.unpack('<B', self.data[marker:marker + 1])[0]

    def read_word(self):
        marker = self.marker
        self.marker += 2
        return  struct.unpack('<H', self.data[marker:marker + 2])[0]
        # return int.from_bytes(self.data[marker:marker + 2], 'little')

    def read_float(self):
        marker = self.marker
        self.marker += 4
        return  struct.unpack('<f', self.data[marker:marker + 4])[0]

    def read_numpy(self, dtype, num_points):
        marker = self.marker
        self.marker += 4 * num_points
        return np.frombuffer(self.data, dtype=dtype, count=num_points, offset=marker)

    def read_block(self):
        kwargs = {}
        kwargs['block_type'] = self.read_byte()
        if kwargs['block_type'] != 0:
            kwargs['block_len'] = self.read_word()
            kwargs['title_len'] = self.read_byte()
            kwargs['environment_len'] = self.read_byte()
            kwargs['notes_len'] = self.read_word()
            kwargs['freq'] = self.read_float()
            kwargs['plane'] = self.read_byte()
            kwargs['plane_angle'] = self.read_float()
            kwargs['symmetry'] = self.read_byte()
            kwargs['num_points'] = self.read_word()
            kwargs['first_angle'] = self.read_float()
            kwargs['angle_delta'] = self.read_float()
            kwargs['points'] = self.read_numpy(np.float32, kwargs['num_points'])
            kwargs['title'] = self.read_string(kwargs['title_len'])
            kwargs['environment'] = self.read_string(kwargs['environment_len'])
            kwargs['notes'] = self.read_string(kwargs['notes_len'])

        return Block(**kwargs)

    def read_blocks(self):
        block_list = []
        while self.marker < len(self.data):
            block_list.append(self.read_block())

        return block_list


class Meta:

    def __str__(self):
        return str(self.__dict__)


    def __repr__(self):
        return self.__str__()

    def __get__(self, obj, cls):
        self.obj = obj
        data = obj.data
        marker = 8
        data_size = len(data)
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



        self.blocks = extractor.read_blocks()
        return self

class PF:
    meta = Meta()
    def __init__(self, data):
        self.data = data

    @ezr.cached_container
    def df(self):
        df_list = []

        for block in self.meta.blocks:
            df = pd.DataFrame(dict(
                phi=block.az_angles,
                value=block.points
            ))
            df['freq'] = block.freq
            df['quantity'] = ezr.slugify(block.quantity)
            df['theta'] = block.plane_angle
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True, sort=False)

        df = df[[
            'quantity',
            'theta',
            'phi',
            'value',
            'freq',
        ]]
        return df



    


@click.command()
@click.option('-i', '--input-file', required=True)
def main(input_file):
    with open(input_file, 'rb') as buff:
        data = buff.read()
        pf = PF(data)

    df = pf.df
    print(df.head().to_string())
    print(df.quantity.value_counts())



if __name__ == '__main__':
    main()
