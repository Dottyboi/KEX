import torch
from pose_format.pose import Pose

data_buffer = open("example.pose", "rb").read()

# Load data as a PyTorch tensor:
from pose_format.torch import TorchPoseBody
pose = Pose.read(data_buffer, TorchPoseBody)
print(pose.size())