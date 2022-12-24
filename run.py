import subprocess
import os
import sys
import time
import re
try:
    import argparse  # required to be installed
except ImportError as e:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "argparse"]
    )
    time.sleep(5)

""" Run the application by service (either frontend or backend) """

parser = argparse.ArgumentParser(description='Run any of the services')
parser.add_argument('--service-name', required=True)

args = parser.parse_args()

# Get arguments
service_name = str(args.service_name)

backend_compose_file = os.path.join(
    os.getcwd(), "API/backend/mvcs/docker-compose.yml")

if service_name == "backend":
    subprocess.run(
        ["docker", "compose", "-f", backend_compose_file, "up", "-d"],
        capture_output=False,
    )
    t_end = time.time() + 60 * 2
    while time.time() < t_end:
        container_up = subprocess.run(
            ["docker", "ps", "-a"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(container_up.stdout)
        if re.match(
            r"^(?=.*\bmvcs-api-1\b)(?=.*\bUp\b).*$"
            , container_up.stdout
        ):
            subprocess.run(
                ["docker", "exec", "-i", "mvcs-api-1", "service ssh start"]
            )
            break
