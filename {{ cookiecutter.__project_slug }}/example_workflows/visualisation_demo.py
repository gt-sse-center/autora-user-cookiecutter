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
from PIL import Image

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
         axis='on', status_ax=None, status_msg=''):
    ax.clear()
    ax.axis(axis)
    if text is None:
        if x_points is not None and y_points is not None:
            ax.plot(x_points, y_points, 'bo', color='black')
        if vertical_lines is not None:
            for line_x in vertical_lines:
                ax.axvline(x=line_x, color='green', linestyle='-')
        if x_graph is not None and y_graph is not None:
            ax.plot(x_graph, y_graph, color="blue", linestyle="-")
    else:
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=12)
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    if status_ax is not None:
        status_ax.clear()
        status_ax.axis('off')
        status_ax.text(0.5, 0.5, status_msg, ha='center', va='center', fontsize=12)
        status_ax.set_aspect('equal')



# *** GET THE CONDITIONS *** #

# ** Sampling the coherences ** #

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


# ** Creating the trial sequencs ** #

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



# *** PROCESS DATA *** #

# process the raw trial data
def get_accuracy_from_observations(observations, conditions):
    accuracies = []
    # parse the string into an object
    trials = json.loads(observations)['trials']

    # for each condition calculate the accuracy
    for coherence in conditions:
        # filter the trials for the rok trials (not instruction, fixation, feedback ...
        rok_trials = [trial for trial in trials if trial['trial_type'] == 'rok']
        # filter the trials for the ones with the correct coherence (ATTENTION: Here we give a margin since
        # to account for precision loss due to conversions between different data types
        trials_coherence = [trial for trial in rok_trials if (
                (trial['coherence_movement'] < coherence * 100 + .1) and (
                trial['coherence_movement'] > coherence * 100 - .1))]
        # filter the correct trials
        rok_trials_correct = [trial for trial in trials_coherence if trial['correct']]
        # accuracy is the ratio of correct trials to all trials
        if len(trials_coherence) > 0:
            acc = len(rok_trials_correct) / len(trials_coherence)
        else:
            # Errorhandling
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
    ## Set up for the experiment
    # All conditions
    conditions_all = []
    observations_all = []
    conditions_flat = None
    observations_flat = None
    observations_pred = None

    # *** Plotting *** #
    fig = Figure()

    # blue guy subplot
    blue_guy_ax = fig.add_subplot(231, aspect='equal')
    blue_guy_ax.axis('off')
    blue_guy_img = np.asarray(Image.open('BlueGuy.png'))
    blue_guy_ax.imshow(blue_guy_img)

    # green guy subplot
    green_guy_ax = fig.add_subplot(233, aspect='equal')
    green_guy_ax.axis('off')
    green_guy_img = np.asarray(Image.open('GreenGuy.png'))
    green_guy_ax.imshow(green_guy_img)

    # status message subplot
    status_ax = fig.add_subplot(232, aspect='equal')
    status_ax.axis('off')

    # theorist subplot
    theorist_ax = fig.add_subplot(234, aspect='equal', xlim=(0, 1), ylim=(0, 1))
    theorist_ax.set_title('Theorist')

    # experiment_runner subplot
    experiment_runner_ax = fig.add_subplot(235, aspect='equal', xlim=(0, 1), ylim=(0, 1))
    experiment_runner_ax.axis('off')

    # experimentalist subplot
    experimentalist_ax = fig.add_subplot(236, aspect='equal', xlim=(0, 1), ylim=(0, 1))
    experimentalist_ax.set_title('Experimentalist')

    fig.subplots_adjust(wspace=1, hspace=.1)
    fig.set_size_inches(12, 5)

    window = tk.Tk()
    window.title('AutoRA - Closed Loop Demo')

    # Create a canvas and add your figure to it, then pack it into the window
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def experiment():
        # run the experiment (this is done in a different thread to allow for the visualisation to be synchronized
        nonlocal conditions_all, observations_all, conditions_flat, observations_flat, observations_pred
        for c in range(CYCLES):
            print(f'starting cycle {c}')
            # get the coherence list:
            print('experimentalist working...')
            conditions = get_coherences(conditions_all)

            # get the trial sequences:
            trial_sequences = get_trial_sequences(conditions[0])

            # plot the experimentalist
            for i in range(len(conditions[0])):
                time.sleep(random.random() * 2)
                plot(
                    x_points=conditions_flat, y_points=observations_flat,
                    x_graph=conditions_flat, y_graph=observations_pred,
                    vertical_lines=conditions[0][:i + 1],
                    ax=experimentalist_ax, title='Experimentalist',
                    status_ax=status_ax, status_msg='Experimentalist working')
                canvas.draw()
            time.sleep(1)

            print('experiment runner working...')
            # plot the experiment runner
            plot(ax=experiment_runner_ax, text='Collecting Data',
                 status_ax=status_ax, status_msg='Running Online Experiment', axis='off')

            canvas.draw()

            # upload the trial sequences to firebase
            send_conditions('autora', trial_sequences, FIREBASE_CREDENTIALS)

            observations = None
            # get all observations/run the online experiment
            while observations is None:
                time.sleep(10)
                # Check if all the conditions are observed.
                # Set a time out of 100s for participants that started the condition
                #             but didn't finish (after this time spots are freed)
                check_firebase = check_firebase_status("autora", FIREBASE_CREDENTIALS, 100)
                # if the observations are finished, get them as a list of strings
                if check_firebase == "finished":
                    _observation = get_observations("autora", FIREBASE_CREDENTIALS)
                    observations = [_observation[key] for key in sorted(_observation.keys())]

            # plot the theorist
            print('theorist working...')
            plot(ax=experiment_runner_ax, text='', axis='off')
            plot(ax=theorist_ax, title='Theorist', text='Analysing Data', axis='off',
                 status_ax=status_ax, status_msg='Theorist working')
            canvas.draw()

            # process the observations to accuracies
            for ob in observations:
                conditions_all.append(list(conditions[0]))
                accuracies = get_accuracy_from_observations(ob, conditions[0])
                observations_all.append(accuracies)

            # flatten the conditions_all and the observations_all
            _conditions_flat = np.ravel(conditions_all).tolist()
            _observations_flat = np.ravel(observations_all).tolist()

            # the theorist expects an array of arrays. Here we have n 1-dimensional arrays
            conditions_flat = np.array([np.array([x]) for x in _conditions_flat])
            observations_flat = np.array([np.array([x]) for x in _observations_flat])

            # data analysis with BMS theorist
            theorist = BMSRegressor(epochs=500)
            theorist.fit(conditions_flat, observations_flat)
            observations_pred = theorist.predict(conditions_flat)

            # plot the result in the theorist
            plot(
                x_points=conditions_flat, y_points=observations_flat,
                x_graph=conditions_flat, y_graph=observations_pred,
                vertical_lines=None,
                ax=theorist_ax, title='Theorist',
                status_ax=status_ax, status_msg='',
            )

            canvas.draw()

    # Run your experiment in a separate thread
    threading.Thread(target=experiment).start()

    # Start the Tkinter event loop in the main thread
    window.mainloop()


main()
#
# root.mainloop()
