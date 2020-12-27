import modules as mod
from os import system
from pathlib import Path

def main():
    script_path = str(Path().absolute())
    system("clear")
    mod.init(script_path)
    mod.main_menu()

if __name__ == "__main__":
    main()
