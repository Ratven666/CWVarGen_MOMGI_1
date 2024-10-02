import math

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

from GnssMasureGenerator import GnssMeasureGenerator
from GnssNetGenerator import GnssNetGenerator
from GnssVector import GnssVector


class EqualisedNetwork:

    def __init__(self, *gnss_vectors: GnssVector):
        self.gnss_vectors = list(gnss_vectors)
        self.a_coefficients_df = None
        self.p_coefficients_df = None
        self.l_ds = None
        self.dt_ds = None
        self.coord_lst = self.calculate()

    def add_gnss_vector(self, gnss_vector: GnssVector):
        if isinstance(gnss_vector, GnssVector):
            self.gnss_vectors.append(gnss_vector)
        else:
            raise ValueError("Дллжен быть GnssVector")

    def _get_a_coefficients_df(self):
        if self.a_coefficients_df is None:
            df = pd.DataFrame()
            for vector in self.gnss_vectors:
                df = pd.concat([df, vector.get_a_coefficients_df()])
            self.a_coefficients_df = df.fillna(0)
            return df.fillna(0)
        else:
            return self.a_coefficients_df

    def _get_p_coefficients_df(self):
        if self.p_coefficients_df is None:
            df = pd.DataFrame()
            for vector in self.gnss_vectors:
                df = pd.concat([df, vector.get_p_df()])
            self.p_coefficients_df = df.fillna(0)
            return df.fillna(0)
        else:
            return self.p_coefficients_df

    def _get_l_ds(self):
        if self.l_ds is None:
            ds = pd.Series()
            for vector in self.gnss_vectors:
                ds = pd.concat([ds, vector.get_l_ds()])
            self.l_ds = ds
            return ds
        else:
            return self.l_ds

    def _get_base_coord_ds(self):
        ds = pd.Series()
        for vector in self.gnss_vectors:
            ds = ds.combine_first(vector.get_base_coord_ds())
        return ds

    def get_final_coordinates(self):
        base_coord = self._get_base_coord_ds()
        dt = self._get_dt_ds()
        return base_coord.add(dt, fill_value=0)

    def _get_dt_ds(self):
        if self.dt_ds is None:
            a = self._get_a_coefficients_df()
            point_idx = a.columns
            a = a.to_numpy()
            p = self._get_p_coefficients_df().to_numpy()
            l = self._get_l_ds().to_numpy()
            n = a.T @ p @ a
            atpl = a.T @ p @ l
            q = np.linalg.inv(n)
            dt = -q @ atpl
            dt_ds = pd.Series(dt.flatten(), index=point_idx)
            self.dt_ds = dt_ds
            return dt_ds
        else:
            return self.dt_ds

    def _get_v_ds(self):
        a = self._get_a_coefficients_df().to_numpy()
        dt = self._get_dt_ds().to_numpy()
        l = self._get_l_ds().to_numpy()
        v = a @ dt + l
        ds = pd.Series(v, index=self._get_a_coefficients_df().index)
        return ds

    def _get_mu(self):
        v = self._get_v_ds().to_numpy()
        p = self._get_p_coefficients_df().to_numpy()
        mu = v.T @ p @ v
        return mu

    def calculate(self):
        self._calk_points_mse_ellipses()
        return self.get_final_coordinates()

    def _calk_points_mse_ellipses(self):
        a = self._get_a_coefficients_df()
        point_idx = a.columns
        a = a.to_numpy()
        p = self._get_p_coefficients_df().to_numpy()
        n = a.T @ p @ a
        mu = self._get_mu()
        q = mu * np.linalg.inv(n)
        q_df = pd.DataFrame(q, columns=point_idx, index=point_idx)
        for vector in self.gnss_vectors:
            for point in vector.point_0, vector.point_1:
                if point.is_rover():
                    p_np = q_df[[f"{point.name}_x",
                                 f"{point.name}_y"]].loc[[f"{point.name}_x",
                                                          f"{point.name}_y"]].to_numpy()
                    theta = math.degrees(math.atan2((2 * p_np[0][1]), (p_np[0][1] - p_np[1][1])) / 2)
                    theta = theta + 360 if theta < 0 else theta
                    q = ((p_np[0][0] - p_np[1][1]) ** 2 + 4 * p_np[1][0] ** 2) ** 0.5
                    a = ((p_np[0][0] + p_np[1][1] + q) / 2) ** 0.5
                    b = ((p_np[0][0] + p_np[1][1] - q) / 2) ** 0.5
                    try:
                        m_z = q_df.loc[f"{point.name}_z"][f"{point.name}_z"] ** 0.5
                    except KeyError:
                        m_z = None
                    point.mse = {"M": (p_np[0][0] + p_np[1][1]) ** 0.5,
                                      "m_x": p_np[0][0] ** 0.5,
                                      "m_y": p_np[1][1] ** 0.5,
                                      "m_z": m_z,
                                      "theta": theta,
                                      "a": a,
                                      "b": b}
                else:
                    point.mse = {"M": 0, "m_x": 0, "m_y": 0,
                                 "m_z": 0, "theta": 0, "a": 0, "b": 0}

    def plot_eq_net(self, fig=None, ax=None, show=True):
        if fig is None and ax is None:
            fig, ax = plt.subplots()

        for vector in self.gnss_vectors:
            vector.plot_vector(fig, ax, show=False)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        if show:
            plt.show()



if __name__ == "__main__":
    gnss_net_1 = GnssNetGenerator(random_seed=42, num_points=5).create_gnss_net()
    gmg = GnssMeasureGenerator(gnss_net_1, random_seed=42, num_of_measure=100)

    # gnss_net_1.plot_net()

    v1 = GnssVector(gnss_net_1, "siey", "pvau")
    v2 = GnssVector(gnss_net_1, "zjov", "pvau")
    v3 = GnssVector(gnss_net_1, "zjov", "pusn")
    v4 = GnssVector(gnss_net_1, "iccw", "pusn")
    v5 = GnssVector(gnss_net_1, "iccw", "pvau")

    en = EqualisedNetwork(v1, v2, v3, v4)
    en.add_gnss_vector(v5)

    # print(en.gnss_vectors, sep="\n\n")

    # en.plot_eq_net()
    #
    # print(en.get_p_coefficients_df())
    #

    # print(a.T @ p @ l)
    #
    # print(a.T @ p @ a)
    #
    # print(en.get_a_coefficients_df().columns)
    # print(en.get_dt_ds())
    #
    # print(en._get_base_coord_ds())
    print(gnss_net_1)

    # print(en.get_final_coordinates())
    #
    # print(en._get_v_ds())
    #
    # print(en._get_mu())
    #
    # print(en._get_v_ds().to_numpy() * 10)

    # print(en._get_a_coefficients_df().index)
