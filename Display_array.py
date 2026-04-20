import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import matplotlib.animation as animation


LINES = {
    "right_hand": (
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
    ),
    "left_hand": (
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
    ),
    "body": (
        (0, 1),
        (0, 2),
        (1, 3),
        (2, 4),
        (3, 5),
        (4, 6),
        (6, 8),
        (8, 10),
        (10, 6),
        (5, 7),
        (7, 9),
        (9, 11),
        (11, 5),
    ),
    "face": (
        (0, 11),
        (0, 14),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 1),
        (5, 6),
        (6, 7),
        (7, 8),
        (8, 5),
        (9, 10),
        (10, 11),
        (12, 13),
        (13, 14),
        (15, 19),
        (15, 21),
        (16, 20),
        (16, 22),
        (17, 19),
        (17, 20),
        (18, 21),
        (18, 22),
        (23, 24),
    ),
}


def update_lines(frame, line_plots, line_points):
    for plot, point in zip(line_plots, line_points[frame]):
        plot.set_data_3d(point)
    return line_plots

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache_dir", default="Sign_cache\Ã…TTA@num_1.pose.npz", type=Path
    )
    parser.add_argument(
        "--gif_dir", default="./Sign_gif", type=Path
    )
    args = parser.parse_args()

    pose = np.load(args.cache_dir)["pose"]


    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    i = 0
    for x, y, z in pose[1]:
        ax.plot(x, y, z, "o")
        ax.text(x,y,z,i)
        i+=1

    for key, value in LINES:
        for line in value:
            match key:
                case "right_hand":
                    offset = 0
                case "left_hand":
                    offset = 0
                case "body":
                    offset = 21
                case "face":
                    offset = 33

    plt.show()

"""def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache_dir", default="Sign_cache\Ã…TTA@num_1.pose.npz", type=Path
    )
    parser.add_argument(
        "--gif_dir", default="./Sign_gif", type=Path
    )
    args = parser.parse_args()

    b = np.load(args.cache_dir)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    connections = {"right_hand": ("body", 5), "left_hand": ("body", 4)}
    points = sum(len(b[choice][0]) for choice in LINES.keys())
    print(points)
    line_plots = [ax.plot([], [], [])[0] for _ in range(points)]
    frame = 0
    line_points = []
    for frame in range(25):
        line_points.append([])
        for choice in LINES.keys():
            for start, stop in LINES[choice]:
                if len(b[choice][frame]) == 0:
                    continue
                base = (
                    b[choice][frame][0] if not choice in ["body", "face"] else [0, 0, 0]
                )
                joint = (
                    b[connections[choice][0]][frame][connections[choice][1]]
                    if not choice in ["body", "face"]
                    else [0, 0, 0]
                )

                line_points[frame].append(
                    (
                        [
                            b[choice][frame][start][0] - base[0] + joint[0],
                            b[choice][frame][stop][0] - base[0] + joint[0],
                        ],
                        [
                            (b[choice][frame][start][2] - base[2] + joint[2]) * 50,
                            (b[choice][frame][stop][2] - base[2] + joint[2]) * 50,
                        ],
                        [
                            -(b[choice][frame][start][1] - base[1] + joint[1]),
                            -(b[choice][frame][stop][1] - base[1] + joint[1]),
                        ],
                    )
                )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim3d(-1, 1)
    ax.set_ylim3d(-1, 1)
    ax.set_zlim3d(-1, 1)

    ani = animation.FuncAnimation(
        fig, update_lines, 25, fargs=(line_plots, line_points), interval=1000 / 25
    )

    ani.save(args.gif_dir / (args.cache_dir.name[:-4] + ".gif"))

    plt.show()"""

if __name__ == "__main__":
    main()