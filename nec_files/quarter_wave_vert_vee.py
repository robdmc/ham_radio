from neclib import Antenna
import numpy as np


ant = Antenna(nsegs=13, units='m')
ant.symbols(
    sep=1,
    h_radial=.08,
    h_feed = .18,
    h_vert1=10,
    h_vert2=5,
    rad=.016,
    l_radial=5,
    nsegs_vert=11,
    nsegs_radial=9,
)


# Define vertical
f = np.logspace(np.log10(1 / np.pi), np.log10(1), 5)
ant.wire([0, 0, 'h_radial'], [0, 0 , f'h_feed'], rad='rad', nsegs=1, source_seg=1)
ant.wire([0, 0, 'h_feed'], [0, 'sep', f'h_feed + h_vert1'], rad='rad', nsegs='nsegs_vert')
ant.wire([0, 0, 'h_feed'], [0, '-sep', f'h_feed + h_vert2'], rad='rad', nsegs='nsegs_vert')

# # Define tee
# ant.wire([0, 0, 'h_radial + h_tee'], [0, '-l_tee1', f'h_radial + h_tee'], rad='rad', nsegs='nsegs_tee')
# ant.wire([0, 0, 'h_radial + h_tee'], [0, 'l_tee2', f'h_radial + h_tee'], rad='rad', nsegs='nsegs_tee')


# Define radials
ant.radials(16, 'l_radial', origin=[0, 0, 'h_radial'], rad='rad', nsegs='nsegs_radial')

print(ant.write())
