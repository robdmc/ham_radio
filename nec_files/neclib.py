import attr

@attr.s
class Wire:
    starting = attr.ib(converter=lambda v: [str(e) for e in v])
    ending = attr.ib(converter=lambda v: [str(e) for e in v])
    tag = attr.ib(default=None, converter=str)
    dia = attr.ib(default=None, converter=str)
    nsegs = attr.ib(default=None, converter=str)
    source_seg = attr.ib(default=None, converter=str)
    conductivity = attr.ib(default=58000000, converter=str)

    def write_wire(self):
        out = 'GW\t'
        out += '\t'.join([
            self.tag,
            self.nsegs,
            self.starting[0],
            self.starting[1],
            self.starting[2],
            self.ending[0],
            self.ending[1],
            self.ending[2],
            self.dia,
        ])
        return out

    def write_load(self):
        out = f'LD\t5\t{self.tag}\t1\t{self.nsegs}\t{self.conductivity}'
        return out

    def write_excitation(self):
        out = ''
        if self.source_seg != 'None':
            out = f'EX\t0\t{self.tag}\t{self.source_seg}\t0\t0'
        return out




@attr.s
class Antenna:
    dia = attr.ib(default=.001628, converter=str)
    nsegs = attr.ib(default=13)
    freq_mhz = attr.ib(default=7.15)
    symbols_dict = attr.ib(factory=lambda: {})
    wires_list = attr.ib(factory=lambda: [])
    units = attr.ib(default='meters')

    @property
    def scale(self):
        m = 1
        ft = 0.3048
        return {
            'm': m,
            'meters': m,
            'meter': m,
            'ft': ft,
            'foot': ft,
            'feet': ft,
        }[self.units]


    def symbols(self, **kwargs):
        self.symbols_dict.update(kwargs)

    def wire(self, starting, ending, dia=None, nsegs=None, source_seg=None):
        nsegs = self.nsegs if nsegs is None else nsegs
        dia = self.dia if dia is None else dia
        tag = str(len(self.wires_list) + 1)
        self.wires_list.append(Wire(starting, ending, tag, dia, nsegs, source_seg))

    def radials(self, number, height, length, origin=None, dia=None, nsegs=None):
        pass

    def _write_symbols(self):
        return '\n'.join(f'SY {k}={v}' for (k, v) in self.symbols_dict.items())

    def _write_wires(self):
        return '\n'.join(w.write_wire() for w in self.wires_list)

    def _write_loads(self):
        return '\n'.join(w.write_load() for w in self.wires_list)

    def _write_scale(self):
        return f'GS\t0\t0\t{self.scale}'

    def _write_done_geometry(self):
        return 'GE\t1'

    def _write_ground(self):
        return 'GN\t2\t0\t0\t0\t13\t0.005'

    def _write_kernel(self):
        return 'EK'

    def _write_excitations(self):
        out = '\n'.join(w.write_excitation() for w in self.wires_list)
        out = out.strip()
        return out

    def _write_frequency(self):
        return f'FR\t0\t0\t0\t0\t{self.freq_mhz}\t0'

    def _write_end_run(self):
        return 'EN'

    def write(self):
        out = 'CM\nCE\n'
        out += '\n'.join([
            self._write_symbols(),
            self._write_wires(),
            self._write_scale(),
            self._write_done_geometry(),
            self._write_loads(),
            self._write_ground(),
            self._write_kernel(),
            self._write_excitations(),
            self._write_frequency(),
            self._write_end_run(),
        ])
        return out

    def radials(self, number, length, origin=None, dia=None, nsegs=None):
        import math
        if origin is None:
            origin = [0, 0, 0]

        if nsegs is None:
            nsegs = self.nsegs

        radials = []
        d_theta = 2 * math.pi / number
        for nn in range(number):
            theta = nn * d_theta
            x = round(origin[0] + length * math.cos(theta), 3)
            y = round(origin[1] + length * math.sin(theta), 3)
            z = origin[2]
            self.wire(starting=origin, ending=[x, y, z], nsegs=nsegs)


if __name__ == '__main__':
    ant = Antenna(units='m')
    ant.symbols(
        h=10,
        dia=.001
    )
    ant.wire([0, 0, 0], [0, 0, 'h'], source_seg=1, dia='dia')
    ant.wire([0, 0, 'h'], [0, 0, '2*h'], dia='dia')
    ant.radials(32, 10)

    print(ant.write())
