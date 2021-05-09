"""
This file was modified from
https://fornax.phys.unm.edu/lwa/subversion/branches/lwa_user/lwa_user/nec_util.py
"""


import numpy as np
import pandas as pd
import os
import re
import logging


_NEC_UTIL_LOG = logging.getLogger('nec_util')
_NEC_UTIL_LOG.setLevel(logging.INFO)


class NECImpedance:
    '''NECImpedance:
    Python class to read an array of impedance values from a NEC2 .out file
    The .nec file should loop over a range of frequencies with an FR card
    like this:
    FR 0 91 0 0 10.0 1.0
    The RP card should be minimal to keep the runtime and output file sizefrom growing huge.  For example.
    RP 0,91,1,1000,0.,0.,1.0,1.0
    '''
    def __init__(self, necname):
        outname = os.path.splitext(necname)[0] + '.out'
        f = open(outname)
        # Start at beginning of file
        f.seek(0)
        # skip all lines until a line containing "STRUCTURE SPECIFICATION": this
        # effectively skips all comments (from CM cards) and text resulting from
        # reading Numerical Green's Function parts. Of course, if a user writes
        # "STRUCTURE SPECIFICATION" in his comment lines, this still fails...
        for line in f:
            if line.find('STRUCTURE SPECIFICATION') >= 0:
                break
        else:
            raise RuntimeError("STRUCTURE SPECIFICATION not found!")

        freqs = []
        impedances = []
        while (True):
            #  Now look for FREQUENCY and get the value
            for line in f:
                if line.find('FREQUENCY') >= 0:
                    break
            for line in f:
                _NEC_UTIL_LOG.debug(line.strip())
                if line.find('FREQUENCY=') >= 0:
                    freq = float(line[line.find('=') + 1:].split()[0])
                    break
                if line.find('FREQUENCY :') >= 0:
                    freq = float(line[line.find(':') + 1:].split()[0])
                    break
            else:
                _NEC_UTIL_LOG.debug("No more freqs...")
                break
            _NEC_UTIL_LOG.debug("Found frequency %f MHz", freq)
            for line in f:
                if line.find('ANTENNA INPUT PARAMETERS') >= 0:
                    break
            gotimp = False
            for line in f:
                if line.find('IMPEDANCE') >= 0:
                    gotimp = True
                    break
            if not gotimp:
                raise RuntimeError("IMPEDANCE not found")
            for line in f:
                break
            for line in f:
                _NEC_UTIL_LOG.debug(line.strip())
                break
            # Here we need to add a space before - signs that
            # are not preceeded by an E, so it will parse
            line = re.sub(r'(\d)-', r'\1 -', line)
            re_z = float(line.split()[6])
            im_z = float(line.split()[7])
            freqs.append(freq)
            impedances.append(complex(re_z, im_z))

        self.freqs = np.array(freqs)
        self.z = np.array(impedances)

    @property
    def df(self):
        df = pd.DataFrame({'f': self.freqs, 'r': np.real(self.z), 'x': np.imag(self.z)})
        df = df.drop_duplicates('f', keep='last')
        df = df.sort_values(by='f').reset_index(drop=True)
        return df
