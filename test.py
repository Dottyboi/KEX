from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer
import os

def main() -> None:
    sign_dict = dict()

    files = map(lambda x : f"C:\KEX\Sign_pose\{x}" ,os.listdir(f"Sign_pose"))
    
    for filepath in files:
        with open(filepath, "rb") as f:
            pose = Pose.read(f.read())


        v = PoseVisualizer(pose)

        file = filepath[18:-5]

        # Draws pose on top of video. 
        v.save_video(f"C:\KEX\Sign_overlayed\{file}.mp4", v.draw_on_video(f"C:\KEX\Sign_videos\{file}.mp4"))


    return None


if __name__ == "__main__":
    main()

