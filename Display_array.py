import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import matplotlib.animation as animation


LINES = (
    (2, 5),
    (0, 17),
    (0, 1),
    (5, 9),
    (9, 13),
    (13, 17),
    (1, 2),
    (2, 3),
    (3, 4),
    (5, 6),
    (6, 7),
    (7, 8),
    (9, 10),
    (10, 11),
    (11, 12),
    (13, 14),
    (14, 15),
    (15, 16),
    (17, 18),
    (18, 19),
    (19, 20),
    (23, 26),
    (21, 38),
    (21, 22),
    (26, 30),
    (30, 34),
    (34, 38),
    (22, 23),
    (23, 24),
    (24, 25),
    (26, 27),
    (27, 28),
    (28, 29),
    (30, 31),
    (31, 32),
    (32, 33),
    (34, 35),
    (35, 36),
    (36, 37),
    (38, 39),
    (39, 40),
    (40, 41),
    (42, 43),
    (42, 44),
    (43, 45),
    (44, 46),
    (45, 47),
    (46, 48),
    (48, 50),
    (50, 52),
    (52, 48),
    (47, 49),
    (49, 51),
    (51, 53),
    (53, 47),
    (54, 65),
    (54, 68),
    (55, 56),
    (56, 57),
    (57, 58),
    (58, 55),
    (59, 60),
    (60, 61),
    (61, 62),
    (62, 59),
    (63, 64),
    (64, 65),
    (66, 67),
    (67, 68),
    (69, 73),
    (69, 75),
    (70, 74),
    (70, 76),
    (71, 73),
    (71, 74),
    (72, 75),
    (72, 76),
    (77, 78),
)


def update_lines(frame, line_plots, line_points):
    for plot, point in zip(line_plots, line_points[frame]):
        plot.set_data_3d(point)
    return line_plots


def plot_animated(b, args):

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    points = 78
    line_plots = [ax.plot([], [], [])[0] for _ in range(points)]
    frame = 0
    line_points = []
    for frame in range(len(b)):
        line_points.append([])
        for point in b[frame]:
            if not point.any():
                print(point)
        for start, stop in LINES:
            line_points[frame].append(
                (
                    [b[frame][start][0], b[frame][stop][0]],
                    [b[frame][start][2], b[frame][stop][2]],
                    [b[frame][start][1], b[frame][stop][1]],
                )
            )

    print(type(b[frame][0][0]))
    print(
        f"right_hand:\n{b[frame][:21,:]}\n"
        + f"left_hand:\n{b[frame][21:42,:]}\n"
        + f"body:\n{b[frame][42:54,:]}\n"
        + f"face:\n{b[frame][54:,:]}\n"
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim3d(-1, 1)
    ax.set_ylim3d(-1, 1)
    ax.set_zlim3d(-1, 1)

    ani = animation.FuncAnimation(
        fig, update_lines, len(b), fargs=(line_plots, line_points), interval=1000 / 25
    )

    ani.save(args.gif_dir / (args.cache_dir.name[:-4] + ".gif"))

    plt.show()


def plot_notime(b):
    new_b = []

    def gaussian(x, mu, sig):
        return (
            1.0
            / (np.sqrt(2.0 * np.pi * sig))
            * np.exp(-np.power((x - mu), 2.0) / (2 * sig))
        )

    for point in range(len(b[-1])):
        x, y, z = [], [], []

        for frame in range(len(b)):
            x.append(b[frame][point][0] if b[frame][point][0] else 0)
            y.append(b[frame][point][1] if b[frame][point][1] else 0)
            z.append(b[frame][point][2] if b[frame][point][2] else 0)

        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        gauss = []
        for frame in range(1, len(b) + 1):
            gauss.append(gaussian(frame - 26 / 2, 0, 1))

        gauss = np.array(gauss)

        x = x @ gauss
        y = y @ gauss
        z = z @ gauss

        new_b.append([x, y, z])

    new_b = np.array(new_b)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    for start, stop in LINES:
        ax.plot(
            [new_b[start][0], new_b[stop][0]],
            [new_b[start][2], new_b[stop][2]],
            [new_b[start][1], new_b[stop][1]],
        )

    ax.plot(0, 0, 0, "o", c="r")
    ax.text(0, 0, 0, "origo")

    print(new_b.shape)

    plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache_dir", default="Sign_cache\Ã…TTA@num_1.pose.npz", type=Path
    )
    parser.add_argument("--gif_dir", default="./Sign_gif", type=Path)
    args = parser.parse_args()

    b = np.load(args.cache_dir)["pose"]

    plot_animated(b, args)

    # plot_notime(b)


if __name__ == "__main__":
    main()
