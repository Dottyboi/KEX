import torch
from pose_format.pose import Pose
import pose_format
print(dir(pose_format))
from pose_format.torch import pose_body as TorchPoseBody

data_buffer = open("example.pose", "rb").read()

# Load data as a PyTorch tensor:
pose = Pose.read(data_buffer, TorchPoseBody)
print(pose.size())