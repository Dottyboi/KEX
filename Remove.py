import os


def main():
    folder = "Sign_pose"
    files = map(lambda x : f"{folder}/{x}" ,os.listdir(folder))

    for file in files:
        num = int(file.split("_")[-1][:-4])
        if num > 17:
            print(f"Removed {file}")
            os.remove(file)


if __name__ == "__main__":
    main()