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
    files = map(lambda x : (x[:-5], f"C:\\KEX\\test\\pose\\{x}") ,os.listdir(f"C:\\KEX\\test\\pose"))

    for filename, filepath in files:
        print(filename, filepath)
        if os.path.exists(f"C:\\KEX\\Sign_overlayed\\{filename}.mp4"):
            continue
        
        with open(filepath, "rb") as f:
            pose = Pose.read(f.read())


        v = PoseVisualizer(pose)


        # Draws pose on top of video. 
        print(f"Now overlaying {filename}")
        print(f"C:\\KEX\\test\\gif\\{filename}.mp4", f"C:\\KEX\\test\\video\\{filename}.mp4")
        with HiddenPrints():
            v.save_video(f"C:\\KEX\\test\\gif\\{filename}.mp4", v.draw_on_video(f"C:\\KEX\\test\\video\\{filename}.mp4"))
        print(f"Done overlaying {filename}\n")


    return None


if __name__ == "__main__":
    main()
