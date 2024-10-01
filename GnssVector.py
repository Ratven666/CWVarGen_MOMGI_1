import math

from GnssMasureGenerator import GnssMeasureGenerator
from GnssNet import GnssNet
from GnssNetGenerator import GnssNetGenerator


class GnssVector:

    def __init__(self, gnss_net: GnssNet, point_0_name: str, point_1_name: str):
        self.gnss_net = gnss_net
        self.point_0 = self.gnss_net.get_point_by_name(point_0_name)
        self.point_1 = self.gnss_net.get_point_by_name(point_1_name)
        self.dx, self.dy, self.dz = None, None, None
        self.s_dist, self.azimuth, self.zenith = None, None, None
        self.mse_dx, self.mse_dy, self.mse_dz = None, None, None
        self.mse_dist, self.mse_azimuth, self.mse_zenith = None, None, None
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
        self.azimuth = math.atan2(self.dy, self.dx)
        self.zenith = math.acos(self.dz / self.s_dist)

        self.calk_vector_mse()
        # self.calk_mse_stat()

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

        self.mse_dist = ((self.dx / self.s_dist) ** 2 * self.mse_dx ** 2 +
                         (self.dy / self.s_dist) ** 2 * self.mse_dy ** 2 +
                         (self.dz / self.s_dist) ** 2 * self.mse_dz ** 2) ** 0.5

        self.mse_azimuth = ((-self.dy / (self.dx ** 2 + self.dy ** 2)) ** 2 * self.mse_dx ** 2 +
                            (self.dx / (self.dx ** 2 + self.dy ** 2)) ** 2 * self.mse_dy ** 2) ** 0.5

        self.mse_zenith = ((-1 / (self.s_dist * (1 - (self.dz / self.s_dist) ** 2) ** 0.5)) ** 2 * self.mse_dz ** 2 +
                           (self.dz / (self.s_dist ** 2 * (1 - (self.dz / self.s_dist) ** 2) ** 0.5)) ** 2 * self.mse_dist ** 2) ** 0.5

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
                f"mse_s_dist={self.mse_dist:.3f}, "
                f"mse_azimuth={math.degrees(self.mse_azimuth) * 206265:.3f}, "
                f"mse_zenith={math.degrees(self.mse_zenith) * 206265:.3f})")


if __name__ == "__main__":
    gnss_net = GnssNetGenerator(random_seed=42, num_points=5).create_gnss_net()

    gmg = GnssMeasureGenerator(gnss_net, random_seed=42, num_of_measure=100)

    # gnss_net.plot_net()

    gnss_vector = GnssVector(gnss_net, "SIEY", "PVAU")
    print(gnss_vector)
    # gnss_net.plot_net()
    print("0.09485379353656577 61.318497097279504 622.7606537516397")