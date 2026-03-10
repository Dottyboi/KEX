import subprocess
import sys, os
    
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    with open("requirements.txt", encoding="UTF-16 LE") as file:
        file[0] = file[0][7:]
        for requirement in file:
            try:
                install(requirement.strip())
            except Exception:
                print(requirement)

if __name__ == "__main__":
    main()