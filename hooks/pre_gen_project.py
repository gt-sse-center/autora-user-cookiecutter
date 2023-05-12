import subprocess
 
subprocess.run(['npx', 'create-react-app', '{{ cookiecutter.__test_subject_environment }}', '--template', 'autora-firebase'])
subprocess.run(['npm', 'install', '-g', 'firebase-tools'])
subprocess.run(['cd', '{{ cookiecutter.__test_subject_environment }}'])
subprocess.run(['firebase', 'init'])
