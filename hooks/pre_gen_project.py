import os
import subprocess
import sys
import venv


# Check if the required packages are installed, and install them if not
required_packages = ['requests', 'tomlkit', 'inquirer']
missing_packages = [pkg for pkg in required_packages if pkg not in sys.modules]


def setup():
    # Define the name and location of the virtual environment
    venv_dir = 'temp/venvTmp'
    venv_path = os.path.join(os.getcwd(), venv_dir)

    # Create the virtual environment
    if 'VIRTUAL_ENV' not in os.environ:
        if sys.platform == 'win32':
            venv.create(venv_path, with_pip=True)
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
            python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
            subprocess.call(['cmd.exe', '/c', activate_script])
        else:
            venv.create(venv_path, with_pip=True, system_site_packages=True)
            activate_script = os.path.join(venv_path, 'bin', 'activate')
            python_executable = os.path.join(venv_path, 'bin', 'python')
            subprocess.call(f"source {activate_script}", shell=True)
    else:
        python_executable = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'python')

    # Install the dependencies using pip
    subprocess.check_call([python_executable, "-m", "pip", "install", *required_packages])


if __name__ == '__main__':
    # Call the function to run the post-gen script
    setup()
