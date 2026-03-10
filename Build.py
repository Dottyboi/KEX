import subprocess
import sys, os
    
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    with open(os.getcwd().join("/requirements.txt")) as file:
        for requirement in file:
            install(requirement)

if __name__ == "__main__":
    main()