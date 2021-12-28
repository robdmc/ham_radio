from neclib import Antenna

ant = Antenna(nsegs=13, units='m')
ant.symbols(
    h_radial=.08,
    h_feed=.25,
    h_vert_left=10.2,
    h_vert_right=5.2,
    rad=.016,
    l_radial=5,
    nsegs_el=11,
    nsegs_radial=9,
    sep=.25,

)
# Define feed
ant.wire([0, 0, 'h_radial'], [0, 0, 'h_feed'], rad='rad', nsegs=1, source_seg=1)

# Define separators
ant.wire(['-sep', 0, 'h_feed'], [0, 0, 'h_feed'], rad='rad', nsegs=1)
ant.wire([0, 0, 'h_feed'], ['sep', 0, 'h_feed'], rad='rad', nsegs=1)

# Define radiators
ant.wire(['-sep', 0, 'h_feed'], ['-sep', 0, 'h_feed + h_vert_left'], rad='rad', nsegs='nsegs_el')
ant.wire(['sep', 0, 'h_feed'], ['sep', 0, 'h_feed + h_vert_right'], rad='rad', nsegs='nsegs_el')

# Define radials
ant.radials(16, 'l_radial', origin=[0, 0, 'h_radial'], rad='rad', nsegs='nsegs_radial')

print(ant.write())
