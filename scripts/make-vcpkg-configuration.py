import os
import subprocess
import sys
import json
import time

from pathlib import Path

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PORTS_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, '../ports')


def get_version_tag(version):
    if 'version' in version:
        return [version['version'], 'version']
    elif 'version-date' in version:
        return [version['version-date'], 'version-date']
    elif 'version-semver' in version:
        return [version['version-semver'], 'version-semver']
    elif 'version-string' in version:
        return [version['version-string'], 'version-string']


def get_version_port_version(version):
    if 'port-version' in version:
        return version['port-version']
    return 0

def get_current_branch():
    """Get the current git branch name"""
    result = subprocess.run('git branch --show-current', 
                          shell=True, 
                          capture_output=True, 
                          text=True)
    if result.returncode == 0:
        return result.stdout.strip()  # Use .strip() to remove newline
    else:
        return "HEAD"

def get_port_names():
    # Assume each directory in ${VCPKG_ROOT}/ports is a different port
    port_names = [item for item in os.listdir(
        PORTS_DIRECTORY) if os.path.isdir(os.path.join(PORTS_DIRECTORY, item))]
    port_names.sort()
    return port_names


def make_vcpkg_json():
    overrides = []

    port_names = get_port_names()

    for port in port_names:
        with open(os.path.join(PORTS_DIRECTORY, port, "vcpkg.json"), 'r') as json_file:
            current_json = json.load(json_file)

            if 'name' in current_json :
                pkg_name = current_json['name']
            version_kv = get_version_tag(current_json)
            revision_port = get_version_port_version(current_json)
            if revision_port == 0:
                version_pkg = version_kv[0]
            else:
                version_pkg = f'{version_kv[0]}#{revision_port}'
            version_tag = str(version_kv[1])

            override_pkg = {
                "name": pkg_name,
                f'{version_tag}': version_pkg,
            }
            overrides.append(override_pkg)

    vcpkg_json = {
        "dependencies": [
        ],
        "overrides": overrides
    }

    with open('vcpkg.json', 'w') as f:
        json.dump(vcpkg_json, f, indent=4)


def make_vcpkg_configuration():
    start_time = time.time()

    os.chdir(SCRIPT_DIRECTORY)

    port_names = get_port_names()

    git_ret = subprocess.run("git remote get-url origin --push", shell=True, capture_output=True, text=True)
    baseline_ret = subprocess.run('git rev-parse HEAD', shell=True, capture_output=True, text=True)

    if git_ret.returncode == 0:
        origin_url = str(git_ret.stdout.strip())
    else:
        origin_url = '{insert repo url}'

    if baseline_ret.returncode == 0:
        baseline_hash = str(baseline_ret.stdout.strip())
    else:
        baseline_hash = '0000000000000000000000000000000000000000'

    vcpkg_configurations = {
        "default-registry": {
            "kind": "git",
            "repository": "https://github.com/microsoft/vcpkg.git",
            "baseline": "3425f537d2f01c761d2d2cff59a7577eb4f568c0"
        },
        "registries": [
            {
                "kind": "git",
                "repository": origin_url,
                "reference": get_current_branch(),
                "packages": port_names,
                "baseline": baseline_hash
            }
        ]
    }

    print(vcpkg_configurations)

    with open('vcpkg-configuration.json', 'w') as f:
        json.dump(vcpkg_configurations, f, indent=4)

    elapsed_time = time.time() - start_time
    print(f'\nElapsed time: {elapsed_time:.2f} seconds')


def main():
    if not os.path.exists(PORTS_DIRECTORY):
        print(f'Ports directory is not exist')
        sys.exit(-1)
    make_vcpkg_configuration()
    make_vcpkg_json()


if __name__ == "__main__":
    main()
