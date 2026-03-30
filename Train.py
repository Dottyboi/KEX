import torch
from pose_format.pose import Pose
from pose_format.torch.pose_body import TorchPoseBody

data_buffer = open("example.pose", "rb").read()

# Load data as a PyTorch tensor:
pose = Pose.read(data_buffer, TorchPoseBody).torch()
print(type(pose))