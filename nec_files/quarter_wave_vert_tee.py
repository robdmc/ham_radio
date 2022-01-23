from neclib import Antenna
import numpy as np


ant = Antenna(nsegs=13, units='m')
ant.symbols(
    lam=40,
    h_radial=.08,
    h_vert='lam / 8',
    h_tee='lam / 8',
    l_tee1='lam / 16',
    l_tee2='lam / 16',
    rad=.016,
    l_radial=5,
    nsegs_vert=11,
    nsegs_radial=9,
    nsegs_tee=9,
)


# Define vertical
f = np.logspace(np.log10(1 / np.pi), np.log10(1), 5)
ant.wire([0, 0, 'h_radial'], [0, 0, f'h_radial + h_tee'], rad='rad', nsegs='nsegs_vert', source_seg=1)
ant.wire([0, 0, 'h_radial + h_tee'], [0, 0, f'h_radial + h_tee + h_vert'], rad='rad', nsegs='nsegs_vert')

# Define tee
ant.wire([0, 0, 'h_radial + h_tee'], [0, '-l_tee1', f'h_radial + h_tee'], rad='rad', nsegs='nsegs_tee')
ant.wire([0, 0, 'h_radial + h_tee'], [0, 'l_tee2', f'h_radial + h_tee'], rad='rad', nsegs='nsegs_tee')


# Define radials
ant.radials(16, 'l_radial', origin=[0, 0, 'h_radial'], rad='rad', nsegs='nsegs_radial')

print(ant.write())
