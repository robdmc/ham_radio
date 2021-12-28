from neclib import Antenna
import numpy as np

ant = Antenna(nsegs=13, units='m')
ant.symbols(
    h_radial=.08,
    h_feed=.25,
    h_vert=10.2,
    rad=.016,
    l_radial=5,
    nsegs_el=11,
    nsegs_radial=9,
    sep=.25,

)
# Define feed
ant.wire([0, 0, 'h_radial'], [0, 0, 'h_feed'], rad='rad', nsegs=1, source_seg=1)

# Define separators
ant.wire(['-2*sep', 0, 'h_feed'], ['-sep', 0, 'h_feed'], rad='rad', nsegs=1)
ant.wire(['-sep', 0, 'h_feed'], [0, 0, 'h_feed'], rad='rad', nsegs=1)
ant.wire([0, 0, 'h_feed'], ['sep', 0, 'h_feed'], rad='rad', nsegs=1)
ant.wire(['sep', 0, 'h_feed'], ['2*sep', 0, 'h_feed'], rad='rad', nsegs=1)


# Define radiators

f = np.logspace(np.log10(1 / np.pi), np.log10(1), 5)
ant.wire(['-2*sep', 0, 'h_feed'], ['-2*sep', 0, f'h_feed + {f[0]}*h_vert'], rad='rad', nsegs='nsegs_el')
ant.wire(['-1*sep', 0, 'h_feed'], ['-1*sep', 0, f'h_feed + {f[1]}*h_vert'], rad='rad', nsegs='nsegs_el')
ant.wire(['-0*sep', 0, 'h_feed'], ['-0*sep', 0, f'h_feed + {f[2]}*h_vert'], rad='rad', nsegs='nsegs_el')
ant.wire(['1*sep', 0, 'h_feed'], ['1*sep', 0, f'h_feed + {f[3]}*h_vert'], rad='rad', nsegs='nsegs_el')
ant.wire(['2*sep', 0, 'h_feed'], ['2*sep', 0, f'h_feed + {f[4]}*h_vert'], rad='rad', nsegs='nsegs_el')

ant.wire(['-2*sep', 0, f'h_feed + {f[0]} * h_vert'], ['-1*sep', 0, f'h_feed + {f[1]}*h_vert'], rad='rad', nsegs=1)
ant.wire(['-1*sep', 0, f'h_feed + {f[1]} * h_vert'], ['-0*sep', 0, f'h_feed + {f[2]}*h_vert'], rad='rad', nsegs=1)
ant.wire(['0*sep', 0, f'h_feed + {f[2]} * h_vert'], ['1*sep', 0, f'h_feed + {f[3]}*h_vert'], rad='rad', nsegs=1)
ant.wire(['1*sep', 0, f'h_feed + {f[3]} * h_vert'], ['2*sep', 0, f'h_feed + {f[4]}*h_vert'], rad='rad', nsegs=1)




# Define radials
ant.radials(16, 'l_radial', origin=[0, 0, 'h_radial'], rad='rad', nsegs='nsegs_radial')

print(ant.write())
