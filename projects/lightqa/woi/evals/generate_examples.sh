## Model Checkpoints
# Knowledge Model
KM="/checkpoint/light/projects/lightqa/woi/models/woi_fidgold/model"
# KM="oracle"
KM_MODEL_PARAMS="--krm-skip-generation false --krm-inference beam --krm-beam-size 3 --krm-beam-min-length 10 --krm-beam-block-ngram 3 --krm-beam-context-block-ngram -1"

# Dialogue Model
# BB2.7B
# DM="/checkpoint/kshuster/projects/wizard_internet/woi_sweep7_Wed_Jun__2/967/model"
#BB400m
# DM="/checkpoint/kshuster/projects/wizard_internet/woi_sweep4_Wed_Jun__2/cb2/model"
# BART
DM="/checkpoint/kshuster/projects/wizard_internet/woi_sweep5_Wed_Jun__2/58b/model"
# T5-Large
# DM="/checkpoint/kshuster/projects/wizard_internet/woi_sweep6_Wed_Jun__2/99a/model"
DM_MODEL_PARAMS="--drm-skip-generation false --drm-inference beam --drm-beam-size 3 --drm-beam-min-length 20 --drm-beam-block-ngram 3 --drm-beam-context-block-ngram -1 --beam-disregard-knowledge-for-context-blocking false"

python parlai_internal/projects/light/lightqa/seq2seq2seq/scripts/stacked_agent_eval.py \
--task internal:wizard_of_internet:WizardDialogTeacher -dt valid:stream -bs 1 -n 100 \
--speaker-tags false \
--include-checked-sentence false \
--krm-retriever-debug-index compressed \
--krm-gold-knowledge-fpath /checkpoint/komeili/projects/wizard-internet/fid_gold_docs/knowledge_doc_full-hist.jsonl \
--interactive false --mutators flatten --random-order true --verbose true \
--knowledge-response-model-path ${KM} \
--dialogue-response-model-path ${DM} \
${KM_MODEL_PARAMS} \
${DM_MODEL_PARAMS}
