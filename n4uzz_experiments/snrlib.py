import asyncio

import easier as ezr
import pandas as pd
from aiohttp import ClientSession
from aiochclient import ChClient


class WSPR(ezr.pickle_cache_mixin):
    pkc = ezr.pickle_cache_state('active')

    def __init__(self, starting='12/1/2021', ending='1/1/2040', callsign_rex=r'N4UZZ.*'):
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
