import subprocess
import sys, os
    
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    with open("requirements.txt", encoding="UTF-16 LE") as file:
        start = True
        for requirement in file:
            if start:
                requirement = requirement[7:]
                start = not start
            try:
                install(requirement.strip())
            except Exception:
                print(requirement)

if __name__ == "__main__":
    main()