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
    if sys.platform == 'win32':
        venv.create(venv_path, with_pip=True)
        activate_script = os.path.join(venv_path, 'Scripts', 'activate')
        python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        venv.create(venv_path, with_pip=True, system_site_packages=True)
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        python_executable = os.path.join(venv_path, 'bin', 'python')

    # Activate the virtual environment
    if sys.platform.startswith('win'):
        subprocess.call(['cmd.exe', '/c', activate_script])
    else:
        subprocess.call(['source', activate_script], shell=True)

    # Install the dependencies using pip
    subprocess.check_call([python_executable, "-m", "pip", "install", *missing_packages])


if __name__ == '__main__':
    # Call the function to run the post-gen script
    setup()
