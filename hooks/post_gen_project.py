import subprocess
import os
import sys
import requests
from tomlkit import parse
import inquirer
import shutil




def clean_up():
    venv_dir = os.path.join(os.getcwd(), 'temp/venv')
    to_remove = os.path.join(os.getcwd(), 'temp')

    # Deactivate the virtual environment
    if sys.platform.startswith('win'):
        deactivate_command = os.path.join(venv_dir, 'Scripts', 'deactivate')
    else:
        deactivate_command = os.path.join(venv_dir, 'bin', 'deactivate')

    try:
        subprocess.call(['source', deactivate_command], shell=True)
    except Exception as e:
        print(f"Error: {str(e)}")

    # Delete the virtual environment directory
    shutil.rmtree(to_remove)


def create_python_environment(version, is_prerelease, project_directory, requirements_file):
    # Get the project directory

    # Create a new virtual environment in the project directory
    venv_dir = os.path.join(project_directory, f'venv{version}')

    subprocess.run([f"python{version}", "-m", "venv", venv_dir], capture_output=True)

    # Install packages using pip and the requirements.txt file
    # Determine paths and commands based on the operating system
    if sys.platform == "win32":
        pip_exe = os.path.join(venv_dir, 'Scripts', 'pip')
        activate_command = os.path.join(venv_dir, 'Scripts', 'activate')
        print_message = f"\n\nProject setup is complete. To activate the virtual environment, run:\n\n{activate_command}\n\nOr if you're using PowerShell:\n\n. {activate_command}"
    else:
        pip_exe = os.path.join(venv_dir, 'bin', 'pip')
        activate_command = f"source {os.path.join(venv_dir, 'bin', 'activate')}"
        print_message = f"\n\nProject setup is complete. To activate the virtual environment, run:\n\n{activate_command}"
    if is_prerelease == 'yes':
        subprocess.run([pip_exe, "install", "--pre", "-r", requirements_file])
    else:
        subprocess.run([pip_exe, "install", "-r", requirements_file])

    return print_message


def create_requirement(source_branch, requirements_file):

    response = requests.get(f'https://raw.githubusercontent.com/AutoResearch/autora/{source_branch}/pyproject.toml')
    doc = parse(response.text)
    # Extract the list of dependencies from the 'all' section
    all_deps = doc["project"]["optional-dependencies"]["all"]

    # Remove the prefix and brackets from each dependency
    all_deps_clean = [s.split("[")[1].split("]")[0] for s in all_deps]

    additional_deps = []
    print(
        'In the following questions, mark the packages you want to install with >SPACE< and press >RETURN< to continue')
    for deps in all_deps_clean:
        type = deps.replace('all-', '')

        lst = doc["project"]["optional-dependencies"][deps]
        if lst != []:
            questions = [
                inquirer.Checkbox('choice',
                                  message=f"Do you want to install {type}",
                                  choices=lst,
                                  ),
            ]

            additional_deps += inquirer.prompt(questions)['choice']
    # Install packages using pip and the requirements.txt file

    with open(requirements_file, 'a') as f:
        for a in additional_deps:
            f.write(f'\n{a}')
    questions = [
        inquirer.List('prerelease',
                      message="Do you want to install the newest versions (Attention: Experimental!)?",
                      choices=['yes', 'no'],
                      ),
    ]

    answers = inquirer.prompt(questions)

    # Print a message showing how to activate the virtual environment
    return answers['prerelease'] == 'yes'


def main():
    source_branch = 'restructure/autora'
    python_version = '{{ cookiecutter.python_version }}'
    project_directory = os.path.join(os.path.realpath(os.path.curdir), 'researcher_hub')
    requirements_file = os.path.join(project_directory, 'requirements.txt')
    is_prerelease = create_requirement(source_branch, requirements_file)
    try:
        msg = create_requirement(python_version, is_prerelease, project_directory, requirements_file)
    except:
        msg = 'It is recommended to use a virtual environment in the research_hub directory.'
    clean_up()
    print(msg)


if __name__ == '__main__':
    main()
