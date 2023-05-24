import subprocess
import os
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
        'In the following questions, mark the packages you want to add to requirements.txt with >SPACE< and press >RETURN< to continue')
    for deps in all_deps_clean:
        type = deps.replace('all-', '')

        lst = doc["project"]["optional-dependencies"][deps]
        if lst != []:
            questions = [
                inquirer.Checkbox(f'{type}',
                                  message=f"Do you want to install {type}",
                                  choices=lst,
                                  ),
            ]

            additional_deps += inquirer.prompt(questions)[f'{type}']

    # Install packages using pip and the requirements.txt file
    print(additional_deps)
    with open(requirements_file, 'a') as f:
        for a in additional_deps:
            f.write(f'\n{a}')

    return 'autora[experiment-runner-firebase-prolific]' in additional_deps


def create_autora_example_project():
    question_1 = [inquirer.List('firebase',
                                message="Do you want to set up a firebase experiment? (ATTENTION: Node to be installed for this feature)",
                                choices=["yes", "no"],
                                )
                  ]

    answer = inquirer.prompt(question_1)

    if answer['firebase'] == 'no':
        return

    if not check_if_firebase_tools_installed():
        # Install firebase-tools
        subprocess.call(['npm', 'install', '-g', 'firebase-tools'], shell=True)

    subprocess.call(['npx', 'create-react-app', 'testing_zone', '--template', 'autora-firebase'])

    questions = [inquirer.List('project_type',
                               message='What type of project do you want to create?',
                               choices=['Blank', 'JsPsych', 'SuperExperiment', 'SweetBean']
                               )]

    answers = inquirer.prompt(questions)

    if answers['project_type'] == 'JsPsych':
        example_file = 'js_psych'
    if answers['project_type'] == 'SuperExperiment':
        example_file = 'super_experiment'
    if answers['project_type'] == 'SweetBean':
        example_file = 'sweet_bean'

    shutil.move(f'example_mains/{example_file}.js', 'testing_zone/src/design/main.js')
    shutil.move(f'example_workflows/{example_file}.py', 'researcher_hub/autora_workflow.py')
    shutil.move('readmes/README_AUTORA.md', 'researcher_hub/README.md')
    shutil.move('readmes/README_FIREBASE.md', 'testing_zone/README.md')

    # Remove tmps
    to_remove = os.path.join(os.getcwd(), 'example_workflows')
    shutil.rmtree(to_remove)
    to_remove = os.path.join(os.getcwd(), 'example_mains')
    shutil.rmtree(to_remove)
    to_remove = os.path.join(os.getcwd(), 'readmes')
    shutil.rmtree(to_remove)


def check_if_firebase_tools_installed():
    try:
        # Run the command to check if firebase-tools is installed
        subprocess.check_output(['firebase', '--version'])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    source_branch = 'restructure/autora'
    project_directory = os.path.join(os.path.realpath(os.path.curdir), 'researcher_hub')
    requirements_file = os.path.join(project_directory, 'requirements.txt')
    if create_autora_hub_requirements(source_branch, requirements_file):
        create_autora_example_project()
    clean_up()


if __name__ == '__main__':
    main()
