import os
from datetime import datetime
from main import version

class Logger:
    
    def startup():
        if os.path.exists("runtime.log"):
            os.remove("runtime.log")

    def log_event(message, extra="", uinput=""):
        with open("runtime.log", "a") as log_dumper:
            base_line = f"{datetime.now()} | v{version} | Error: {message}"
            if extra == "":
                log_dumper.writelines(base_line + "\n")
            else:
                log_dumper.writelines(f"{base_line} | Additional Info: {extra} | Input: {uinput}\n")