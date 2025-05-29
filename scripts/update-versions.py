import subprocess
import os


def main():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    subprocess.run(
        'vcpkg --x-builtin-ports-root=./ports --x-builtin-registry-versions-dir=./versions x-add-version --all --verbose --overwrite-version --skip-version-format-check', shell=True)


if __name__ == "__main__":
    main()
