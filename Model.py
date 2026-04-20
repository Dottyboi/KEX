# import torch
# import torch.nn as nn
# import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

b = np.load("Sign_cache\Ã…TTA@num_1.pose.npz")

print(f"left_hand: {b["left_hand"][0]}")
print(f"right_hand: {b["right_hand"][0]}")
print(f"body: {b["body"][0]}")
print(f"face: {b["face"][0]}")

fig = plt.figure()
ax = fig.add_subplot(projection="3d")

lines = {
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
}
connections = {"right_hand": ("body", 5), "left_hand": ("body", 4)}

frame = -5

print(len(b["body"]))

for choice in lines.keys():
    

for choice in lines.keys():
    for start, stop in lines[choice]:
        base = b[choice][frame][0] if choice != "body" else [0, 0, 0]
        joint = (
            b[connections[choice][0]][frame][connections[choice][1]]
            if choice != "body"
            else [0, 0, 0]
        )

        ax.plot(
            [
                b[choice][frame][start][0] - base[0] + joint[0],
                b[choice][frame][stop][0] - base[0] + joint[0],
            ],
            [
                b[choice][frame][start][1] - base[1] + joint[1],
                b[choice][frame][stop][1] - base[1] + joint[1],
            ],
            zs=[
                b[choice][frame][start][2] - base[2] + joint[2],
                b[choice][frame][stop][2] - base[2] + joint[2],
            ],
        )


ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_xlim3d(-1, 1)
ax.set_ylim3d(-1, 1)
ax.set_zlim3d(-0.11, 0.11)

plt.show()

# ani bs
"""
import matplotlib.cm as cm
import matplotlib.animation as animation

img = [] # some array of images
frames = [] # for storing the generated images
fig = plt.figure()
for i in xrange(6):
    frames.append([plt.imshow(img[i], cmap=cm.Greys_r,animated=True)])

ani = animation.ArtistAnimation(fig, frames, interval=50, blit=True,
                                repeat_delay=1000)
# ani.save('movie.mp4')
plt.show()"""

"""
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


net = Net()"""
