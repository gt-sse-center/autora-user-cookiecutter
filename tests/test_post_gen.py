from hooks.post_gen_project import create_python_environment
import os


def test_create_environment():
    python_versions = ["3.8", "3.9", "3.10", "3.11"]
    project_dir = os.path.join(os.path.realpath(os.path.curdir), '../{{ cookiecutter.__project_slug }}/researcher_hub')
    requirements_file = os.path.join(os.path.realpath(os.path.curdir),
                                     '../{{ cookiecutter.__project_slug }}/researcher_hub/requirements.txt')

    for v in python_versions:
        result = create_python_environment(v, True, project_dir, requirements_file)

        assert result is not None
