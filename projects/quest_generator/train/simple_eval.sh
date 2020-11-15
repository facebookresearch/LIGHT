

#parlai i -mf /checkpoint/light/quest_generator/models/sw1/dda_jobid=4/model.checkpoint --inference beam --beam-context-block-ngram 3  --beam-block-ngram 3  --beam-size 10 --beam-min-length 20 -dt valid


#parlai display_model -t fromfile:fromfile_datapath=/checkpoint/light/quest_generator/v1/valid.txt -mf /checkpoint/light/quest_generator/models/sw1/dda_jobid=4/model.checkpoint --inference beam --beam-context-block-ngram 3  --beam-block-ngram 3  --beam-size 10 --beam-min-length 20 -ne 20 -dt valid > /checkpoint/light/quest_generator/models/sw1/dda_jobid=4/model.valid_examples


#parlai display_model -t fromfile:fromfile_datapath=/checkpoint/light/quest_generator/v1/valid.txt -mf /checkpoint/light/quest_generator/models/sw1/514_jobid=3/model.checkpoint --inference beam --beam-context-block-ngram 3  --beam-block-ngram 3  --beam-size 10 --beam-min-length 20 -ne 20 -dt valid > /checkpoint/light/quest_generator/models/sw1/514_jobid=3/model.valid_examples

parlai display_model -t fromfile:fromfile_datapath=/checkpoint/light/quest_generator/v1/valid.txt -mf /checkpoint/light/quest_generator/models/sw1/51b_jobid=2/model.checkpoint --inference beam --beam-context-block-ngram 3  --beam-block-ngram 3  --beam-size 10 --beam-min-length 20 -ne 20 -dt valid > /checkpoint/light/quest_generator/models/sw1/51b_jobid=2/model.valid_examples

 parlai display_model -t fromfile:fromfile_datapath=/checkpoint/light/quest_generator/v1/valid.txt -mf /checkpoint/light/quest_generator/models/sw1/d9f_jobid=1/model.checkpoint --inference beam --beam-context-block-ngram 3  --beam-block-ngram 3  --beam-size 10 --beam-min-length 20 -ne 20 -dt valid > /checkpoint/light/quest_generator/models/sw1/d9f_jobid=1/model.valid_examples
