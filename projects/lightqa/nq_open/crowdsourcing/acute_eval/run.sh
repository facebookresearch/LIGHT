# Eval for Seq2Seq2Seq on NQ
python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/model_eval.py \
-bs 1 -dt test -ne 150 \
--add-wow-history true \
-t parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher \
--model parlai_internal.projects.light.lightqa.seq2seq2seq.task.agents:StackedKnowledgeDialogueAgent \
--knowledge-response-model-path /checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model \
--dialogue-response-model-path /checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model \
--drm-beam-min-length 1 --drm-beam-size 30 \
--beam-filter-for-knowledge-response true --beam-filter-questions true --beam-filter-self-references true \
--drm-beam-context-block-ngram 5 \
--krm-path-to-index /private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact \
-rf /checkpoint/ladolphs/projects/light/lightqa/nq_open/crowdsource/history/nq_seq2seq2seq_no_questions_no_self.json

# Eval for no knowledge model
python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/model_eval.py \
-bs 1 -dt test -ne 150 \
--add-wow-history true \
-t parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher \
-mf /checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model \
--beam-min-length 1 --beam-size 3 --inference beam --beam_block_ngram 3 --beam_context_block_ngram -1 \
--model bart --skip-generation false -rf /checkpoint/ladolphs/projects/light/lightqa/nq_open/crowdsource/history/nq_bart_benchmark.json

# Eval for rag-wiki
python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/model_eval.py \
-bs 1 -dt test -ne 150 \
--add-wow-history true \
-t parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher \
-mf /private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model \
--beam-min-length 1 --beam-size 3 \
--skip-generation false -rf /checkpoint/ladolphs/projects/light/lightqa/nq_open/crowdsource/history/nq_rag_wiki_benchmark.json

# Eval for T5-FID QA model
python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/model_eval.py \
-bs 1 -dt test -ne 150 \
--add-wow-history true \
-t parlai_internal.projects.light.lightqa.nq_open.task.agents:NQOpenTeacher \
-mf /checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model \
--path-to-index /private/home/ladolphs/code/ParlAI/data/models/hallucination/wiki_index_exact/exact \
--indexer-type exact \
--beam-min-length 1 --beam-size 1 \
--skip-generation false -rf /checkpoint/ladolphs/projects/light/lightqa/nq_open/crowdsource/history/t5_qa_benchmark.json

# Run acute eval + analysis
python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/run.py \
conf=nq_open_knowledge

python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/run.py \
conf=nq_open_engaging

# Run acute eval + analysis LIVE
REQUESTER_NAME=leox1v
python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/run.py \
mephisto.blueprint.matchups_per_pair=100 \
conf=nq_open_knowledge mephisto/architect=heroku mephisto.provider.requester_name=${REQUESTER_NAME}

python parlai_internal/projects/light/lightqa/nq_open/crowdsourcing/acute_eval/run.py \
mephisto.blueprint.matchups_per_pair=100 \
conf=nq_open_engaging mephisto/architect=heroku mephisto.provider.requester_name=${REQUESTER_NAME}
