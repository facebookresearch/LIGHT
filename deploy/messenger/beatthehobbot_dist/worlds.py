from parlai.core.agents import create_agent
from parlai.core.dict import DictionaryAgent

from parlai_internal.projects.light.beatthehobbot.chat_service.utils import LIGHTPersonaGenerator
import parlai_internal.chat_service.utils.misc as internal_utils
from parlai.chat_service.utils.misc import DictFrequencies
from parlai_internal.projects.light.beatthehobbot_dist.onboarding_worlds import (
    LIGHTBotOverworld,
    LIGHTBotOnboardWorld,
)
from parlai_internal.projects.light.beatthehobbot_dist.single_player_world import (
    LIGHTSinglePlayerWorld
)

from copy import deepcopy
import os
import json

def module_initialize(opt, manager):
    """Initialize the module, pulling in resources and the model file."""
    print(opt)

    service_strategy = internal_utils.get_service_strategy(opt, manager)
    opt['service_strategy'] = service_strategy

    res_path = service_strategy.fetch_resources()
    opt['offensive_lang_path'] = os.path.join(res_path, 'offensive_language.txt')
    opt['nonsequiturs_path'] = os.path.join(res_path, 'light-non-sequiturs.txt')
    opt['trainset'] = os.path.join(res_path, 'agent_to_utterance_trainset.txt')
    opt['partner_trainset'] = os.path.join(res_path, 'agent_to_utterance_partner_trainset.txt')
    opt['baseforms'] = os.path.join(res_path, 'agent_baseforms.json')

    # Polyranker model args
    opt['model_file'] = os.path.join(res_path, 'model')
    opt['override'] = {
        'no_cuda': True,
        'batchsize': 1,
        'fixed_candidates_path': os.path.join(res_path, 'light_cands.txt'),
        'interactive_mode': True,
        'candidates': 'fixed',
        'eval_candidates': 'fixed',
        'fp16': False,
        'encode_candidate_vecs': True,
        'from_speaker_bonus': 20,
        'to_speaker_bonus': 20,
    }
    
    agent_opt = {k: v for (k, v) in opt.items() if k != 'service_strategy'}
    agent = create_agent(agent_opt)
    shared_params = agent.share()
    opt['shared_bot_params'] = shared_params

    # Scoring agent model args
    opt['shared_scoring_params'] = shared_params.copy()
    opt['shared_scoring_params']['opt'] = shared_params['opt'].copy()
    opt['shared_scoring_params']['opt']['use_reply'] = 'none'
    opt['shared_scoring_params']['opt']['override'] = opt['override'].copy()
    opt['shared_scoring_params']['opt']['override']['use_reply'] = 'none'

    # Rest of LIGHT setup
    opt['persona_generator'] = LIGHTPersonaGenerator(
        path=os.path.join(res_path, 'personas.json')
    )

    # Build a dictionary for use in OffensiveLanguageDetector
    dict_agent = DictionaryAgent({})
    dict_agent.load(os.path.join(res_path, 'personachat.dict'))
    dict_freqs = DictFrequencies(dict_agent.freq)

    opt['dict_freqs'] = dict_freqs
    
    opt['logger_handler'] = None  # only have single player
    with open(os.path.join(res_path, 'character_emojis.json'), 'r') as jsonfile:
        opt['all_persona_emojis'] = json.load(jsonfile)
