"""
Basic Workflow
    Single condition Variable (0-1), Single Observation Variable(0-1)
    Theorist: LinearRegression
    Experimentalist: Random Sampling
    Runner: Firebase Runner (no prolific recruitment)
"""

from autora.variable import VariableCollection, Variable
from autora.experiment_runner.firebase_prolific import firebase_runner
from autora.experimentalist.pipeline import make_pipeline
import numpy as np
from sklearn.linear_model import LinearRegression
from autora.workflow.cycle import Cycle

# *** Set up variables *** #
# independent variable is coherence (0 - 1)
# dependent variable is accuracy (0 - 1)
variables = VariableCollection(
    independent_variables=[Variable(name="x", allowed_values=range(1))],
    dependent_variables=[Variable(name="y", value_range=(-1, 1))])

# *** Set up the theorist *** #
# Here we use a linear regression as theorist, but you can use other theorists included in autora (for a list: https://autoresearch.github.io/autora/)
# Or you can set up your own theorist
theorist = LinearRegression()

# *** Set up the experimentalist *** #
# Here we use a random sampler as experimentalist, but you can use other experimentalists included in autora (for a list:  https://autoresearch.github.io/autora/)
# Or you can set up your own experimentalist
uniform_random_rng = np.random.default_rng(seed=180)


def uniform_random_sampler():
    return uniform_random_rng.uniform(low=0, high=1, size=3)


experimentalist = make_pipeline([uniform_random_sampler])

# *** Set up the runner *** #
# Here fill in your own credentials
# (https://console.firebase.google.com/)
#   -> project -> project settings -> service accounts -> generate new private key

firebase_credentials = {
    "type": "type",
    "project_id": "project_id",
    "private_key_id": "private_key_id",
    "private_key": "private_key",
    "client_email": "client_email",
    "client_id": "client_id",
    "auth_uri": "auth_uri",
    "token_uri": "token_uri",
    "auth_provider_x509_cert_url": "auth_provider_x509_cert_url",
    "client_x509_cert_url": "client_x509_cert_url"
}

# simple experiment runner that runs the experiment on firebase
experiment_runner = firebase_runner(
    firebase_credentials=firebase_credentials,
    time_out=100,
    sleep_time=5)

# *** Set up the cycle *** #
cycle = Cycle(
    variables=variables,
    theorist=theorist,
    experimentalist=experimentalist,
    experiment_runner=experiment_runner,
    monitor=lambda state: print(f"Generated {len(state.models)} models"))

# run the cycle (we will be running 3 cycles with 3 conditions each)
cycle.run(num_cycles=3)


# *** Report the data *** #
# If you changed the theorist, also change this part
def report_linear_fit(m: LinearRegression, precision=4):
    s = f"y = {np.round(m.coef_[0].item(), precision)} x " \
        f"+ {np.round(m.intercept_.item(), 4)}"
    return s


print(report_linear_fit(cycle.data.models[0]))
print(report_linear_fit(cycle.data.models[-1]))
