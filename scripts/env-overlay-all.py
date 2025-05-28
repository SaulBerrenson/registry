import subprocess
import os
import time
import sys


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PORTS_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, '../ports')


def main():
    start_time = time.time()

    # Assume each directory in ${VCPKG_ROOT}/ports is a different port
    port_names = [item for item in os.listdir(
        PORTS_DIRECTORY) if os.path.isdir(os.path.join(PORTS_DIRECTORY, item))]
    port_names.sort()

    if sys.platform == 'win32':
        env_value = ';'.join([os.path.join(PORTS_DIRECTORY, ele)
                              for ele in port_names])
        subprocess.run(["powershell", "-c",
                        f"[Environment]::SetEnvironmentVariable('VCPKG_OVERLAY_PORTS', '{env_value}','User')"])
    else:
        with open(os.path.join(SCRIPT_DIRECTORY, 'env-overlay-all.sh'), 'w') as f:
            env_value = ':'.join([os.path.join(PORTS_DIRECTORY, ele)
                                  for ele in port_names])
            f.write(f'export VCPKG_OVERLAY_PORTS="{env_value}"')


if __name__ == "__main__":
    main()
