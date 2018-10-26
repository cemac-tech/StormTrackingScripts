# -*- coding: utf-8 -*-
"""Storm calculations

This module was developed by CEMAC as part of the AMAMA 2050 Project.
This scripts build on Work done my Rory Fitzpatrick, taking the
information generated by dataminer to cacluate desired diagnostics
about storms over desired area.

Example:
    To use::
        module load Strom_calculations
        c = storm_calculations(x1,x2,y1,y2,size)

Attributes:
    varslist(list): List of vairables required in dataminer
    fname(str): File to extract lat and lons
    froot(str): Root folder of data

.. CEMAC_stomtracking:
   https://github.com/cemac/StormTrackingScripts
right, so in this file we are setting up all the information needed
for our CAPE calculations.
Looking at the literature, we need pressure, temperature, dewpoint temperature,
height, and specific  (g/kg) for all the intense storms. We will use the
pressure values 850 hPa upwards in order to remove the issues with 925 hPa T
values for some storms.
"""

import pandas as pd
import numpy as np
import metpy.calc as metcalc


class stormcalcs(object):
    '''Description
       Stage 1: currently a suit of functions for finding information on
       storms in region and Generating cvs files of that information.

    '''
    def __init__(self, csvname, altcsvname=None):

        fname = self.csvname
        df = pd.read_csv(csvname, sep=',')
        cold = df.mean_T15_1800 - df.mean_T15_1200
        mslp_diff = df.eve_mslp_mean - df.midday_mslp
        u_diff_10m = df.eve_wind_99p - df.midday_wind
        u3_diff_10m = df.eve_wind3_99p - df.midday_wind3
        precip99 = df.precip_99th_perc*3600
        precipvol = df.precip_accum*3600
        vars = ['pressure', 'T' 'dewpT', 'height', 'Q', 'z', 'RH650']
        self.tephidf = pd.DataFrame(columns=vars)
        vars = ['P_lcl', 'P_lfc', 'P_el', 'CAPE', 'CIN']
        self.capedf = pd.DataFrame(columns=vars)

    def calc_cape(self, q15, T, idx):
        '''Description:
            Variable required to calculate Convective Available Potential
            Energy: $\int_{zf}^{zn} g
            \left( \frac{T_{v, parcel} - T_{v,env}}{T_{v,env}}\right)
            \mathrm{d}z$
            If > 0 storms possible if enough moisture
            Attributes:
                idx: row index
            Returns:
            CAPE(dataframe): dataframe containing Vars for cape calculations
            TEPHI(dataframe): dataframe containg vars for tephigrams
        '''
        P = self.allvars['eve_mslp_mean'].loc[idx]/100
        # ? 975 is a max value ?
        if P > 975:
            P = 975
        xy850 = genslice(row.llon, row.llat, row.ulat, row.ulon,
                         n1=q, n2=100)
        # midday
        q15 = q15[3, :, :].extract(xy850)
        T = T[3, :, :].extract(xy850)
        # get rid of values sub 100?
        T[T.data < 100] = np.nan
        q15[T.data < 100] = np.nan
        for p in range(0, T_data.shape[0]):
            Tp = np.nanmean(T[p, :, :])
            Qp = np.nanmean(Q[p, :, :])
        Tcol = cubemean(Tp).data
        qcol = cubemean(q15p).data
        T.data = Tcol
        q.data = qcol
        pressure = T.coord('pressure').points
        pval = T.data.shape[0] + 1
        f_T = fle_T[3, : pval, 1, 1]
        f_q = fle_q[3, : pval, 1, 1]
        f_T.data[:pval] = Tcol
        f_T.data[pval] = allvars['mean_T15_1800'].loc[idx]
        f_q.data[:pval] = qcol
        f_q.data[pval] = cubemean(q15).data
        t = f_T
        pres = f_q
        f_q.data = pressure*100
        pressures = f_q.data
        if len(pressure == 18):
            for p in range(0, len(pressures)):
                if 710. >= pressures[p] > 690.:
                    RH_650hPa = ([(0.263 * pres.data[p] * pressures.data[p])
                                  / 2.714**((17.67*(t.data[p] - 273.16)) /
                                            (t.data[p] - 29.65))])
                T = (0.263 * pres.data[p] *
                     pressures.data[p])/2.714**((17.67*(t.data[p] -
                                                 273.16))/(t.data[p] - 29.65))
                dwpt = meteocalc.dew_point(temperature=t[p].data - 273.16,
                                           humidity=T)
                if p < len(pressures)-1:
                    pressure = (t[p].data*((cube_mslp.data /
                                            pressures.data[p])**(1./5.257) - 1)
                                / 0.0065)
                else:
                    height[p] = 1.5

        self.tephidf['pressure'].loc[idx] = np.average(pressure, axis=0)
        self.tephidf['T'].loc[idx] = np.average(T, axis=0)
        self.tephidf['dewpT'].loc[idx] = np.average(depwT, axis=0)
        self.tephidf['height'].loc[idx] = np.average(height, axis=0)
        self.tephidf['Q'].loc[idx] = np.average(Q, axis=0)
        self.tephidf['p99'].loc[idx] = np.average(p99, axis=0)
        self.tephidf['xwind'].loc[idx] = np.average(xwind, axis=0)
        self.tephidf['ywind'].loc[idx] = np.average(ywind, axis=0)
        self.tephidf['RH650'].loc[idx] = np.average(RH650, axis=0)
        mydata = dict(zip(('hght', 'pres', 'temp', 'dwpt'),
                          (height, pressure, T, dewpT)))
        S = sk.Sounding(soundingdata=mydata)
        parcel = S.get_parcel('mu')
        self.capedf.loc[idx] = S.get_cape(*parcel)
