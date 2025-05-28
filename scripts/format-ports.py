import os
import subprocess
import sys
import json
import time

from pathlib import Path

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PORTS_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, '../ports')


def reformat_ports():
    start_time = time.time()

    # Assume each directory in ${VCPKG_ROOT}/ports is a different port
    port_names = [item for item in os.listdir(
        PORTS_DIRECTORY) if os.path.isdir(os.path.join(PORTS_DIRECTORY, item))]
    port_names.sort()

    baseline_entries = {}
    total_count = len(port_names)
    os.chdir(PORTS_DIRECTORY)
    for i, port_name in enumerate(port_names, 1):
        port_file_path = os.path.join(PORTS_DIRECTORY, f'{port_name}', 'vcpkg.json')
        subprocess.run(f'vcpkg format-manifest \"{port_file_path}\"')

    elapsed_time = time.time() - start_time
    print(f'\nElapsed time: {elapsed_time:.2f} seconds')


def main():
    if not os.path.exists(PORTS_DIRECTORY):
        print(f'Ports directory is not exist')
        sys.exit(-1)
    reformat_ports()


if __name__ == "__main__":
    main()
