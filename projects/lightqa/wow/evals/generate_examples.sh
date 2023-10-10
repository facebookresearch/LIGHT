python parlai_internal/projects/light/lightqa/seq2seq2seq/scripts/stacked_agent_eval.py \
--task wizard_of_wikipedia:Generator -dt test -bs 1 -n 100 \
--interactive true --mutators flatten --random-order false --verbose true \
--drm-beam-context-block-ngram 3 --beam-disregard-knowledge-for-context-blocking false \
--knowledge-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model \
--dialogue-response-no-knowledge-model-path /checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model \
--dialogue-response-rag-wiki-model-path /private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model
