# User Cookiecutter: Setting Up An AutoRA Workflow And Online Experiment

To establish a complete online closed-loop system for AutoRA, there are two key components that need to be configured:

1. AutoRA Workflow:
   - This workflow can be executed locally, on a server, or using cylc. It must have the ability to communicate with a website, allowing for the setting of new conditions and retrieval of observation data.
   - The AutoRA workflow can be customized by adding or removing AutoRA functions, such as AutoRA experimentalists or AutoRA theorists. It relies on an AutoRA Experimentation-Manager to facilitate communication.

2. Experiment Conducting Website:
   - The website serves as a platform for conducting experiments and needs to be compatible with the AutoRA workflow.
   - In this setup, we utilize a node application hosted on Firebase to serve the website.

To simplify the setup process, we provide a cookiecutter template that generates a project folder containing the following two directories:

1. Researcher-Hub:
   - This directory includes a basic example of an AutoRA workflow.
   - You can modify this example by adding or removing AutoRA functions to create a customized AutoRA workflow that suits your requirements.
   - The workflow incorporates an AutoRA Experimentation-Manager, enabling communication to the website.
   - The workflow also incorporates an AutoRA Participation-Manager, enabling recruitment of participants via Prolific

2. Testing-Zone:
   - This directory provides a basic example of a website served with Firebase, ensuring compatibility with the AutoRA workflow.

The following steps outline how to set up the project:

## Set Up The Project On The Firebase Website
To serve a website using Firebase and utilize the Firestore Database, it is necessary to set up a Firebase project. Follow the steps below to get started:

### Google Account
You'll need a Google account to use firebase. You can create one here: 
https://www.google.com/account/about/

### Firebase Project
While logged in into your Google account head over to:
https://firebase.google.com/

- Click on `Get started`
- Click on the plus sign with `add project`
- name your project and click on `continue`
- For now, we don't use Google Analytics (you can leave it enabled if you want to use it in the future)
- Click 'Create project'

### Adding A Webapp To Your Project
in your project console (in the firebase project), we now want to add an app to our project

- Click on `</>`
- name the app (can be the same as your project) and check `Also set up Firebase Hosting`
- Click on `Register app`
- Click on `Next`
- Click on `Next`
- Click on `Continue to console`

### Adding Firestore To Your project
in your project console in the left hand menu click on build and select Firestore Database

- Click on `Create database`
- Leave `Start in production mode` selected and click on `Next`
- Select a Firestore location and click on `Enable`
- To see if everything is set up correctly, in the menu click on the gear symbol next to the Project overview and select `Project settings`
- Under `Default GCP recource location` you should see the Firestore location, you've selected.
  - If you don't see the location, select one now (click on the `pencil-symbol` and then on `Done` in the pop-up window)


## Set Up The Project On Your System
To set up an AutoRA online closed-loop you need:

- `python`
- `node`

You should also consider using an IDE. We recommend: 

- PyCharm. This is a `python`-specific integrated development environment which comes with useful tools 
  for changing the structure of `python` code, running tests, etc. 
- Visual Studio Code. This is a powerful general text editor with plugins to support `python` development.

### Install `Python`

!!! success
    All contributions to the AutoRA core packages work under **python 3.8**, so we recommend using that version 
    for creating a AutoRA workflow.

You can install python:

- Using the instructions at [python.org](https://www.python.org), or
- Using a package manager, e.g.
  [homebrew](https://docs.brew.sh/Homebrew-and-Python), 
  [pyenv](https://github.com/pyenv/pyenv),
  [asdf](https://github.com/asdf-community/asdf-python), 
  [rtx](https://github.com/jdxcode/rtx/blob/main/docs/python.md),
  [winget](https://winstall.app/apps/Python.Python.3.8).

If successful, you should be able to run python in your terminal emulator like this:
```shell
python
```

...and see some output like this:
```
Python 3.11.3 (main, Apr  7 2023, 20:13:31) [Clang 14.0.0 (clang-1400.0.29.202)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
```

### Installing `Node`

!!! success
    The Firebase Website we are setting up, relies on `Node` to be installed on your system.

You can find information about how to install on the [official node website](https://nodejs.org/en)


### Create A Virtual Environment

!!! success
    We recommend setting up your virtual environment using a manager like `venv`, which creates isolated python 
    environments. Other environment managers, like 
    [virtualenv](https://virtualenv.pypa.io/en/latest/),
    [pipenv](https://pipenv.pypa.io/en/latest/),
    [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/), 
    [hatch](https://hatch.pypa.io/latest/), 
    [poetry](https://python-poetry.org), 
    are available and will likely work, but will have different syntax to the syntax shown here.

In the `<project directory>`, run the following command to create a new virtual environment in the `.venv` directory

```shell
python3 -m "venv" ".venv" 
```

!!! hint
    If you have multiple Python versions installed on your system, it may be necessary to specify the Python version when creating a virtual environment. For example, run the following command to specify Python 3.8 for the virtual environment. 
    ```shell
    python3.8 -m "venv" ".venv" 
    ```

Activate it by running
```shell
source ".venv/bin/activate"
```

### Install Dependencies

Upgrade pip:
```shell
pip install --upgrade pip
```

Install the current project development dependencies:
```shell
pip install cookiecutter
```

### Run cookiecutter

Run cookiecutter and select the basic option. 

!!! hint
    if you select advanced, there are more examples but this instruction focuses on the basic template

```shell
cookiecutter https://github.com/AutoResearch/autora-user-cookiecutter
```

## Research Hub: AutoRA Workflow
Running cookiecutter will result in two directories. The `research_hub` contains a basic template for an AutoRA workflow. 

To install the necessary dependencies, change the directory to the `research_hub` and install the requirements.

Change directory:
```shell
cd researcher_environment
```

Install the requirements:
```shell
pip install -r requirements.txt
```

You can find documentation for all parts of the AutoRA workflow in the [User Guide](https://autoresearch.github.io/autora/user-guide/)

## Testing Zone: Firebase Website

The `testing_zone` contains a basic template for a website that is compatible with the [AutoRA Experimentation Manager for Firebase](https://autoresearch.github.io/autora/user-guide/experiment-runners/experimentation-managers/firebase/) and the [AutoRA Participation Manager for Prolific](https://autoresearch.github.io/autora/user-guide/experiment-runners/recruitment-managers/prolific/).

You can find documentation on how to connect the website to an AutoRA workflow, build and deploy it in the documentation for [Firebase Integration](https://autoresearch.github.io/autora/online-experiments/firebase/)





