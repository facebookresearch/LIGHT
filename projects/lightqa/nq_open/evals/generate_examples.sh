python parlai_internal/projects/light/lightqa/seq2seq2seq/scripts/stacked_agent_eval.py \
--task parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher -dt test -bs 1 -n 100 \
--interactive true --mutators flatten --random-order false --verbose true \
--drm-beam-min-length 1 --drm-beam-size 30 \
--beam-filter-for-knowledge-response true --beam-filter-questions true --beam-filter-self-references true \
--drm-beam-context-block-ngram 5 --beam-disregard-knowledge-for-context-blocking true \
--knowledge-response-model-path /checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model \
--krm-path-to-index /private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model \
--dialogue-response-rag-wiki-model-path /private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model \
--dialogue-response-no-knowledge-model-path /checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model