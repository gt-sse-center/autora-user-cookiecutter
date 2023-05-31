""""
In this example, we want to examine the effects of the coherence in a ROK on the accuracy of participant responses.
(The ROK is a version of the RDK where orientated objects like triangles are used instead of dots, this way the objects
have an orientation which can be the same or different from the movement direction)
Each participant should do blocks of different coherences, but in each cycle the coherences are the same for each participant
The direction of the movement, and the direction of the orientation should be counterbalanced in each block.
Outline for one cycle
(1) Sample from a distribution of coherences (an array of 3 coherences for each cycle)
(2) Additional, we choose the dissimilarity sampler to avoid sampling from the same coherences
(3) convert the coherences into blocks of trials for each participant
(4) send the trial sequences to a Firstore database and wait till the participants finished the experiment
(5) get the accuracies for each coherence and pass it into a theorist
(6) use a theorist to get a model
(7) start from (1)
"""
import json
import itertools
import random
import threading

from sweetpea import Factor, CrossBlock, synthesize_trials, MinimumTrials
import sweetpea
import numpy as np
import time
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from autora.experimentalist.sampler import dissimilarity
from autora.theorist.bms import BMSRegressor
from autora.experiment_runner.experimentation_manager.firebase import send_conditions, check_firebase_status, \
    get_observations
from autora.variable import Variable, VariableCollection

# Samples before the dissimilarity sampler
RANDOM_SAMPLES = 50
# blocks per participants
BLOCKS = 3
PARTICIPANTS_PER_CYCLE = 4
CYCLES = 5

# Credentials for firebase
# (https://console.firebase.google.com/)
#   -> project -> project settings -> service accounts -> generate new private key
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "super-experiment-4ea1f",
    "private_key_id": "81ffadae31e49cef93f700e903ee587cb263325b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDQomS9N79WPG+S\nYc+lhY0SqZrnqYNjQHQy6pr+FrpYHSnthTd+++ttq3DuChpzrL9cQZnCVdpYv7AM\naW4KHoJXb/KRIVNG5DSfZcht5+xJz3R6b1bSHapbZXXpCJ+Jz4NGSy2r/+doZOq1\nYBE4bwbnqxdFJ6Xz+E7feJe+g7305BYamlNlBcmnGuLWq02MTj5Th7e+AMt66qOE\ne+45JbqqPPr5VXorrClOiBDbixTVCPRbUTyQ1LEf+8N8WgeRVDqCJNbvInr0nbmb\nNtTbLkvJZi+NdVfF+AV4Kr/c9wKzffsUcTMP/i0s0rU7BBIV6T74zw9ygbiYxK9d\nXuPAKU4dAgMBAAECggEAHfKVicipBSinLkiufPiy45EnbGX7d2F+3HkrFtpt1KyZ\nAmBrMyXXqTYg/3ZBTkXncQd0mf3nWfJoA5wVoMu403K9C6KQON6UhCXg04/lLcIi\n2tlFCeOausRRXMoxVl+MXSh47ZXN4oEL5M2doy9iuxnmvPVAP8kujyrZA06XU4Gw\nmza3zjcw3ChJ0zdLgdH1AoKJ1W3ekkH+JgDmlENnKz7/l9rIWHRqqEPhzXOPDA1p\nQe2hwJpYNSiQXzmr4uolO7JYVsuYwS2KwfhLeMxFaVula8Yfo9GDJXEjuKUXKR6r\nnCe2AxIuLMFUzTj42+LbNU+L2z+waJiCDAM9OGagSQKBgQDvtf5fVjWPMt58m4Nv\nM/GnqvQvtrZ+ZP9u1fucQaFDE6Vdfl+rI3vyWR2JMuVjSqXqju1rxCgcjifnNjj2\n+uvpTkLGKtk1IQj+n6zN8noupwIFaG9WYoSWXQ5IbLcQmg8QI8aNMrexZ7BkbBvZ\nfI7oJpK+jl/Nl6EwuTfK5WJxCQKBgQDez8rm8yUFq/GeS/FjhBLYg9ZdM+vBkw5m\n0KOBISIs6Vztgtd86P67Q3nH7wmesUhCTcp+C4bgAQ9zC/sBGdh9/+kqyRBZNxIV\nEHNy057VlLY0UxEVXwnLPKg4t990GOFH+QFmCQdXrjT2PCPBFUn0TjDhx22kDWFH\nLjJe3Pi9dQJ/Pcytx+Zx6Hk04us093Zs1s08JxDz+6IOOITyWVaSPLjT6UarY3PC\ngLh45OY6PV8BZ3dxvlbUAIilwPY5uXL3Xy7OCEkDtq7NoteHtZDN7zkfTEWgbqT3\nicxz4jgk+iK9v2t5xO1Obm5NC5bTlz6FmVRYgMgz6s0swWL+/1AkEQKBgQCfB0CS\nxkhOXAMAMMQBe2rYDoEZ1M0YRJWq3I9WwwdZdtZUz2ZuSP5HOknZYctD8NTaPhuh\nCykhCKC2RH7Ksl/KzrTlTMzWYHAPiMZd1p0vZA0IG6G91y9uV8TZdqOOgZOJgzh0\nU01iT3yNoy8ByOgX7xcEjwq6ZLJh058wBhejYQKBgCIYDiTC4hCM0c5lb0mCFvUJ\nlSycmyVcrwkOhLC3VzqKnwiOHt9JzV9t8I2aHnPwfaW2wkWX7HIecF9RbyBnEAfs\nCi1QxLgrBKAN9GRfMCM/BzZ0fSXovm0GSq9UC7/49QOoFhebNoQqf5KzMqa97tzS\nDnW0pc5wfltqBsCAGOdm\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-mddrv@super-experiment-4ea1f.iam.gserviceaccount.com",
    "client_id": "104084508309239025783",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-mddrv%40super-experiment-4ea1f.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# define variables
variables = VariableCollection(
    independent_variables=[Variable(name="coherence", allowed_values=range(1))],
    dependent_variables=[Variable(name="accuracy", value_range=range(1))])

uniform_random_rng = np.random.default_rng(seed=180)


# *** HELPER FUNCTIONS *** #

# format SweetPea generated trial sequence so it convenient to use in a jsPsych experiment
def reformat(sequence):
    num_trials = len(next(iter(sequence.values())))
    long_format = []
    for i in range(num_trials):
        trial = {}
        for key, values in sequence.items():
            trial[key] = values[i]
        long_format.append(trial)
    return long_format


# plot data to a tkinter window
def plot(x_points=None, y_points=None, vertical_lines=None, x_graph=None, y_graph=None, ax=None, text=None, title='',
         axis='on'):
    ax.clear()
    ax.axis(axis)
    if text is None:
        if x_points is not None and y_points is not None:
            ax.plot(x_points, y_points, 'bo')

        if vertical_lines is not None:
            for line_x in vertical_lines:
                ax.axvline(x=line_x, color='red', linestyle='--')

        if x_graph is not None and y_graph is not None:
            ax.plot(x_graph, y_graph, "-")
    else:
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=12)
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')


# get n samples of an 3-tuple
def run_random_sampler(n):
    return uniform_random_rng.uniform(low=0, high=1, size=(n, BLOCKS))


# sample the n most dissimilar 3-tuples in reference to X_ref
def run_dissimilarity(X, X_ref, n):
    return dissimilarity.summed_dissimilarity_sampler(X, X_ref, n)


# get the CONDITION_PER_PARTICIPANT coherences for a cycle
def get_coherences(X_ref=None):
    # on the first cycle return PARTICIPANTS_PER_CYCLE random 3-tuples
    if X_ref is None or X_ref == []:
        return run_random_sampler(1)
    # after the first cycle return the PARTICIPANTS_PER_CYCLE most dissimilar samples out of RANDOM_SAMPLES
    X_ = run_random_sampler(RANDOM_SAMPLES)
    return run_dissimilarity(X_, X_ref, 1)


# given the coherences, get a list of three trial sequences in sweetPea (https://sites.google.com/view/sweetpea-ai) for each participant
def get_trial_sequences(coherences):
    n = BLOCKS * PARTICIPANTS_PER_CYCLE

    # SweetPea: Generate n sequences that are counterbalanced for the movement and orientation
    direction_mov = Factor('dir_mov', [0, 180])
    direction_or = Factor('dir_or', [0, 180])
    design = [direction_mov, direction_or]
    crossing = [direction_mov, direction_or]
    constraints = [MinimumTrials(8)]
    block = CrossBlock(design, crossing, constraints)
    _trial_sequences = synthesize_trials(block, n)

    # SweetPea formats the trial_sequences in a way that is inconvenient for jsPsych to read, therefore we reformat:
    # Example:
    #       {dir_mov: [0, 180, 0, 180], dir_or: [180, 180, 0, 0], ...}
    #       ->
    #       [{dir_mov: 0, dir_or: 180}, {dir_mov: 180, dir_or: 180}, ...]

    _trial_sequences = [reformat(s) for s in _trial_sequences]

    # Here we split the list of trial sequences into blocks for each participant
    trial_sequences = [_trial_sequences[i:i + BLOCKS] for i in
                       range(0, len(_trial_sequences), BLOCKS)]

    # For each trial sequence we want to append the coherence of each block to each trial of that block
    for participant_list in trial_sequences:
        for i, sequence in enumerate(participant_list):
            for item in sequence:
                item['coherence'] = coherences[i]

    # the result is a list that contains a list of blocks for each participant
    return trial_sequences


def get_accuracy_from_observations(observations, conditions):
    accuracies = []
    trials = json.loads(observations)['trials']
    for coherence in conditions:
        rok_trials = [trial for trial in trials if trial['trial_type'] == 'rok']
        trials_coherence = [trial for trial in rok_trials if (
                (trial['coherence_movement'] < coherence * 100 + .1) and (
                    trial['coherence_movement'] > coherence * 100 - .1))]
        rok_trials_correct = [trial for trial in trials_coherence if trial['correct']]
        if len(trials_coherence) > 0:
            acc = len(rok_trials_correct) / len(trials_coherence)
        else:
            print(f'Warning: Something went wrong')
            print('coherence:', coherence)
            print('rok_trials:', rok_trials)
            print('trials_coherence:', trials_coherence)
            print('rok_trials_correct:', rok_trials_correct)
            acc = 0
        accuracies.append(acc)
    return accuracies


# Your plot function goes here...

def main():
    # All conditions
    conditions_all = []
    observations_all = []
    conditions_flat = None
    observations_flat = None
    observations_pred = None
    fig = Figure()
    # Add the first subplot
    ax1 = fig.add_subplot(131, aspect='equal', xlim=(0, 1), ylim=(0, 1))
    ax1.set_title('Experimentalist')
    # Add the second subplot
    ax2 = fig.add_subplot(132, aspect='equal', xlim=(0, 1), ylim=(0, 1))
    ax2.set_title('Experiment Runner')
    ax2.axis('off')
    # Add the third subplot
    ax3 = fig.add_subplot(133, aspect='equal', xlim=(0, 1), ylim=(0, 1))
    ax3.set_title('Theorist')

    fig.subplots_adjust(wspace=1)
    fig.set_size_inches(12, 5)

    window = tk.Tk()
    window.title('My Matplotlib Plot')

    # Create a canvas and add your figure to it, then pack it into the window
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def experiment():
        nonlocal conditions_all, observations_all, conditions_flat, observations_flat, observations_pred
        for c in range(CYCLES):
            print(f'starting cycle {c}')
            # get the coherence list:
            print('experimentalist working...')
            conditions = get_coherences(conditions_all)

            # get the trial sequences:
            trial_sequences = get_trial_sequences(conditions[0])
            for i in range(len(conditions[0])):
                time.sleep(random.random()*2)
                plot(
                    x_points=conditions_flat, y_points=observations_flat,
                    x_graph=conditions_flat, y_graph=observations_pred,
                    vertical_lines=conditions[0][:i+1],
                    ax=ax1, title='Experimentalist')
                canvas.draw()
            time.sleep(1)

            print('experiment runner working...')
            plot(ax=ax2, text='Collecting Data', title='Experiment Runner', axis='off')

            canvas.draw()

            # upload the trial sequences to firebase
            send_conditions('autora', trial_sequences, FIREBASE_CREDENTIALS)

            nr_dots = 0
            observations = None
            while observations is None:
                for i in range(4):
                    nr_dots += 1
                    nr_dots %= 4
                    time.sleep(random.random()*2)
                    plot(ax=ax2, text="."*nr_dots, title='Collecting Data', axis='off')
                    canvas.draw()
                # Check if all the conditions are observed.
                # Set a time out of 100s for participants that started the condition
                #             but didn't finish (after this time spots are freed)
                check_firebase = check_firebase_status("autora", FIREBASE_CREDENTIALS, 100)
                if check_firebase == "finished":
                    _observation = get_observations("autora", FIREBASE_CREDENTIALS)
                    observations = [_observation[key] for key in sorted(_observation.keys())]

            print('theorist working...')
            plot(ax=ax2, text='', title='Experiment Runner', axis='off')
            plot(ax=ax3, text='Analysing data', title='Theorist', axis='off')
            canvas.draw()

            for ob in observations:
                conditions_all.append(list(conditions[0]))
                accuracies = get_accuracy_from_observations(ob, conditions[0])
                observations_all.append(accuracies)

            # flatten the conditions_all and the observations_all
            _conditions_flat = np.ravel(conditions_all).tolist()
            _observations_flat = np.ravel(observations_all).tolist()
            # Reshape the conditions_all array to have a single column

            # make elements arrays
            conditions_flat = np.array([np.array([x]) for x in _conditions_flat])
            observations_flat = np.array([np.array([x]) for x in _observations_flat])

            # data analysis with BMS
            estimator = BMSRegressor(epochs=500)
            estimator.fit(conditions_flat, observations_flat)
            observations_pred = estimator.predict(conditions_flat)

            print(conditions_flat)
            print(observations_flat)
            print(observations_pred)

            plot(
                x_points=conditions_flat, y_points=observations_flat,
                x_graph=conditions_flat, y_graph=observations_pred,
                vertical_lines=None,
                ax=ax3, title='Theorist')

            canvas.draw()

    # Run your experiment in a separate thread
    threading.Thread(target=experiment).start()

    # Start the Tkinter event loop in the main thread
    window.mainloop()


main()
#
# root.mainloop()
