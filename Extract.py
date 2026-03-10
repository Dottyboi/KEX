import os, re
import xml.etree.ElementTree as ET
import ffmpeg



class SignNode: # not used
    def __init__(self, sign: str, special : str = "") -> None:
        self.sign = sign
        self.special = special
        self.children: dict[str, SignNode] = dict() # key = version, value = node



class SignTree: # not used
    def __init__(self, dictionary: dict[str, SignNode]):
        if not dictionary:
            self.__dict : dict[str, SignNode] = dict()
        else:
            self.__dict : dict[str, SignNode] = dictionary

    def __getitem__(self, key) -> SignNode:
        return self.__dict[key]
    
    def __findroot(self, value: str) -> SignNode:
        return self.__dict[value]
    
    def __recfind(self, node: SignNode) -> SignNode:
        return SignNode("")

    def find(self, value: str) -> SignNode:
        root : SignNode = self.__findroot(value)
        return self.__recfind(root)

class Sign:
    def __init__(self, sign: str, start: str, end: str, filepath: str) -> None:
        self.sign : str = sign
        self.time : tuple[int, int] = (start, end)
        self.filepath : str = filepath

    def __eq__(self, value: object) -> bool:
        if type(value) == Sign:
            return self.sign == value.sign
        else:
            return self.sign == value
        
    def __hash__(self) -> int:
        return hash(self.sign)
    
    def __str__(self) -> str:
        return f"{self.sign} at {self.filepath} [{self.time[0]} - {self.time[1]}]"
    
    def __repr__(self) -> str:
        return self.__str__()
    

def ms_to_timestamp(ms : str|int) -> str:
    return f"{int(ms)//(1000*60*60):02}:{int(ms)//(1000*60)%60:02}:{int(ms)//1000%60:02}.{int(ms)%1000//10:02}"

def extract_signs(filepath: str, sign_dict : dict[str, list[Sign]]) -> bool:
    tree = ET.parse(filepath)
    root = tree.getroot()

    time_order = root.find("TIME_ORDER")
    if time_order:
        time_conversion_table = {child.attrib["TIME_SLOT_ID"] : child.attrib["TIME_VALUE"]  for child in time_order}
    else:
        raise ValueError("Times not found")
    
    header = root.find("HEADER")

    if header == None:
        return False

    videos = list(map(lambda x : os.path.realpath(f"{os.getcwd()}/SSLC/SSLC_videofiler_mp4{x.attrib["RELATIVE_MEDIA_URL"][1:]}"), header.findall("MEDIA_DESCRIPTOR")))

    double_participant = re.compile("S[0-9]{3}")

    remove_list = []

    for video in videos:
        
        if len(double_participant.findall(video)) != 1:
            remove_list.append(video)
        elif not os.path.exists(video):
            remove_list.append(video)

    for video in remove_list:
        videos.pop(videos.index(video))

    if not videos:
        return False

    tiers = root.findall("TIER")

    for tier in tiers:
        if tier.attrib["LINGUISTIC_TYPE_REF"] in ("gloss_dh<>nondh"):
            annotations = map(lambda x : x.find("ALIGNABLE_ANNOTATION") ,tier.findall("ANNOTATION"))

            try:
                participant = tier.attrib["PARTICIPANT"]
            except KeyError:
                continue
            video_file = ""
            
            for video in videos:
                if participant in video:
                    video_file = video

            if not video_file:
                continue

            for annotation in annotations:
                if annotation == None:
                    continue

                times = [int(time_conversion_table[annotation.attrib["TIME_SLOT_REF1"]]), 
                         int(time_conversion_table[annotation.attrib["TIME_SLOT_REF2"]])]

                annotation_value = annotation.find("ANNOTATION_VALUE")

                if annotation_value == None:
                    raise ValueError("ANNOTATION_VALUE not found")

                sign = annotation_value.text


                signs = []

                if not sign:
                    continue

                if "^" in sign:
                    signs += sign.split("^")


                for sign in signs:
                    length = times[1] - times[0]

                    diff = max(0, 1000 - length)//2

                    node = Sign(sign, ms_to_timestamp(max(times[0]-diff, 0)), ms_to_timestamp(min(times[1]+diff)), video_file)
                    if sign in sign_dict.keys():
                        sign_dict[sign].append(node)
                    else:
                        sign_dict[sign] = [node]


    return True


def main() -> None:
    sign_dict = dict()

    files = map(lambda x : f"SSLC/Eaf files annotations 20231220/{x}" ,os.listdir(f"SSLC/Eaf files annotations 20231220"))
    
    for filepath in files:
        if filepath[-3:] != "eaf":
            continue

        if extract_signs(filepath, sign_dict):
            print(f"{filepath} done.")
        else:
            print(f"Video file for {filepath} not found.")

    l = list()
    for key in sign_dict.keys():
        l.append(key)
    l.sort(key= lambda key : len(sign_dict[key]))

    count = 0

    l = l[-100:]

    for key in l:
        print(f"{key}: {len(sign_dict[key])}")
        count += len(sign_dict[key])

    print(f"Signs = {len(l)}")
    print(f"Video files = {count}")

    for annotation in l:
        signs = sign_dict[annotation]

        for sign in signs:
            i = 1

            while os.path.exists(f"Sign_videos/{sign.sign}_{i}.mp4"):
                i += 1


            (
                ffmpeg
                .input(sign.filepath)
                .trim(start=sign.time[0], end=sign.time[1])
                .output(f"Sign_videos/{sign.sign}_{i}.mp4")
                .run()
            )


    return None


if __name__ == "__main__":
    main()