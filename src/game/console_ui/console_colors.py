from colorama import Fore, Style, init
init()

RESET  = "\033[0m"
CYAN   = "\033[96m"  # Active player block
YELLOW = "\033[93m"  # Placed blocks
EMPTY  = "."

PLAYER_COLOR = Fore.CYAN
PLACED_COLOR = Fore.YELLOW
RESET = Style.RESET_ALL