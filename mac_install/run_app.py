import sys
import os
import socket
from streamlit.web import cli as stcli


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        app_path = os.path.join(sys._MEIPASS, "danceui.py")
    else:
        app_path = os.path.join(os.path.dirname(__file__), "danceui.py")

    port = str(find_free_port())
    sys.argv = [
        "streamlit", "run", app_path,
        "--server.headless", "true",
        "--server.port", port,
        "--browser.serverPort", port,
        "--global.developmentMode", "false",
    ]
    sys.exit(stcli.main())
