# Eval for Seq2Seq2Seq on light_dialog_wild question subset
python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/lightqa/acute_eval/model_eval.py \
-bs 1 -dt test -ne 100 \
-t parlai_internal.projects.light.lightqa.lightqa.task.agents:LightQuestionSubsetTeacher \
--mutators flatten,self_say_once \
--model parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent \
--knowledge-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model \
--drm-beam-min-length 10 --drm-beam-size 3 --krm-beam-size 3 --beam-filter-for-knowledge-response false \
-rf /checkpoint/ladolphs/projects/light/lightqa/lightqa/crowdsource/lightqa/light_seq2seq2seq.json

# Eval for Seq2Seq2Seq (single model) on light_dialog_wild question subset
python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/lightqa/acute_eval/model_eval.py \
-bs 1 -dt test -ne 100 \
-t parlai_internal.projects.light.lightqa.lightqa.task.agents:LightQuestionSubsetTeacher \
--mutators flatten,self_say_once \
--model parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent \
--knowledge-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_12_Thu_Sep_23_1335/27b/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_12_Thu_Sep_23_1335/27b/model \
--drm-beam-min-length 10 --drm-beam-size 3 --krm-beam-size 3 --beam-filter-for-knowledge-response false \
-rf /checkpoint/ladolphs/projects/light/lightqa/lightqa/crowdsource/lightqa/light_seq2seq2seq_single.json

# Eval for no knowledge model on light_dialog_wild question subset
python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/lightqa/acute_eval/model_eval.py \
-bs 1 -dt test -ne 100 \
-t parlai_internal.projects.light.lightqa.lightqa.task.agents:LightQuestionSubsetTeacher \
--mutators flatten,self_say_once \
-mf /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_7_Thu_Sep_09_1235/7a6/model \
--beam-min-length 10 --beam-size 3 --inference beam --beam_block_ngram 3 --beam_context_block_ngram -1 \
--model bart --skip-generation false \
-rf /checkpoint/ladolphs/projects/light/lightqa/lightqa/crowdsource/lightqa/light_bart_benchmark.json

# Eval for human on light_dialog_wild question subset
python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/lightqa/acute_eval/model_eval.py \
-bs 1 -dt test -ne 100 \
-t parlai_internal.projects.light.lightqa.lightqa.task.agents:LightQuestionSubsetTeacher \
--mutators flatten,self_say_once \
-m repeat_label \
-rf /checkpoint/ladolphs/projects/light/lightqa/lightqa/crowdsource/lightqa/light_gold_label.json


# # Run acute eval + analysis
# python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/acute_eval/run.py \
# conf=lightqa_knowledge

# python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/acute_eval/run.py \
# conf=lightqa_engaging

# # Run acute eval + analysis LIVE
# REQUESTER_NAME=leox1v
# python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/acute_eval/run.py \
# mephisto.blueprint.matchups_per_pair=100 \
# conf=lightqa_knowledge mephisto/architect=heroku mephisto.provider.requester_name=${REQUESTER_NAME}

# python parlai_internal/projects/light/lightqa/lightqa/crowdsourcing/acute_eval/run.py \
# mephisto.blueprint.matchups_per_pair=100 \
# conf=lightqa_engaging mephisto/architect=heroku mephisto.provider.requester_name=${REQUESTER_NAME}
