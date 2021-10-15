# Interactive Script
You can run the interactive script with the seq2seq2seq model in the following way:

```
python scripts/examples/light_interactive.py \
--model-file "" \
--model parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent \
--knowledge-response-model-path /checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light_and_summaryqa/model \
--dialogue-response-model-path /checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart/model \
--drm-beam-min-length 10 --drm-beam-size 3 --krm-beam-size 3 --drm-beam-block-ngram 3 \
--beam-filter-for-knowledge-response true
```