from kozo import Kozo
from resources import Resources 

def main():
    user = Kozo()
    Resources.login(user)    
    Resources.get_commands(user)

if __name__ == "__main__":
    main()
