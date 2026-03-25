import os, re, sys
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

class Node:
    def __init__(self, value, nxt=None):
        self.value = value
        self.next = nxt


class Queue:
    def __init__(self) -> None:
        self.__first = None
        self.__last = None

    def isEmpty(self) -> bool:
        return not (self.__first and self.__last)

    def enqueue(self, obj) -> None:
        node = Node(obj)
        if self.isEmpty():
            self.__first = node
            self.__last = node

        else:
            self.__last.next = node
            self.__last = node

    def dequeue(self):
        if not self.__first:
            return None
        val = self.__first.value
        self.__first = self.__first.next
        if self.__first == None:
            self.__last = None
        return val

    def remove(self, obj) -> None:
        if self.isEmpty():
            return None

        node = self.__first

        last = None

        while True:
            if node.value == obj:
                if last:
                    last.next = node.next
                    if not node.next:
                        self.__last = last
                else:
                    self.__first = node.next
                break
            if node.next:
                last = node
                node = node.next
            else:
                break

    def __str__(self):
        if self.isEmpty():
            return "[]"

        string = "["
        node = self.__first

        while True:
            string += str(node.value)
            if node.next:
                string += ", "
                node = node.next
            else:
                break
        return string + "]"

class Sign:
    def __init__(self, sign: str, start: str, end: str, filepath: str) -> None:
        self.sign : str = sign
        self.time : tuple[str, str] = (start, end)
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
    
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

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

                times = (int(time_conversion_table[annotation.attrib["TIME_SLOT_REF1"]]), 
                         int(time_conversion_table[annotation.attrib["TIME_SLOT_REF2"]]))

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

                    #node = Sign(sign, ms_to_timestamp(max(times[0] - diff, 0)), ms_to_timestamp(min(times[1] + diff, int(sorted(time_conversion_table.values())[-1]))), video_file)
                    node = Sign(sign, ms_to_timestamp(times[0] - diff), ms_to_timestamp(times[1] + diff), video_file)
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

    process_queue = Queue()

    for annotation in l:
        signs = sign_dict[annotation]

        i = 1

        for sign in signs:

            process = (
                ffmpeg
                .input(sign.filepath)
                .trim(start=sign.time[0], end=sign.time[1])
                .output(f"Sign_videos/{sign.sign}_{i}.mp4")
            )

            process_queue.enqueue((process, f"Sign_videos/{sign.sign}_{i}.mp4"))

            i += 1

            process = (
                ffmpeg
                .input(sign.filepath)
                .trim(start=sign.time[0], end=sign.time[1])
                .filter('hflip')
                .output(f"Sign_videos/{sign.sign}_{i}.mp4")
            )

            process_queue.enqueue((process, f"Sign_videos/{sign.sign}_{i}.mp4"))

            i += 1

    while not process_queue.isEmpty():
        processing_list = list()

        for i in range(6):
            process_sign = process_queue.dequeue()

            if process_sign == None: continue

            processing_list.append(process_sign)

        wait_list = list()

        for process, sign in processing_list:
            print(f"Processing {sign}...")
            wait_list.append((process.run_async(pipe_stdout=False), sign))

        while wait_list:
            for process, sign in wait_list:
                poll = process.poll()
                if poll:
                    wait_list.pop(wait_list.index((process, sign)))
                    print(f"{sign} done!")
                else:
                    print(poll)
                    print(f"Waiting on {sign}...")
    return None


if __name__ == "__main__":
    main()