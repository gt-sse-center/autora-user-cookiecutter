import subprocess
import os
import sys
import requests
from tomlkit import parse
import inquirer
import shutil


def clean_up():
    to_remove = os.path.join(os.getcwd(), 'temp')
    subprocess.call(['deactivate'], shell=True)
    shutil.rmtree(to_remove)


def create_autora_hub_requirements(source_branch, requirements_file):
    response = requests.get(f'https://raw.githubusercontent.com/AutoResearch/autora/{source_branch}/pyproject.toml')
    doc = parse(response.text)

    # Extract the list of dependencies from the 'all' section
    all_deps = doc["project"]["optional-dependencies"]["all"]

    # Remove the prefix and brackets from each dependency
    all_deps_clean = [s.split("[")[1].split("]")[0] for s in all_deps]

    additional_deps = []
    print(
        'In the following questions, mark the packages you want to add to your requirements with >SPACE< and press >RETURN< to continue')
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
    print(additional_deps)

    with open(requirements_file, 'a') as f:
        for a in additional_deps:
            f.write(f'\n{a}')


def main():
    source_branch = 'restructure/autora'
    project_directory = os.path.join(os.path.realpath(os.path.curdir), 'researcher_hub')
    requirements_file = os.path.join(project_directory, 'requirements.txt')
    create_autora_hub_requirements(source_branch, requirements_file)
    clean_up()


if __name__ == '__main__':
    main()
