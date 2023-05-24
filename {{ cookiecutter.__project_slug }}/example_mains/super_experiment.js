// ATTENTION: To be able to import from "super-experiment", first install it in your test_subject_environment folder
// via the following command in the terminal: ``npm install super-experiment``
// this works together with the super_experiment_workflow.py in the examples/research_environment folder


import {instructions, block, createTrialSequence, accuracyBlock} from "super-experiment";

/**
 * This runs a super_experiment with coherence as condition and outputs the accuracy of the block as observation.
 * @param id (from autora: a id between 0 - number of participants per circle (can be used for between counterbalancing)
 * @param condition (from autora: the condition (in this case a single value between 0 and 1 is expected)
 * @return {Promise<*>} (to autora: the observation (in this case the average accuracy)
 */
const main = async (id, condition) => {
    // Show instructions (wait till participant presses a button)
    await instructions()
    // create a trial sequence of ten trials from a single coherence (all else being randomized, but not counterbalanced)
    const trial_sequence = createTrialSequence(10, {'coh': condition})
    // run the block with the created trial sequence
    const data = await block(trial_sequence)
    // calculate the accuracy from the data
    const observation = accuracyBlock(data)
    // return the observation
    return await observation
}

export default main