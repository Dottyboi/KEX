import os, re
import xml.etree.ElementTree as ET


# TODO: Fixa datastrukturen så att det blir trädliknande
# TODO: Hitta ett sätt att göra träningen oberoende av höger- eller vänsterhänt tecknande
# TODO: Fråga Jonas om uppdelningen i signgrejen
# TODO: Fråga Jonas om 

class SignNode:
    def __init__(self, sign: str, special : str = "") -> None:
        self.sign = sign
        self.special = special
        self.children: dict[str, SignNode] = dict() # key = version, value = node



class SignTree:
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
    def __init__(self, sign: str, start: int, end: int, filepath: str) -> None:
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
    

def extract_signs(filepath: str, sign_dict : dict[str, list[Sign]]) -> bool:
    tree = ET.parse(filepath)
    root = tree.getroot()

    time_order = root.find("TIME_ORDER")
    if time_order:
        time_conversion_table = {child.attrib["TIME_SLOT_ID"] : child.attrib["TIME_VALUE"] for child in time_order}
    else:
        raise ValueError("Times not found")
    
    header = root.find("HEADER")

    if header == None:
        return False

    videos = list(map(lambda x : f"SSLC/SSLC_videofiler_mp4{x.attrib["RELATIVE_MEDIA_URL"][1:]}", header.findall("MEDIA_DESCRIPTOR")))

    double_participant = re.compile("S[0-9]{3}_S[0-9]{3}")

    for index, video in enumerate(videos):
        if double_participant.match(video):
            videos.pop(index)
        if not os.path.exists(video):
            videos.pop(index)

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

                times = (time_conversion_table[annotation.attrib["TIME_SLOT_REF1"]], 
                         time_conversion_table[annotation.attrib["TIME_SLOT_REF2"]])

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
                    if sign in sign_dict.keys():
                        sign_dict[sign].append(Sign(sign, int(times[0]), int(times[1]), video_file))
                    else:
                        sign_dict[sign] = [Sign(sign, int(times[0]), int(times[1]), video_file)]

    return True


def main() -> None:
    sign_dict = dict()

    files = map(lambda x : "SSLC/Eaf files annotations 20231220/" + x ,os.listdir("SSLC/Eaf files annotations 20231220"))
    
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

    return None


if __name__ == "__main__":
    main()