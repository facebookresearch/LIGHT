# Experiments

## Wizard of Wikipedia
### Models
```
## Baselines

# BART
/checkpoint/light/projects/lightqa/wow/models/wow_baseline_bart/model
# BART RAG DPR
/checkpoint/light/projects/lightqa/wow/models/wow_baseline_bart_rag_dpr/model


## K2R

# Knowledge Response Model (BART RAG DPR)
/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model
# Dialogue Response Model (BART)
/checkpoint/light/projects/lightqa/wow/models/wow_drm_bart/model
# Confidence Score conditioned Dialogue Response Model (BART)
/checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model
# Shared Model (BART RAG DPR): can be used as both Knowledge Response Model and Dialogue Response Model
/checkpoint/light/projects/lightqa/wow/models/wow_krm_drm_shared_bart_rag_dpr/model
```
### Evaluation
```
# Baselines

# Regenerate baseline results with
python parlai_internal/projects/light/lightqa/wow/evals/final_evals/baseline_1.py


# K2R

# Regenerate K2R results with (includes confidence score conditioned results)
python parlai_internal/projects/light/lightqa/wow/evals/final_evals/s2s2s_1.py

# Generate examples
python parlai_internal/projects/light/lightqa/wow/evals/generate_examples.sh
```

## Natural Questions
### Models
```
## Baselines

# BART
/checkpoint/light/projects/lightqa/nq_open/models/nq_baseline_bart/model
# BART RAG DPR
/checkpoint/light/projects/lightqa/nq_open/models/nq_baseline_bart_rag_dpr/model


## K2R

# Knowledge Response Model (T5 QA Model trained on NQ)
/checkpoint/light/projects/lightqa/nq_open/models/nq_krm_t5/model

# Dialogue Response Model (BART)
/checkpoint/light/projects/lightqa/nq_open/models/nq_drm_bart/model
```
### Evaluation
```
# Baselines

# Regenerate baseline results with
python parlai_internal/projects/light/lightqa/nq_open/evals/final_evals/baseline_1.py


# K2R

# Regenerate K2R results with
python parlai_internal/projects/light/lightqa/nq_open/evals/final_evals/s2s2s_1.py

# Generate examples
python parlai_internal/projects/light/lightqa/nq_open/evals/generate_examples.sh
```


## LIGHT/LIGHTQA
### Models
```
## Baselines

# BART trained on light-dialog-wild (no knowledge).
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_light/model
# BART trained on summaryQA.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_summaryqa/model
# BART trained on light-dialog-wild (no knowledge) and summaryQA.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_light_and_summaryqa/model


## K2R

# Knowledge Response Model (BART)
# Trained on LIGHTNC.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light/model
# Trained on summaryQA.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_summaryqa/model
# Trained on summaryQA + LIGHTNC.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light_and_summaryqa/model
# Shared param model.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_drm_shared_bart/model

# Dialogue Response Model (BART)
# Trained on lightNC (light-dialog-wild with a noun chunk of the target utterance as knowledge).
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart/model
# Shared param model.
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_drm_shared_bart/model
# Trained with 0-10 confidence int
/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart_confidence/model

# Generate examples
python parlai_internal/projects/light/lightqa/lightqa/evals/generate_examples.sh

```
### Evaluation
```
# Baselines

# Regenerate baseline results with
python parlai_internal/projects/light/lightqa/lightqa/evals/final_evals/baseline_1.py


# K2R

# Regenerate K2R results with
python parlai_internal/projects/light/lightqa/lightqa/evals/final_evals/s2s2s_1.py

```
