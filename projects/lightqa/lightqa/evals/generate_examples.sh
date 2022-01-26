# Light-dialog-wild
python parlai_internal/projects/light/lightqa/seq2seq2seq/scripts/stacked_agent_eval.py \
-t light_dialog_wild \
-dt test -bs 1 -n 100 \
--mutators flatten,self_say_once \
--interactive true --random-order false --verbose true \
--knowledge-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model \
--drm-beam-min-length 10 --drm-beam-size 3 --krm-beam-size 3 --drm-beam-context-block-ngram 3 --beam-filter-for-knowledge-response true \
--dialogue-response-no-knowledge-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_7_Thu_Sep_09_1235/1c7/model \
--drmnk-beam-min-length 10 --drmnk-beam-size 3 --drmnk-beam-context-block-ngram 3

# SummaryQA
python parlai_internal/projects/light/lightqa/seq2seq2seq/scripts/stacked_agent_eval.py \
-t parlai_internal.projects.light.lightqa.lightqa.task.agents:SummaryQATeacher \
-dt test -bs 1 -n 100 \
--mutators flatten,self_say_once \
--interactive true --random-order false --verbose true \
--knowledge-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model \
--drm-beam-min-length 10 --drm-beam-size 3 --krm-beam-size 3 --drm-beam-context-block-ngram 3 --beam-filter-for-knowledge-response true \
--dialogue-response-no-knowledge-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_7_Thu_Sep_09_1235/1c7/model \
--drmnk-beam-min-length 1 --drmnk-beam-size 3 --drmnk-beam-context-block-ngram 3 \
--dialogue-response-rag-wiki-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/974/model \
--drmrw-beam-min-length 10 --drmrw-beam-size 3 --drmrw-beam-context-block-ngram 3
