import subprocess
import os
import requests
from tomlkit import parse
import inquirer
import shutil
import requests
import textwrap

__sample_experiment_deps = {
    "html-button": (
        "jspsych-html-button-response.html",
        ["jsPsychHtmlButtonResponse from '@jspsych/plugin-html-button-response'"],
    ),
    "reaction-time": (
        "jspsych-serial-reaction-time.html",
        ["jsPsychSerialReactionTime from '@jspsych/plugin-serial-reaction-time'"],
    ),
    "multi-choice-survey": (
        "jspsych-survey-multi-choice.html",
        ["jsPsychSurveyMultiChoice from '@jspsych/plugin-survey-multi-choice'"],
    ),
    "multi-select-survey": (
        "jspsych-survey-multi-select.html",
        ["jsPsychSurveyMultiSelect from '@jspsych/plugin-survey-multi-select'"],
    ),
    "save-trial-parameters": (
        "save-trial-parameters.html",
        [
            "jsPsychHtmlKeyboardResponse from '@jspsych/plugin-html-keyboard-response'",
            "jsPsychHtmlButtonResponse from '@jspsych/plugin-html-button-response'",
            "jsPsychCanvasKeyboardResponse from '@jspsych/plugin-canvas-keyboard-response'",
        ],
    ),
    "lexical-decision": (
        "lexical-decision.html",
        [
            "jsPsychHtmlKeyboardResponse from '@jspsych/plugin-html-keyboard-response'",
            "jsPsychHtmlButtonResponse from '@jspsych/plugin-html-button-response'",
        ],
    ),
    "pause-unpause": (
        "pause-unpause.html",
        ["jsPsychHtmlKeyboardResponse from '@jspsych/plugin-html-keyboard-response'"],
    ),
    "canvas-slider-response": (
        "jspsych-canvas-slider-response.html",
        ["jsPsychCanvasSliderResponse from '@jspsych/plugin-canvas-slider-response'"],
    ),
}


def write_to_js(jspsych_example_name: str, output_filepath: str) -> bool:
    """Scrape js code from jspsych's GitHub examples page and write to an output file

    Args:
        jspsych_example_name (str): Name of jspsych examples. Must be a key in __sample_experiment_deps variable
        output_filepath (str): File path to write output js file to

    Returns:
        bool: True if successful, False otherwise
    """
    if jspsych_example_name not in __sample_experiment_deps.keys():
        print("Please enter a valid jspsych example name")

        return False

    try:
        response = requests.get(
            f"https://raw.githubusercontent.com/jspsych/jsPsych/main/examples/{__sample_experiment_deps[jspsych_example_name][0]}"
        )
    except Exception as e:
        print("Error: {e}")
        return False

    status = response.status_code

    if status != 200:
        print(f"Error - Unable to fetch data. Status code {status}")
        return

    response_text = response.text

    # Extract js code from between final script tags
    script_tag_onwards = response_text.split("<script>")[-1]
    js_script = textwrap.dedent(script_tag_onwards.split("</script>")[0]).strip() + "\n"
    js_script = textwrap.indent(js_script, "  ")

    # Get dependencies
    proj_deps = __sample_experiment_deps[jspsych_example_name][1]

    output_file_text = ""
    import_dep_text = ""
    comment_text = "// To use the jsPsych package first install jspsych using `npm install jspsych`\n"

    # Add import text to output file and comments instructing how to install necessary dependencies
    for dep in proj_deps:
        import_dep_text += f"import {dep}\n"

        dep_package_name = dep.split("from ")[1]
        comment_text += f"// This example uses the '{dep_package_name[17:]} plugin. Install it via `npm install {dep_package_name}`\n"

    # Build output file
    output_file_text += textwrap.dedent(comment_text)
    output_file_text += textwrap.dedent(
        """
        // Here is documentation on how to program a jspsych experiment using npm:
        // https://www.jspsych.org/7.3/tutorials/hello-world/#option-3-using-npm

        import {initJsPsych} from 'jspsych';
        import 'jspsych/css/jspsych.css'
    """
    )

    output_file_text += import_dep_text
    output_file_text += "\nconst main = async (id, condition) => {\n"
    output_file_text += js_script
    output_file_text += "} \n\nexport default main\n"

    # Write to file
    with open(output_filepath, "w") as js_file:
        js_file.write(output_file_text)

    return True


def clean_up():
    to_remove = os.path.join(os.getcwd(), "temp")
    if os.path.exists(to_remove):
        subprocess.call(["deactivate"], shell=True)
        shutil.rmtree(to_remove)


def basic_or_advanced():
    question_1 = [
        inquirer.List(
            "advanced",
            message="Do you want to use advanced features?",
            choices=["yes", "no"],
        )
    ]
    answer = inquirer.prompt(question_1)
    return answer["advanced"] == "yes"


def create_autora_hub_requirements(source_branch, requirements_file):
    # TODO: update back to AutoResearch/autora/main branch after merging necessary changes
    response = requests.get(
        f"https://raw.githubusercontent.com/varun646/autora/add-all-synthetic/pyproject.toml"
    )
    doc = parse(response.text)

    # Extract the list of dependencies from the 'all' section
    all_deps = doc["project"]["optional-dependencies"]["all"]

    # Remove the prefix and brackets from each dependency
    all_deps_clean = [s.split("[")[1].split("]")[0] for s in all_deps]

    additional_deps = []
    print(
        "In the following questions, mark the packages you want to add to requirements.txt with >SPACE< and press >RETURN< to continue"
    )
    for deps in all_deps_clean:
        type = deps.replace("all-", "")

        lst = doc["project"]["optional-dependencies"][deps]
        if lst != []:
            questions = [
                inquirer.Checkbox(
                    f"{type}",
                    message=f"Do you want to install {type}",
                    choices=lst,
                ),
            ]

            additional_deps += inquirer.prompt(questions)[f"{type}"]

    # Install packages using pip and the requirements.txt file
    with open(requirements_file, "a") as f:
        for a in additional_deps:
            f.write(f"\n{a}")

    return "autora[experiment-runner-firebase-prolific]" in additional_deps


def setup_basic(requirements_file):
    if not check_if_firebase_tools_installed():
        # Install firebase-tools
        subprocess.call(["npm", "install", "-g", "firebase-tools"], shell=True)

    subprocess.call(
        ["npx", "create-react-app", "testing_zone", "--template", "autora-firebase"]
    )
    with open(requirements_file, "a") as f:
        f.write("\nautora")
    shutil.move(f"example_mains/basic.js", "testing_zone/src/design/main.js")
    shutil.move(f"example_workflows/basic.py", "researcher_hub/autora_workflow.py")
    shutil.move(f"readmes/README_AUTORA.md", "researcher_hub/README.md")
    shutil.move(f"readmes/README_FIREBASE_basic.md", "testing_zone/README.md")

    # Remove tmps
    to_remove = os.path.join(os.getcwd(), "example_workflows")
    shutil.rmtree(to_remove)
    to_remove = os.path.join(os.getcwd(), "example_mains")
    shutil.rmtree(to_remove)
    to_remove = os.path.join(os.getcwd(), "readmes")
    shutil.rmtree(to_remove)


def create_autora_example_project():
    question_1 = [
        inquirer.List(
            "firebase",
            message="Do you want to set up a firebase experiment? (ATTENTION: Node is required for this feature)",
            choices=["yes", "no"],
        )
    ]

    answer = inquirer.prompt(question_1)

    if answer["firebase"] == "no":
        return

    if not check_if_firebase_tools_installed():
        # Install firebase-tools
        subprocess.call(["npm", "install", "-g", "firebase-tools"], shell=True)

    subprocess.call(
        ["npx", "create-react-app", "testing_zone", "--template", "autora-firebase"]
    )

    questions = [
        inquirer.List(
            "project_type",
            message="What type of project do you want to create?",
            choices=[
                "Blank",
                "JsPsych - Stroop",
                "JsPsych - RDK",
                "JsPsych - HTML Button",
                "JsPsych - Reaction Time",
                "JsPsych - Multi Choice Survey",
                "JsPsych - Multi Select Survey",
                "JsPsych - Save Trial Parameters",
                "JsPsych - Lexical Decision",
                "JsPsych - Pause/Unpause",
                "JsPsych - Canvas Slider Response",
                "SuperExperiment",
                "SweetBean",
            ],
        )
    ]

    answers = inquirer.prompt(questions)

    match answers["project_type"]:
        case "JsPsych - Stroop":
            example_file = "js_psych_stroop"
        case "JsPsych - RDK":
            example_file = "js_psych_rdk"
        case "SuperExperiment":
            example_file = "super_experiment"
        case "SweetBean":
            example_file = "sweet_bean"
        case "JsPsych - HTML Button":
            example_file = "html-button"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Reaction Time":
            example_file = "reaction-time"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Multi Choice Survey":
            example_file = "multi-choice-survey"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Multi Select Survey":
            example_file = "multi-select-survey"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Save Trial Parameters":
            example_file = "save-trial-parameters"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Lexical Decision":
            example_file = "lexical-decision"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Pause/Unpause":
            example_file = "pause-unpause"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case "JsPsych - Canvas Slider Response":
            example_file = "canvas-slider-response"
            write_to_js(
                jspsych_example_name=example_file,
                output_filepath=f"example_mains/{example_file}.js",
            )
        case _:
            example_file = None

    if example_file != None:
        shutil.move(
            f"example_mains/{example_file}.js", "testing_zone/src/design/main.js"
        )

        # TODO: look into which workflow file to use
        shutil.move(
            f"example_workflows/js_psych_stroop.py", "researcher_hub/autora_workflow.py"
        )
        shutil.move(f"readmes/README_AUTORA.md", "researcher_hub/README.md")

        # TODO: look into which README to use
        # shutil.move(
        #     f"readmes/README_FIREBASE_{example_file}.md", "testing_zone/README.md"
        # )

    # Remove tmps
    to_remove = os.path.join(os.getcwd(), "example_workflows")
    shutil.rmtree(to_remove)
    to_remove = os.path.join(os.getcwd(), "example_mains")
    shutil.rmtree(to_remove)
    to_remove = os.path.join(os.getcwd(), "readmes")
    shutil.rmtree(to_remove)


def check_if_firebase_tools_installed():
    try:
        # Run the command to check if firebase-tools is installed
        subprocess.check_output(["firebase", "--version"])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    source_branch = "main"
    project_directory = os.path.join(os.path.realpath(os.path.curdir), "researcher_hub")
    requirements_file = os.path.join(project_directory, "requirements.txt")
    if basic_or_advanced():
        if create_autora_hub_requirements(source_branch, requirements_file):
            create_autora_example_project()
    else:
        setup_basic(requirements_file)
    clean_up()


if __name__ == "__main__":
    main()
