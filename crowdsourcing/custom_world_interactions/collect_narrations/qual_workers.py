from mephisto.abstractions.providers.mturk.utils.script_utils import (
    # direct_allow_mturk_workers,
    direct_soft_block_mturk_workers,
)
from parlai_internal.crowdsourcing.projects.reverse_persona.utils.dataloading_utils import (
    get_block_list,
)

import os

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
print(TASK_DIRECTORY)
print(get_block_list(
        f"/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt"
    ))

# direct_soft_block_mturk_workers(
#     db,
#     get_block_list(
#         f"/private/home/alexgurung/LIGHT/crowdsourcing/custom_world_interactions/jing_allow_workers.txt"
#     ),
#     ALLOWLIST_QUAL_NAME,
#     cfg.mephisto.provider.requester_name,
# )