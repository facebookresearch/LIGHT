# Interactive Script
You can run the interactive script with the seq2seq2seq model in the following way:

```
python scripts/examples/light_interactive.py \
--model-file "" \
--model parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent \
--knowledge-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model \
--drm-beam-min-length 10 --drm-beam-size 3 --krm-beam-size 3 --drm-beam-block-ngram 3 \
--beam-filter-for-knowledge-response true
```