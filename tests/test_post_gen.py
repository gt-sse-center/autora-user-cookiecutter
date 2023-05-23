from hooks.post_gen_project import create_python_environment
import os

def test_create_environment():
    python_versions = ["3.8", "3.9", "3.10", "3.11"]
    PROJECT_DIR = os.path.join(os.path.realpath(os.path.curdir), '../{{ cookiecutter.__project_slug }}/researcher_hub')
    REQUIREMENTS_FILE =  os.path.join(os.path.realpath(os.path.curdir), '../{{ cookiecutter.__project_slug }}/researcher_hub/requirements.txt')

    result = create_python_environment(True)

    assert result is not None