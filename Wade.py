print("Hello World")

from datetime import datetime
import smtplib
from email.message import EmailMessage
from pathlib import Path
from configparser import ConfigParser

# Join needs tuples
config_path = "".join( ( str(Path(__file__).parent), "/config" ) )
list_path = "".join( ( str(Path(__file__).parent), "/list.markdown" ) )
config = ConfigParser()
config.read(config_path)

today = datetime.strftime(datetime.today(), "%d.%m")
day = datetime.strftime(datetime.today(), "%d")
weekday = "day " + str(datetime.today().isoweekday())

def get_tasks():
    """Get tasks for today and create a list."""
    with open(list_path, "r") as f:
        tasks = list()
        for row in f:
            if row.startswith(today):
                # Append onetime and yearly tasks
                tasks.append(row)
            if row.startswith(day + ".XX"):
                # Append monthly tasks
                tasks.append(row)
            if row.startswith(weekday):
                # Append weekly tasks
                tasks.append(row)
    return tasks
get_tasks()

# This is used later for logging
date_now = datetime.now()

if get_tasks():
    log_text = "Tasks sent."
    host = config.get("smtp", "server")
    port = config.get("smtp", "port")
    subject = "Your personal reminder for %s" % today
    address = config.get("smtp", "to")
    sender = config.get("smtp", "from")
    text = "".join(get_tasks())

    body = "\n".join((
        "From: %s" % sender,
        "To: %s" % address,
        "Subject: %s" % subject,
        "",
        text
    ))

    server = smtplib.SMTP(host, port)
    server.starttls()
    server.ehlo()
    server.login(config.get("smtp", "login"), config.get("smtp", "password"))
    server.sendmail(sender, [address], body.encode("utf-8"))
    server.quit()
else:
    log_text = "No tasks found."

with open("/var/log/python_reminder/log", "a") as log:
    log.write("Reminder executed on %s. %s \n" % (date_now, log_text))