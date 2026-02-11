import re, os

def extract_signs(sign_dict : dict, filepath : str):
    annotation_start = re.compile('.*<ALIGNABLE_ANNOTATION ANNOTATION_ID=".*"$')

    with open(filepath, "r+", encoding="UTF-8") as file:
        for row in file:
            if annotation_start.match(row):
                annotation = row.split('"')[1]
                row1 = next(file)
                time = re.compile(".*TIME_SLOT")
                if not time.match(row1):
                    row1 = next(file)
                times = row1.split('"')
                start = times[1]
                end = times[3]
                row2 = next(file)
                try:
                    sign = re.findall(">.*<", row2)[0][1:-1]
                except IndexError:
                    row3 = next(file)
                    sign = re.findall(">.*<", row2[:-1]+row3)[0][1:-1]
                
                if " " in sign or "^" in sign or "#" in sign:
                    continue

                if sign in sign_dict.keys():
                    sign_dict[sign].append((annotation, start, end))
                else:
                    sign_dict[sign] = [(filepath, annotation, start, end)]

def main():
    sign_dict = dict()
    for i in range(1, 409):
        filepath = f"SSLC\Eaf files annotations 20231220\SSLC01_{i:03}.eaf"
        if os.path.exists(filepath):
            extract_signs(sign_dict, filepath)
            print(f"{i}/408 filer klara")
    l = list()
    for key in sign_dict.keys():
        l.append(key)
    l.sort(key= lambda key : len(sign_dict[key]))

    for key in l:
        print(f"{key}: {len(sign_dict[key])}")
        


if __name__ == "__main__":
    main()