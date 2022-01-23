from neclib import Antenna

ant = Antenna(nsegs=13, units='m')
h_feed = .25
ant.symbols(
    h_radial=.08,
    h_feed=h_feed,
    h_vert_40=10.2-h_feed,
    h_vert_30=6.74-h_feed,
    h_vert_20=5.2-h_feed,
    h_vert_17=3.83-h_feed,
    rad=.016,
    l_radial=5,
    nsegs_el=11,
    nsegs_radial=9,
    sep=.25,

)

# See: https://www.m0mcx.co.uk/wp-content/uploads/10mABV-User-guide.pdf

# Define feed
ant.wire([0, 0, 'h_radial'], [0, 0, 'h_feed'], rad='rad', nsegs=1, source_seg=1)

# Define separators
ant.wire(['-2 * sep', 0, 'h_feed'], ['-sep',    0, 'h_feed'], rad='rad', nsegs=1)
ant.wire(['-sep',     0, 'h_feed'], [0,         0, 'h_feed'], rad='rad', nsegs=1)
ant.wire([0,          0, 'h_feed'], ['sep',     0, 'h_feed'], rad='rad', nsegs=1)
ant.wire(['sep',      0, 'h_feed'], ['2 * sep', 0, 'h_feed'], rad='rad', nsegs=1)

# Define radiators
ant.wire(['-2 * sep', 0, 'h_feed'], ['-2 * sep', 0, 'h_feed + h_vert_40'], rad='rad', nsegs='nsegs_el')
ant.wire(['-sep',     0, 'h_feed'], [    '-sep', 0, 'h_feed + h_vert_30'], rad='rad', nsegs='nsegs_el')
ant.wire(['sep',      0, 'h_feed'], [     'sep', 0, 'h_feed + h_vert_20'], rad='rad', nsegs='nsegs_el')
ant.wire(['2 * sep',  0, 'h_feed'], [ '2 * sep', 0, 'h_feed + h_vert_17'], rad='rad', nsegs='nsegs_el')

# Define radials
ant.radials(16, 'l_radial', origin=[0, 0, 'h_radial'], rad='rad', nsegs='nsegs_radial')

print(ant.write())
