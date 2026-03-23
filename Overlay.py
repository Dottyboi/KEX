from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer
import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def main() -> None:
    sign_dict = dict()

    files = map(lambda x : f"C:\\KEX\\Sign_pose\\{x}" ,os.listdir(f"Sign_pose"))

    for filepath in files:
        if os.exists(f"C:\\KEX\\Sign_overlayed\\{ffilepath[17:-5]}.mp4"):
            continue
        
        with open(filepath, "rb") as f:
            pose = Pose.read(f.read())


        v = PoseVisualizer(pose)

        file = filepath[17:-5]

        # Draws pose on top of video. 
        print(f"Now overlaying {file}")
        with HiddenPrints():
            v.save_video(f"C:\\KEX\\Sign_overlayed\\{file}.mp4", v.draw_on_video(f"C:\\KEX\\Sign_videos\\{file}.mp4"))
        print(f"Done overlaying {file}\n")


    return None


if __name__ == "__main__":
    main()
