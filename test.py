from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer


with open("example.pose", "rb") as f:
    pose = Pose.read(f.read())

v = PoseVisualizer(pose)

v.save_video("example.mp4", v.draw())

# Draws pose on top of video. 
v.save_video("example.mp4", v.draw_on_video("SSLC\SSLC_videofiler_mp4\SSLC01_004_S001_S002_p.mp4"))