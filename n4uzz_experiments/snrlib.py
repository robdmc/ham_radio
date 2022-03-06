import asyncio

import easier as ezr
import pandas as pd
import numpy as np
from aiohttp import ClientSession
from aiochclient import ChClient


class WSPR(ezr.pickle_cache_mixin):
    pkc = ezr.pickle_cache_state('active')

    def __init__(self, starting='12/1/2021', ending='1/1/2040', callsign_rex=r'N4UZZ.*'):
        """
        Times are in UTC.  defaults to grabbing all records that match callsign regex
        """
        starting = str(pd.Timestamp(starting).date())
        ending = str(pd.Timestamp(ending).date())

        self.query = f"""
            SELECT
                *
            FROM
                wspr.rx
            WHERE
                time >='{starting}'
            AND
                time <='{ending}'
            AND
                match(rx_sign, '{callsign_rex}')
        """

    async def _get_frame_from_db(self):
        s = ClientSession()
        client = ChClient(s, url="https://db1.wspr.live")
        if not await client.is_alive():
            raise RuntimeError("database conneciton failed!")

        all_rows = await client.fetch(self.query)
        df = pd.DataFrame(all_rows)
        await client.close()
        await s.close()
        return df

    @ezr.pickle_cached_container()
    def df_raw(self):
        return asyncio.run(self._get_frame_from_db())

    @ezr.cached_container
    def df(self):
        df = self.df_raw
        df.loc[:, 'time_utc'] = df.time.dt.tz_localize('UTC')
        df['time_local'] = df.time_utc.dt.tz_convert('US/Central')
        df = df.sort_values(by='time_local')
        miles_per_km = 0.621371
        df.loc[:, 'distance'] = miles_per_km * df.distance

        df = df.rename(columns={
            'tx_sign': 'sender_callsign',
            'rx_sign': 'receiver_callsign',
            'tx_lat': 'lat_sender',
            'tx_lon': 'lon_sender',
            'distance': 'miles',
        })

        df = df[[
            'time_local',
            'time_utc',
            'sender_callsign',
            'receiver_callsign',
            'snr',
            'lat_sender',
            'lon_sender',
            'miles',
        ]]
        return df


class WSPRPair(ezr.BlobMixin):
    starting = ezr.BlobAttr(None)
    ending = ezr.BlobAttr(None)
    ref_callsign = ezr.BlobAttr(None)
    test_callsign = ezr.BlobAttr(None)

    def __init__(
            self,
            wspr_obj=None,
            ref_callsign=None,
            test_callsign=None,
            starting=None,
            ending=None,
            fuzzy_snr=True,
            limits_time_zone='utc'):
        """
        Args:
            wspr_obj: a snrlib.WSPR() object
            ref_callsign: the call sign associated with the reference antenna
            test_callsign: the call sign associated with the test antenna
            starting: the start time of the test
            ending: the end time of the test
            limits_time_zone: Which timezone to use for limits.  Can be "local" or "utc"
        """
        super().__init__()

        local_zone = 'US/Central'
        utc = 'UTC'
        if limits_time_zone == 'local':
            limits_zone = local_zone
        elif limits_time_zone.lower() == 'utc':
            limits_zone = utc
        else:
            raise ValueError('must be valid timezone')

        self.starting = pd.Timestamp(starting).tz_localize(limits_zone)
        self.ending = pd.Timestamp(ending).tz_localize(limits_zone)
        self.ref_callsign = ref_callsign
        self.test_callsign = test_callsign

        if wspr_obj is None:
            self.wspr = WSPR()
        else:
            self.wspr = wspr_obj

        self.fuzzy_snr = fuzzy_snr

    def enable_pickle_cache(self):
        WSPR.enable_pickle_cache()

    def disable_pickle_cache(self):
        WSPR.disable_pickle_cache()

    @ezr.cached_container
    def df_raw(self):

        df = self.wspr.df

        def fuzzify(x):
            return x + 2 * (.5 - np.random.rand(len(x)))

        if self.fuzzy_snr:
            df.loc[:, 'snr'] = fuzzify(df.snr)

        df = df[df.time_local.between(self.starting, self.ending)]
        return df

    @ezr.cached_container
    def df_ref(self):
        df = self.df_raw
        dfr = df[df.receiver_callsign == self.ref_callsign]
        return dfr

    @ezr.cached_container
    def df_test(self):
        df = self.df_raw
        dft = df[df.receiver_callsign == self.test_callsign]
        return dft

    @ezr.cached_container
    def df(self):
        dfr = self.df_ref
        dft = self.df_test

        join_cols = ['time_local', 'time_utc', 'sender_callsign', 'lat_sender', 'lon_sender', 'miles']
        all_cols = join_cols + ['snr']

        dfj = pd.merge(dfr[all_cols], dft[all_cols], on=join_cols, suffixes=['_ref', '_test'])
        dfj['delta_snr'] = dfj.snr_test - dfj.snr_ref
        return dfj


class Geo:
    def __init__(self, df, scope='global', lat0=32.35730, lon0=-86.149969, num_grid_points=80, scale_miles=500):
        if scope.lower() not in ['us', 'global']:
            raise ValueError('Scope must be either "us" or "global"')

        self.scope = scope.lower()
        self.lat0 = lat0
        self.lon0 = lon0
        self.num_grid_points = num_grid_points

        if not df.empty:
            df = df.groupby(by=['sender_callsign'])[['lat_sender', 'lon_sender', 'delta_snr']].mean().reset_index()

        self.df = df
        self.scale_miles = scale_miles

        self._grid_coord_matrices = None
        self._grid_value_matrix = None

        self.min_lat, self.max_lat = 22, 49
        self.min_lon, self.max_lon = -119, -64

    def __sub__(self, other):
        df = pd.DataFrame()
        b = Geo(df, self.scope, self.lat0, self.lon0, self.num_grid_points, self.scale_miles)
        b._grid_coord_matrices = self.grid_coord_matrices
        b._grid_value_matrix = self.grid_value_matrix - other.grid_value_matrix
        return b

    def get_map_obj(self, ax=None):
        from mpl_toolkits.basemap import Basemap
        if self.scope == 'global':
            m = Basemap(projection='aeqd', lat_0=self.lat0, lon_0=self.lon0, ax=ax)
        else:
            m = Basemap(
                llcrnrlon=-119,
                llcrnrlat=22,
                urcrnrlon=-64,
                urcrnrlat=49,
                projection='lcc',
                lat_1=33,
                lat_2=45,
                lon_0=-95
            )

        if ax is not None:
            m.drawstates()
            m.drawcountries()
            m.drawcoastlines()

        return m

    @ezr.cached_container
    def grid_coord_matrices(self):
        if self._grid_coord_matrices is not None:
            return self._grid_coord_matrices

        m = self.get_map_obj()
        grid_points = self.num_grid_points
        grid_lons_matrix, grid_lats_matrix, x, y = m.makegrid(grid_points, grid_points, returnxy=True)
        tup = grid_lats_matrix, grid_lons_matrix, x, y
        return tup

    @ezr.cached_container
    def grid_value_matrix(self):
        if self._grid_value_matrix is not None:
            return self._grid_value_matrix

        lat_col = 'lat_sender'
        lon_col = 'lon_sender'
        val_col = 'delta_snr'
        df = self.df
        return self.get_values(df[lat_col], df[lon_col], df[val_col])

    def get_values(self, data_lats, data_lons, data_vals, batch_len=200):
        earth_rad_mi = 3958.8

        # Limit data to US if that is the scope
        if self.scope == 'us':
            dfd = pd.DataFrame({
                'lat': data_lats,
                'lon': data_lons,
                'vals': data_vals,
            })
            dfd = dfd[dfd.lat.between(self.min_lat, self.max_lat)]
            dfd = dfd[dfd.lon.between(self.min_lon, self.max_lon)]

            data_lats = dfd.lat.values
            data_lons = dfd.lon.values
            data_vals = dfd.vals.values

        # Get the lat/lons for the grid
        grid_lats_matrix, grid_lons_matrix, _, _ = self.grid_coord_matrices

        # Transform the lat/lon grids into 1-d arrays
        matrix_shape = grid_lats_matrix.shape
        grid_lats = grid_lats_matrix.reshape(grid_lats_matrix.size) * np.pi / 180
        grid_lons = grid_lons_matrix.reshape(grid_lons_matrix.size) * np.pi / 180

        # Turn the data lats/lons into radians
        data_lats = np.array(data_lats) * np.pi / 180
        data_lons = np.array(data_lons) * np.pi / 180

        # Make dataframe-like arrays of both the grid and the data points
        grid_points = np.stack([grid_lats, grid_lons], axis=1)
        data_points = np.stack([data_lats, data_lons, data_vals], axis=1)

        grid_values = np.zeros(len(grid_points))
        weight_values = np.zeros(len(grid_points))

        # Compute the number of batches I'll need to run
        num_batches = max([len(data_points) // batch_len, 1])

        # Divvy up the data into the appropriate number of batches
        data_batches = np.array_split(data_points, num_batches)
        scale = self.scale_miles

        from tqdm.notebook import tqdm
        from sklearn.metrics.pairwise import haversine_distances

        # Iterate over batches to populate the grid values
        for batch_points in tqdm(data_batches):
            # This is a matrix of distances between the data and the grid points
            dist_matrix = earth_rad_mi * haversine_distances(grid_points, batch_points[:, :2])

            # # Define a weighting function as a function of distance
            # weight_matrix = np.exp(-(dist_matrix / scale) ** 2)
            weight_matrix = 1 / (1 + (dist_matrix / scale) ** 2)

            # Take the weighted sum of all the data points
            weighted_sum = weight_matrix @ batch_points[:, 2]

            # Sum up the weights for normalization later
            sum_weights = np.sum(weight_matrix, 1)

            # Add weighted sums and summed weights to flattened grid elements
            grid_values += weighted_sum.flatten()
            weight_values += sum_weights.flatten()

        # Compute the weighted mean using value and weight sums
        grid_values = grid_values / (weight_values + 1e-12)

        # Reshape weighted mean back into grid shape and return
        grid_values = grid_values.reshape(matrix_shape)
        return grid_values

    def plot(self, center='auto', halfrange='auto', clabel='dB Difference', title='SNR Difference'):
        from matplotlib import pyplot as plt
        import matplotlib.colors as colors
        import colorcet as cc
        plt.subplots_adjust(hspace=.01, )
        fig = plt.figure(figsize=(10, 10))
        fig.tight_layout()
        ax = fig.add_subplot()
        ax.set_title(title)

        m = self.get_map_obj(ax=ax)
        grid_lons_matrix, grid_lats_matrix, x, y = self.grid_coord_matrices

        z = self.grid_value_matrix

        m.drawmapboundary(fill_color='white')

        
        m.fillcontinents(color='whitesmoke', lake_color='white')

        zf = z.flatten()
        zf = zf[~np.isnan(zf)]
        if center == 'auto':
            center = np.median(zf, )

        if halfrange == 'auto':
            span = .25
            halfrange = np.quantile(zf, .5 + span) - np.quantile(zf, .5 - span)

        pcm = m.pcolormesh(
            x, y, z, alpha=1, cmap=cc.cm.CET_D1, norm=colors.CenteredNorm(vcenter=center, halfrange=halfrange))
        cb = plt.colorbar(pcm, orientation='vertical', ax=ax, shrink=0.8, pad=.1)
        cb.set_label(clabel)
        return ax
