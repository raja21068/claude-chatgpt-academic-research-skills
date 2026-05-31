"""Colorama setup — import once here, use everywhere."""
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    RED    = Fore.RED    + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    GREEN  = Fore.GREEN  + Style.BRIGHT
    CYAN   = Fore.CYAN
    RESET  = Style.RESET_ALL
    BOLD   = Style.BRIGHT
except ImportError:
    RED = YELLOW = GREEN = CYAN = RESET = BOLD = ""
