import math

import pandas as pd
from matplotlib import pyplot as plt

from GnssMasureGenerator import GnssMeasureGenerator
from GnssNet import GnssNet
from GnssNetGenerator import GnssNetGenerator
from GnssPoint import GnssPoint


class GnssVector:

    def __init__(self, gnss_net: GnssNet, point_0_name: str, point_1_name: str, color="black"):
        self.gnss_net = gnss_net
        self.point_0 = self.gnss_net.get_point_by_name(point_0_name)
        self.point_1 = self.gnss_net.get_point_by_name(point_1_name)
        self.color = color
        self.x_0, self.y_0, self.z_0 = self.calk_base_coordinates_for_point(self.point_0)
        self.x_1, self.y_1, self.z_1 = self.calk_base_coordinates_for_point(self.point_1)
        self.dx, self.dy, self.dz = None, None, None
        self.s_dist, self.azimuth, self.zenith = None, None, None
        self.h_dist = None
        self.mse_dx, self.mse_dy, self.mse_dz = None, None, None
        self.mse_s_dist, self.mse_azimuth, self.mse_zenith = None, None, None
        self.calk_vector()

    def calk_vector(self):
        d_x, d_y, d_z = [], [], []
        for time, measure_0 in self.point_0:
            measure_1 = self.point_1.measure_data.get(time)
            if measure_1 is not None:
                d_x.append(measure_1["x"] - measure_0["x"])
                d_y.append(measure_1["y"] - measure_0["y"])
                d_z.append(measure_1["z"] - measure_0["z"])

        self.dx = sum(d_x) / len(d_x)
        self.dy = sum(d_y) / len(d_y)
        self.dz = sum(d_z) / len(d_z)
        self.s_dist = (self.dx ** 2 + self.dy ** 2 + self.dz ** 2) ** 0.5
        self.h_dist = (self.dx ** 2 + self.dy ** 2) ** 0.5
        self.azimuth = math.atan2(self.dy, self.dx)
        self.zenith = math.acos(self.dz / self.s_dist)

        self.calk_vector_mse()

    def calk_vector_mse(self):
        vx_2, vy_2, vz_2 = [], [], []
        for time, measure_0 in self.point_0:
            measure_1 = self.point_1.measure_data.get(time)
            if measure_1 is not None:
                vx_2.append((measure_1["x"] - measure_0["x"] - self.dx) ** 2)
                vy_2.append((measure_1["y"] - measure_0["y"] - self.dy) ** 2)
                vz_2.append((measure_1["z"] - measure_0["z"] - self.dz) ** 2)
        self.mse_dx = (sum(vx_2) / (len(vx_2) - 1)) ** 0.5
        self.mse_dy = (sum(vy_2) / (len(vy_2) - 1)) ** 0.5
        self.mse_dz = (sum(vz_2) / (len(vz_2) - 1)) ** 0.5

        self.mse_s_dist = ((self.dx / self.s_dist) ** 2 * self.mse_dx ** 2 +
                           (self.dy / self.s_dist) ** 2 * self.mse_dy ** 2 +
                           (self.dz / self.s_dist) ** 2 * self.mse_dz ** 2) ** 0.5

        self.mse_azimuth = ((-self.dy / (self.dx ** 2 + self.dy ** 2)) ** 2 * self.mse_dx ** 2 +
                            (self.dx / (self.dx ** 2 + self.dy ** 2)) ** 2 * self.mse_dy ** 2) ** 0.5

        self.mse_zenith = ((-1 / (self.s_dist * (1 - (self.dz / self.s_dist) ** 2) ** 0.5)) ** 2 * self.mse_dz ** 2 +
                           (self.dz / (self.s_dist ** 2 * (1 - (self.dz / self.s_dist) ** 2) ** 0.5)) ** 2 * self.mse_s_dist ** 2) ** 0.5

    @staticmethod
    def calk_base_coordinates_for_point(point: GnssPoint):
        x_0, y_0, z_0 = [], [], []
        if point.is_base():
            return point.x, point.y, point.z
        else:
            for time, measure in point:
                x_0.append(measure["x"])
                y_0.append(measure["y"])
                z_0.append(measure["z"])
        x_0 = sum(x_0) / len(x_0)
        y_0 = sum(y_0) / len(y_0)
        z_0 = sum(z_0) / len(z_0)
        return point.x, point.y, point.z
        # return x_0, y_0, z_0

    def plot_vector(self, fig=None, ax=None, show=True):
        if fig is None and ax is None:
            fig, ax = plt.subplots()

        ax.quiver(self.point_0.x, self.point_0.y,
                  self.dx, self.dy, angles='xy', scale_units='xy', scale=1, color=self.color)

        self.point_0.plot_point(fig, ax, show=False)
        self.point_1.plot_point(fig, ax, show=False)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        if show:
            plt.show()

    def _get_s_dist_a_coefficients_df(self):
        coefficient_dict = {}
        if self.point_0.is_rover():
            coefficient_dict[f"{self.point_0.name}_x"] = -math.cos(self.azimuth)
            coefficient_dict[f"{self.point_0.name}_y"] = -math.sin(self.azimuth)
            coefficient_dict[f"{self.point_0.name}_z"] = -self.dz / self.s_dist
        if self.point_1.is_rover():
            coefficient_dict[f"{self.point_1.name}_x"] = math.cos(self.azimuth)
            coefficient_dict[f"{self.point_1.name}_y"] = math.sin(self.azimuth)
            coefficient_dict[f"{self.point_1.name}_z"] = self.dz / self.s_dist
        coefficient_dict = pd.DataFrame([coefficient_dict],
                                        index=[f"s_dist_{self.point_0.name}-{self.point_1.name}"])
        return coefficient_dict

    def _get_azimuth_a_coefficients_df(self):
        coefficient_dict = {}
        if self.point_0.is_rover():
            coefficient_dict[f"{self.point_0.name}_x"] = math.sin(self.azimuth) / self.h_dist
            coefficient_dict[f"{self.point_0.name}_y"] = -math.cos(self.azimuth) / self.h_dist
        if self.point_1.is_rover():
            coefficient_dict[f"{self.point_1.name}_x"] = -math.sin(self.azimuth) / self.h_dist
            coefficient_dict[f"{self.point_1.name}_y"] = math.cos(self.azimuth) / self.h_dist
        coefficient_dict = pd.DataFrame([coefficient_dict],
                                        index=[f"azimuth_{self.point_0.name}-{self.point_1.name}"])
        return coefficient_dict

    def _get_zenith_a_coefficients_df(self):
        coefficient_dict = {}
        if self.point_0.is_rover():
            coefficient_dict[f"{self.point_0.name}_x"] = ((self.dz * math.cos(self.azimuth)) /
                                                                    (self.dz ** 2 + self.h_dist ** 2)) * -1
            coefficient_dict[f"{self.point_0.name}_y"] = ((self.dz * math.sin(self.azimuth)) /
                                                                    (self.dz ** 2 + self.h_dist ** 2)) * -1
            coefficient_dict[f"{self.point_0.name}_z"] = (self.h_dist / (self.h_dist ** 2 + self.dz ** 2))

        if self.point_1.is_rover():
            coefficient_dict[f"{self.point_1.name}_x"] = ((self.dz * math.cos(self.azimuth)) /
                                                                  (self.dz ** 2 + self.h_dist ** 2))
            coefficient_dict[f"{self.point_1.name}_y"] = ((self.dz * math.sin(self.azimuth)) /
                                                                  (self.dz ** 2 + self.h_dist ** 2))
            coefficient_dict[f"{self.point_1.name}_z"] = (self.h_dist / (self.h_dist ** 2 + self.dz ** 2)) * -1
        coefficient_dict = pd.DataFrame([coefficient_dict],
                                        index=[f"zenith_{self.point_0.name}-{self.point_1.name}"])
        return coefficient_dict

    def get_a_coefficients_df(self):
        df = pd.DataFrame()
        df = pd.concat([df, self._get_s_dist_a_coefficients_df()])
        df = pd.concat([df, self._get_azimuth_a_coefficients_df()])
        df = pd.concat([df, self._get_zenith_a_coefficients_df()])
        return df

    def get_p_df(self):
        p_df = pd.DataFrame()
        p_df = pd.concat([p_df, pd.DataFrame([{f"s_dist_{self.point_0.name}-{self.point_1.name}":
                                                    1 / self.mse_s_dist ** 2}],
                                             index=[f"s_dist_{self.point_0.name}-{self.point_1.name}"])])
        p_df = pd.concat([p_df, pd.DataFrame([{f"azimuth_{self.point_0.name}-{self.point_1.name}":
                                                   1 / self.mse_azimuth ** 2}],
                                             index=[f"azimuth_{self.point_0.name}-{self.point_1.name}"])])
        p_df = pd.concat([p_df, pd.DataFrame([{f"zenith_{self.point_0.name}-{self.point_1.name}":
                                                   1 / self.mse_zenith ** 2}],
                                             index=[f"zenith_{self.point_0.name}-{self.point_1.name}"])])
        return p_df

    def get_l_ds(self):
        s_dist_0 = ((self.x_0 - self.x_1) ** 2 + (self.y_0 - self.y_1) ** 2 + (self.z_0 - self.z_1) ** 2) ** 0.5
        azimuth_0 = math.atan2((self.y_1 - self.y_0), (self.x_1 - self.x_0))
        zenith_0 = math.acos((self.z_1 - self.z_0) / s_dist_0)
        ds = pd.Series([(s_dist_0 - self.s_dist),
                      (azimuth_0 - self.azimuth),
                      (zenith_0 - self.zenith)],
                      index=[f"s_dist_{self.point_0.name}-{self.point_1.name}",
                             f"azimuth_{self.point_0.name}-{self.point_1.name}",
                             f"zenith_{self.point_0.name}-{self.point_1.name}",
                            ])
        return ds

    def get_base_coord_ds(self):
        ds = pd.Series([self.x_0, self.y_0, self.z_0, self.x_1, self.y_1, self.z_1],
                       index=[f"{self.point_0.name}_x",
                              f"{self.point_0.name}_y",
                              f"{self.point_0.name}_z",
                              f"{self.point_1.name}_x",
                              f"{self.point_1.name}_y",
                              f"{self.point_1.name}_z",
                              ])
        return ds

    # def calk_mse_stat(self):
    #     distance_lst, azimuth_lst, zenith_lst = [], [], []
    #     for time, measure_0 in self.point_0:
    #         measure_1 = self.point_1.measure_data.get(time)
    #         if measure_1 is not None:
    #             dx = measure_1["x"] - measure_0["x"]
    #             dy = measure_1["y"] - measure_0["y"]
    #             dz = measure_1["z"] - measure_0["z"]
    #             distance_lst.append((dx ** 2 + dy ** 2 + dz ** 2) ** 0.5)
    #             azimuth_lst.append(math.atan2(dy, dx))
    #             zenith_lst.append(math.acos(dz / distance_lst[-1]))
    #     vv_dist = [(distance - self.s_dist) ** 2 for distance in distance_lst]
    #     vv_azimuth = [(azimuth - self.azimuth) ** 2 for azimuth in azimuth_lst]
    #     vv_zenith = [(zenith - self.zenith) ** 2 for zenith in zenith_lst]
    #     self.mse_dist = (sum(vv_dist) / (len(vv_dist) - 1)) ** 0.5
    #     self.mse_azimuth = (sum(vv_azimuth) / (len(vv_azimuth) - 1)) ** 0.5
    #     self.mse_zenith = (sum(vv_zenith) / (len(vv_zenith) - 1)) ** 0.5

    def __str__(self):
        return (f"GnssVector({self.point_0.name}-{self.point_1.name}, "
                f"dist={self.s_dist:.3f}, azimuth={math.degrees(self.azimuth):.3f}, "
                f"zenith={math.degrees(self.zenith):.3f}, "
                f"mse_dx={self.mse_dx:.3f}, mse_dy={self.mse_dy:.3f}, mse_dz={self.mse_dz:.3f} "
                f"mse_s_dist={self.mse_s_dist:.3f}, "
                f"mse_azimuth={math.degrees(self.mse_azimuth) * 206265:.3f}, "
                f"mse_zenith={math.degrees(self.mse_zenith) * 206265:.3f})")

    def __repr__(self):
        return f"GnssVector({self.point_0.name}-{self.point_1.name})"


if __name__ == "__main__":
    gnss_net = GnssNetGenerator(random_seed=42, num_points=5).create_gnss_net()

    gmg = GnssMeasureGenerator(gnss_net, random_seed=42, num_of_measure=100)

    # gnss_net.plot_net()

    # gnss_vector = GnssVector(gnss_net, "SIEY", "PVAU")
    gnss_vector = GnssVector(gnss_net, "PUSN", "PVAU", color="r")
    print(gnss_vector)
    # gnss_net.plot_net()
    print("0.09485379353656577 61.318497097279504 622.7606537516397")

    gnss_vector.plot_vector()

    print(gnss_vector.get_a_coefficients_df())
    print(gnss_vector.get_p_df())
    print(gnss_vector.get_l_ds())
    print(gnss_vector.get_base_coord_ds())