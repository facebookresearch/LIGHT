# Model Scripts

These are scripts to generate automated metrics on model performance (ppl).

`run_evals_for_models.py` creates eval reports for the provided models and datatypes for the "game-setting" variation where all dropouts are set to 0 except for graph-input, essentially mimicking what the model would be shown during a playthrough. The script basically just runs the parlai `eval` commands for you, future versions could better parallelize but for now it just prevents having to run these evaluations manually.

`explore_model_ppl.py` goes through the eval reports and summarizes the ppls for each model. This script could easily be extended to do token accuracies or other metrics present in the eval reports. It sorts the resulting table by mean perplexity, and compares hyper-parameter setups to determine how many of the setups performed best when trained with/without grounding tasks (note these may not be completely fair comparisons, as more teachers likely requires different params)