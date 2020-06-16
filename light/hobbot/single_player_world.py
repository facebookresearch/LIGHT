#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import random
import datetime
import json
import time
import math

from parlai.core.agents import create_agent_from_shared
from parlai.core.worlds import World
from light.hobbot.strategies.light_chat_strategy import LIGHTChatStrategy
import light.hobbot.utils as utils
from light.graph.structured_graph import OOGraph
from light.graph.builders.starspace_all import StarspaceBuilder
from light.graph.events.graph_events import LookEvent

# Task specific constants
GAME_OVER = ('You have ended the game. Thanks for playing!')

MAX_TURNS = 5
MAX_SCORE_POS = 100000
MAX_GAME_TIMEOUT = 1200

SAMPLE_INDS = [1, 100, 1000, 2000, 5000, 10000, 20000, 50000, 95000]
SUBSAMPLE_CANDS = -1

SINGLE_CATCH_THRESHOLD = 11
DOUBLE_CATCH_THRESHOLD = 15

ROOKIE_USER_MIN_SCORE = 40
SCORE_TO_ACT = 5

USE_ACTIONS = [
    'follow',
    'hit',
    'hug',
    'get',
    'put',
    'drop',
    'steal',
    'give',
    'wear',
    'wield',
    # 'remove',
    'eat',
    'drink',
]


def add_scoring_model(opt, model_key):
    if opt.get('shared_scoring_params') is None:
        opt['shared_scoring_params'] = {}
    bot_params = opt['shared_bot_params']
    params = bot_params[model_key]
    scoring_params = params.copy()
    scoring_params['opt'] = params['opt'].copy()
    scoring_params['opt']['use_reply'] = 'none'
    scoring_params['opt']['override'] = params['opt']['override'].copy()
    scoring_params['opt']['override']['use_reply'] = 'none'
    opt['shared_scoring_params'][model_key] = scoring_params


# ---------- LIGHT Dungeon World -------- #
class LIGHTSinglePlayerWorld(World):
    """World that pairs one human with a LIGHT bot"""

    GAME_EMOJIS = utils.GAMEPLAY_EMOJIS

    def __init__(self, opt, human_agents, bot, scoring_bot, model, use_quest=None, task_state=None):
        self.opt = opt
        self.debug = opt.get('is_debug', False)
        self.agent = human_agents[0]

        self.bot = bot
        self.model_opt = bot.opt
        self.delimiter = self.model_opt.get('delimiter', '\n')
        self.quest = use_quest
        self.quest_goal = None
        self.quest_motivation = None
        self.table_prefix = 'lightbot'

        # data
        self.dialogs = []
        self.model_name = model
        self.score = 0
        self.curr_acting_score = 0

        # offensive / personal info detection
        self.blacklist_cnt = 0
        self.flagged_cnt = 0
        self.flagged_messages = []

        # agent based state
        self.saw_bonus = self.agent.data.get('saw_bonus', False)
        self.saw_quest = self.agent.data.get('saw_quest', False)
        self.characters_caught = self.agent.data.get('characters_caught')
        self.characters_caught_string = self.agent.data.get('characters_caught_string')
        self.games_played = self.agent.data.get('light_games_played', 0)

        self.service_strategy: LIGHTChatStrategy = opt["service_strategy"]

        # turn control
        self.chosen_dialog = None
        self.episodeDone = False
        self.game_ended = False
        self.reported = False
        self.seen_welcome_message = False
        self.timeout = False
        self.first_observe = False
        self.bot_action_observe = None
        self.turn = 0

        # Store pre-computed candidates
        self.prepped_cand_scores = []

        # set up personas
        self.human_player_details = {'id': None, 'db_id': None, 'name': None, 'persona': None}
        self.bot_player_details = {'id': None, 'db_id': None, 'name': None, 'persona': None}
        self.location_details = {'id': None, 'db_id': None, 'name': None, 'description': None}
        self.graph_json = None

        with open(self.opt['nonsequiturs_path'], 'r') as nonseq_file:
            self.nonsequiturs = nonseq_file.readlines()

        if task_state is None:
            self.set_up_personas()
        else:
            self.load_state(task_state)

        self.player_node = self.graph.get_node(self.human_player_details['id'])
        self.bot_node = self.graph.get_node(self.bot_player_details['id'])
        self.user_text = self.player_node.get_prefix_view()
        self.actingscore_agent = scoring_bot
        self._init_acting_score_agent()
        self._log('SinglePlayerWorld initialization complete...')

    @staticmethod
    def generate_world(opt, agents, task_state=None):
        bot_params = opt['shared_bot_params']
        if opt.get('shared_scoring_params') is None:
            opt['shared_scoring_params'] = {}

        model_to_use = random.choice(list(bot_params.keys()))
        shared_bot_params = opt['shared_bot_params'][model_to_use]
        if (
            shared_bot_params['opt'].get('boring_alpha', 0) != 0 or
            shared_bot_params['opt']['override'].get('boring_alpha', 0) != 0
        ):
            if random.random() > 0.5:
                model_to_use += '_boring'
                print("Making boring version!")
            else:
                shared_bot_params = shared_bot_params.copy()
                shared_bot_params['opt'] = shared_bot_params['opt'].copy()
                shared_bot_params['opt']['boring_alpha'] = 0
                shared_bot_params['opt']['override'] = shared_bot_params['opt']['override'].copy()
                shared_bot_params['opt']['override']['boring_alpha'] = 0
        bot = create_agent_from_shared(shared_bot_params)

        scoring_model_to_use = 'orig_light_poly'
        if scoring_model_to_use not in opt['shared_scoring_params']:
            add_scoring_model(opt, scoring_model_to_use)
        shared_scoring_params = opt['shared_scoring_params'][scoring_model_to_use]
        scoring_bot = create_agent_from_shared(shared_scoring_params)

        # Determine if we're doing a quest!
        quest = None
        if agents[0].data.get('persona') is None:
            quest = random.choice(opt['available_quests'])
            
            # if agents[0].data.get('total_score') > ROOKIE_USER_MIN_SCORE:
            #     if random.random() > 0.4:
            #         quest = random.choice(opt['available_quests'])

        return LIGHTSinglePlayerWorld(
            opt=opt,
            human_agents=agents,
            bot=bot,
            model=model_to_use,
            scoring_bot=scoring_bot,
            use_quest=quest,
            task_state=task_state,
        )

    @staticmethod
    def assign_roles(agent_ids):
        return ['Player 1']

    def _init_acting_score_agent(self):
        """Initialize the special acting score agent"""
        self.actingscore_agent.observe({
            'episode_done': False,
            'text': self.acting_persona_obs,
        })

        # mark this agent as the special acting score agent
        self.actingscore_agent.actingscore = True
        # override eval step here
        self.actingscore_agent.eval_step = self.actingscore_agent.eval_step_scoresonly

        self.subsamp = SUBSAMPLE_CANDS
        if self.subsamp < 0 or self.subsamp > max(SAMPLE_INDS):
            # no subsampling
            self.SAMPLE_INDS = SAMPLE_INDS
            return

        # Subsample the candidates
        original_len = len(self.actingscore_agent.fixed_candidates)
        print(
            ' [ WARNING: Subsampling candidates for the acting '
            'score agent to {} total ]'.format(self.subsamp)
        )
        self.actingscore_agent.subsample_cands(self.subsamp)

        # now redefine sample inds appropriately ..
        ratio = original_len / self.subsamp
        self.SAMPLE_INDS = [math.floor(x / ratio) for x in SAMPLE_INDS if x > 0]

    def _log(self, text):
        if self.debug:
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('{} DEBUG (LIGHTSinglePlayerWorld): {}'.format(curr_time, text))

    def report_offensive_language(self):
        self.observe_game_msg(utils.REPORTED_OFFLANG)
        self.reported = True
        self.game_ended = True

    def has_offensive_language(self, act):
        """
        Handles just the blacklist part of checking for offensive language.
        Return true if a blacklisted word appears, false if not.
        """
        text = act['text']
        offensive_language = self.service_strategy.has_offensive_language(text, self.chosen_dialog)
        if not offensive_language:
            return False

        self._log(
            f'User sent an offensive message: {offensive_language}'
        )
        context = text
        if self.chosen_dialog is not None:
            context = '\n'.join([self.chosen_dialog, text])
        self.flagged_messages.append(context)
        self.blacklist_cnt += 1
        if self.blacklist_cnt >= 3:
            self.report_offensive_language()
        else:
            self.observe_game_msg(utils.OFFLANG)
        return True

    def check_personal_info(self, act):
        personal_info = self.service_strategy.has_personal_info(act['text'])
        if personal_info:
            self._log('User used personal information')
            self.observe_game_msg('{}\n\nPlease try again.'.format(personal_info))
            return True
        return False

    def too_much_string_overlap(self, s1, s2):
        """
        Filters for when the given strings s1 and s2 share
        more than 50% of their words, based on the length of s2
        """
        if len(s1.strip()) == 0 or len(s2.strip()) == 0:
            return False
        s1_words = set(s1.split())
        s2_words = set(s2.split())

        if len(s2_words) == 0:
            return False

        cnt = len(s1_words & s2_words)
        if (cnt / len(s2_words) > 0.5) or (len(s2_words) < 5 and cnt >= 2):
            return True
        return False

    def set_fixed_cand_scores(self):
        """
        Compute the set of scores for candidates at various score
        levels to later compare the human utterance score to
        """
        self.actingscore_agent.opt['eval_candidates'] = 'fixed'
        self.actingscore_agent.eval_candidates = 'fixed'  # set candidates
        _ = self.actingscore_agent.act()
        self.prepped_cand_scores = self.actingscore_agent.scores

    def get_pos_human_msg(self, human_msg, scores):
        """
        Get the model score of the human message and compare to fixed cands.
        """
        human_score = float(self.actingscore_agent.score_one_candidate(human_msg))
        human_rank = int((scores > human_score).sum())
        return human_rank, human_score

    def validate_human_msg(self, human_msg):
        """
        Check that human message is long enough and does not contain
        too much overlap with the dialogue history.
        """
        # check that the message is long enough
        if len(human_msg.split()) < 5:
            return False

        # check for n-gram match with context
        if self.too_much_string_overlap(
            self.actingscore_agent.history.get_history_str(), human_msg
        ):
            return False

        return True

    def get_acting_score(self, human_msg):
        """Get the score by which the ranking model would have
        ranked the given human message at based on the currently
        scored candidates
        """
        star = random.choice(utils.STAR_EMOJIS)
        if not self.validate_human_msg(human_msg):
            # NOTE: Don't waste computation here, let's return early
            return 1, f'{star} (1 star)'
        pos, score = self.get_pos_human_msg(human_msg, self.prepped_cand_scores)

        score, score_message = 1, f'{star} (1 star)'
        if pos < self.SAMPLE_INDS[1]:    # in top 100
            score, score_message = 4, f'{star}{star}{star}{star} (4 STAR!!!!)'
        elif pos < self.SAMPLE_INDS[2]:  # in top 1000
            score, score_message = 3, f'{star}{star}{star} (3 Star!!)'
        elif pos < self.SAMPLE_INDS[3]:  # in top 2000
            score, score_message = 2, f'{star}{star} (2 Star!)'
        self._log((score_message, pos, len(human_msg.split())))
        return score, score_message

    def get_act(self):
        act = None
        a = self.agent.act()
        allowed_timeout = MAX_GAME_TIMEOUT
        curr_time = time.time()
        while a is None and time.time() - curr_time < allowed_timeout:
            a = self.agent.act()
            time.sleep(0.1)
        if a is None:
            self.timeout = True
            self.game_ended = True
        else:
            act = a
        return act

    def observe_game_msg(self, txt, quick_replies=None):
        msg = {
            'id': '',
            'text': txt,
        }
        if quick_replies is not None:
            msg['quick_replies'] = quick_replies
        self.agent.observe(msg)

    def send_persona(self):
        self.agent.observe({
            'id': '',
            'text': random.choice(self.GAME_EMOJIS) * utils.EMOJI_LENGTH,
        })
        self.agent.observe({
            'id': '',
            'text': random.choice(utils.NEW_GAME_FLASHES),
        })

        persona_text = '*You are a:* {}\n*Persona:* {}'.format(
            self.human_player_details['name'],
            self.human_player_details['persona'],
        )
        # observe persona
        self.agent.observe({
            'id': '',
            'text': persona_text,
        })

    def send_quest(self):
        if not self.saw_quest:
            self.agent.data['saw_quest'] = True
            self.agent.observe({
                'id': '',
                'text': 
                    "The dungeon master is interested in "
                    "seeing how you act. You will be given "
                    "an additional motivation or goal. "
                    "Play your character well to be given "
                    "the opporunity to TAKE ACTION. Choosing "
                    "this option will give you a few actions "
                    "to select. Respond with the number of "
                    "your selected action, then continue your dialogue.",
            })
        self.agent.observe({
            'id': '',
            'text': 
                "Your character has the following motivation: "
                f"{self.quest_motivation}.",
        })

    def set_up_personas(self):
        self._log('Setting up personas...')
        agent_data = self.agent.data

        # Load up a graph
        builder = self.opt['graph_builder']
        human_player_name = None
        if self.quest is not None:
            self.graph, self.world = builder.get_graph_from_quest(self.quest)
            human_player_name = ' '.join(self.quest['data']['character'].split(' ')[1:])
        elif agent_data.get('player'):
            player = agent_data.get('player')
            location = agent_data.get('location')
            self.graph, self.world = builder.get_constrained_graph(location, player)
            human_player_name = player.split(',')[0]
        else:
            self.graph, self.world = builder.get_graph()
        self.graph_json = self.graph.to_json() # TODO do this after every action
        
        # Assign human player
        human_player = None
        available_players = list(self.graph.agents.values())
        print(available_players)
        if human_player_name is not None:
            pos_human_player = self.graph.desc_to_nodes(human_player_name)
            assert len(pos_human_player) > 0, "Could not find given player"
            human_player = pos_human_player[0]
        else:
            human_player = random.choice(available_players)
        available_players.remove(human_player)

        # Assign bot player
        bot_player = random.choice(available_players)

        self.human_player_details = {
            'id': human_player.node_id, 
            'name': human_player.name, 
            'persona': human_player.persona,
            'db_id': human_player.db_id,
        }
        self.bot_player_details = {
            'id': bot_player.node_id, 
            'name': bot_player.name, 
            'persona': bot_player.persona,
            'db_id': bot_player.db_id,
        }
        
        if agent_data.get('player') is None:
            self.send_persona()  # TODO update call

        self._log('Human persona:\n{}'.format(self.human_player_details))

        location = human_player.get_room()
        self.location_details = {
            'id': location.node_id,
            'name': location.name,
            'description': location.desc,
            'db_id': location.db_id,
        }

        self.bot_persona_obs = '\n'.join(
            [
                "_task_speech",
                utils.SETTING_NAME + self.location_details['name'],
                utils.SETTING_DESC + self.location_details['description'],
                utils.PARTNER_NAME + self.human_player_details['name'],
                utils.SELF_NAME + self.bot_player_details['name'],
                utils.SELF_PERSONA + self.bot_player_details['persona'],
            ]
        )
        self._log('Bot persona:\n{}'.format(self.bot_player_details))
        # Create the acting score persona
        self.acting_persona_obs = '\n'.join(
            [
                utils.SETTING_NAME + self.location_details['name'],
                utils.SETTING_DESC + self.location_details['description'],
                utils.PARTNER_NAME + self.bot_player_details['name'],
                utils.SELF_NAME + self.human_player_details['name'],
                utils.SELF_PERSONA + self.human_player_details['persona'],
            ]
        )
        self._log('Acting persona:\n{}'.format(self.acting_persona_obs))
        # Human observe location if not the same setting
        if not agent_data.get('same_setting'):
            character = self.player_node
            look_event = LookEvent(character)
            look_event.execute(self.world)
            room_desc = look_event.view_as(character)
            self.observe_game_msg(room_desc)

        # Send the quest
        if self.quest is not None:
            self.quest_motivation = self.quest['data']['short_motivation']
            if random.random() > 0.05:
                self.quest_motivation = self.quest['data']['mid_motivation']
            self.quest_goal = self.quest['data']['goal']
            self.human_player_details['motivation'] = self.quest_motivation
            self.send_quest()

    def setup_next_game(self):
        locs = [r for r in self.graph.rooms.values() if r.name != self.location_details['name']]
        random.shuffle(locs)
        loc1, loc2 = locs[:2]
        loc1_name, loc2_name = loc1.name, loc2.name
        loc1_option = f'Go: {loc1_name}'[:19]
        loc2_option = f'Go: {loc2_name}'[:19]
        new_partner_option = "New Partner"
        new_character_option = "New Persona"
        exit_option = "EXIT"
        choice_options = [
            loc1_option,
            loc2_option,
            new_partner_option,
            new_character_option,
            exit_option
        ]
        self.observe_game_msg(
            "What would you like to do next?",
            quick_replies=choice_options
        )
        choice = self.get_act()
        while choice is None or choice['text'] not in choice_options:
            if choice is None:
                self.agent.data['next_task'] = 'EXIT'
                return

            self.observe_game_msg(
                "Please choose one of the following options",
                quick_replies=choice_options
            )
            choice = self.get_act()

        curr_persona = (
            f"{self.human_player_details['name']}. "
            f"{self.human_player_details['persona']}"
        )
        choice = choice['text']
        if choice == loc1_option:
            self.agent.data['setting'] = f"{loc1.name}. {loc1.description}"
            self.agent.data['persona'] = curr_persona
        elif choice == loc2_option:
            self.agent.data['setting'] = f"{loc2.name}. {loc2.description}"
            self.agent.data['persona'] = curr_persona
        elif choice == new_partner_option:
            self.agent.data['setting'] = (
                f"{self.location_details['name']}. "
                f"{self.location_details['description']}"
            )
            self.agent.data['persona'] = curr_persona
            self.agent.data['same_setting'] = True
        elif choice == exit_option:
            self.agent.data['next_task'] = 'EXIT'
        self.dialogs.append(f'CHOICE: {choice}')
        return

    def see_character(self):
        persona_text = '*You are a:* {}\n*Persona:* {}'.format(
            self.human_player_details['name'],  # character name
            self.human_player_details['persona'],  # character description
        )
        loc_name, loc_desc = self.location.split('. ', 1)
        # Observe character
        self.observe_game_msg(
            'Please play the following character:\n\n{}'.format(persona_text)
        )
        # Observe location
        self.observe_game_msg(
            'Recall that you have entered the following location: *{}* \n\n{}'.format(
                loc_name,
                loc_desc
            )
        )
        # Observe bot's name
        article = 'an' if self.bot_player_details['name'][0] in 'aeiou' else 'a'
        self.observe_game_msg(
            f'There is {article} *{self.bot_player_details["name"]}* here.',
        )

    def pick_endgame_flash_and_award_characters(self):
        """
        Handle selecting the correct end game flash, and awarding characters
        """
        base_text = random.choice(utils.END_GAME_FLASHES)
        has_self = utils.agent_has_character(self.agent, self.human_player_details['name'])
        has_partner = utils.agent_has_character(self.agent, self.bot_player_details['name'])
        had_duplicate = False
        emojis = ""
        emoji_text = ""
        if self.score >= SINGLE_CATCH_THRESHOLD:
            emoji_text = random.choice(utils.SELF_CAUGHT_FLASHES)
            emojis += utils.award_agent_character(self.agent, self.human_player_details['name'])
            if has_self:
                had_duplicate = True
        if self.score >= DOUBLE_CATCH_THRESHOLD:
            emoji_text = random.choice(utils.PARTNER_CAUGHT_FLASHES)
            emojis += utils.award_agent_character(self.agent, self.bot_player_details['name'])
            if has_partner:
                had_duplicate = True
        flash_text = base_text + emoji_text + emojis
        if had_duplicate:
            flash_text += ' ' + random.choice(utils.ALREADY_CAUGHT_FLASHES)
        if len(emojis) > 0:
            # Update awarded characters
            self.service_strategy.update_character_collection(
                self.agent.id,
                self.agent.data['characters_caught_string'],
            )
            characters_so_far = utils.get_awarded_character_count(self.agent)
            badges = "badges" if characters_so_far != 1 else "badge"
            flash_text += f"\nYou've collected {characters_so_far} {badges} so far."
        return flash_text

    def end_of_game(self):
        self._log('Game is over, handling cleanup')
        # Clear state from this game
        for prop in ['setting', 'partner_persona', 'persona', 'same_setting']:
            if prop in self.agent.data:
                del self.agent.data[prop]
        if self.agent.data.get('next_task') != 'EXIT':
            self.agent.data['next_task'] = None
        if self.timeout:  # if timeout
            flash_text = random.choice(utils.GAME_TIMEOUT_FLASHES)
            if self.score > 0:
                final_text = (
                    f"{flash_text}\n"
                    f"Your score increased by {self.score} points "
                    "from your role-playing skills!"
                )
                self.observe_game_msg(final_text)
            else:
                self.observe_game_msg(flash_text)
            self.agent.data['next_task'] = 'EXIT'
        elif self.reported:  # if reported
            pass
        elif not self.game_ended:
            flash_text = self.pick_endgame_flash_and_award_characters()
            final_text = (
                f"{flash_text}\n"
                f"Your score increased by {self.score} points "
                "from your role-playing skills!"
            )
            self.observe_game_msg(final_text)
            self.update_leaderboard()
            self.agent.data['next_task'] = 'SinglePlayer'
            self.setup_next_game()
            return
        else:  # if user clicked end game
            self.observe_game_msg(GAME_OVER)
        # update and view leaderboard
        self.update_leaderboard()

    def update_leaderboard(self, print_board=True):
        self._log('Updating leaderboard.')
        psid = self.agent.id
        score = int(self.score)
        username = self.agent.data['user_name']

        self.service_strategy.update_leaderboard(psid, score=score, username=username)
        leaderboard_stats = self.service_strategy.get_player_leaderboard_stats(psid)

        rank_msg = 'Your *rank* is {} out of {}.\n'.format(
            leaderboard_stats['rank'], leaderboard_stats['total_players'])
        score_msg = 'Your *total score* is {}.'.format(leaderboard_stats['score'])
        self.observe_game_msg(rank_msg + score_msg)

        if print_board:
            leaderboard = self.service_strategy.get_top_n_leaderboard(num_rows=5)
            text = []
            for i, tup in enumerate(leaderboard):
                text.append('{}. {}: {}'.format(i + 1, tup[1], tup[2]))
            display_text = '\n'.join(text)
            self.agent.observe(
                {'id': 'LEADERBOARD', 'text': '\n' + display_text}
            )
            return
        return

    def log_human_reply(self, text):
        self.dialogs.append('Human: {}'.format(text))

    def observe_welcome_msg(self):
        self.observe_game_msg(utils.SINGLE_PLAYER_WELCOME)

    def report_bot(self):
        self._log('User has reported bot...')
        self.observe_game_msg(utils.REPORT_BOT)
        self.reported = True
        self.game_ended = True

    def spacing_fix(self, text):
        error_list = [(' .', '.'), (' !', '!'), (' ?', '?'), (' ,', ','),
                      ("'", "")]
        for tup in error_list:
            text = text.replace(tup[0], tup[1])
        return text

    def produce_bot_reply(self, act, flagged=False):
        """Creates and chooses a bot message."""
        if not flagged:
            b = self.bot.act()
            while b is None:
                b = self.bot.act()
            self._log('Got an act, reading candidates...')
            bot_cands = b['text_candidates']
        else:
            self._log('Flagged, using non-sequitur')
            b = self.bot.act()
            bot_cands = [random.choice(self.nonsequiturs)]

        bot_replies = [self.spacing_fix(x) for x in bot_cands]
        format_bot_reply = '*{}.* {}'.format(self.bot_player_details['name'], bot_replies[0])
        bot_reply_message = {'id': ''}
        bot_reply_message['text'] = format_bot_reply
        if self.quest is not None and self.curr_acting_score >= SCORE_TO_ACT:
            bot_reply_message['quick_replies'] = ['TAKE ACTION']
        self.agent.observe(bot_reply_message)

        # update dialog data
        self.dialogs.append('Bot: {}'.format(bot_replies[0]))
        self.chosen_dialog = bot_replies[0]
        self.actingscore_agent.observe({
            'text': self.chosen_dialog,
            'episode_done': False,
        })

    def save_data(self):
        self._log('Saving data...')
        # TODO: save any relevant LIGHT data here (like locations and full personas?)
        # write more information to data

        def check_empty(lst, joiner='\n'):
            if lst:
                return joiner.join(lst)
            return None

        dialog = check_empty(self.dialogs)
        if dialog is not None:
            dialog = json.dumps(self.location_details) + "\n" + dialog

        log_data = {
            'psid': self.agent.id,
            'model_name': self.model_name,
            'score': int(self.score),
            'human_persona': json.dumps(self.human_player_details),
            'bot_persona': json.dumps(self.bot_player_details),
            'persona_question': None,
            'reported': self.reported,
            'timeout': self.timeout,
            'dialogue': dialog,
            'flagged_messages': check_empty(self.flagged_messages, joiner='\t')
        }

        self._log('Logging data: {}'.format(log_data))
        return log_data

    def load_state(self, task_state=None):
        """Invoked when this world went down in the middle of a run, and it
        is loading the state from a previous world.
        """
        int_attrs = [
            'score',
            'curr_acting_score',
            'blacklist_cnt',
            'flagged_cnt',
            'games_played',
            'turn',
        ]

        prev_state = json.loads(task_state)
        for k, v in prev_state.items():
            if hasattr(self, k):
                if k in int_attrs:
                    # assure the JSON loads to an integer
                    v = int(v)
                setattr(self, k, v)
            else:
                self._log(
                    f'WARNING! World does not have attribute {k}. Not setting.'
                )

        self.graph, self.world = builder.get_graph_from_quest(self.quest)
        self.graph = OOGraph.from_json(self.graph_json)
        self.world.oo_graph = self.graph

        self.model_name = 'reconnect'
        self.observe_game_msg(
            "Sorry about that! You may now continue the game."
        )

    def offload_state(self):
        """Invoked when a worker is going down and we want to transfer state to
        a new worker. When we call this, shutdown is not called so we need to
        invoke agent shutdown ourselves."""
        # TODO update
        self.observe_game_msg(
            "Uh oh! We encountered a small problem. Please give us up to 30 "
            "seconds to resolve it. We'll tell you when you can send another "
            "message."
        )
        attrs = [
            'quest',
            'quest_goal',
            'quest_motivation',
            'dialogs',
            'score',
            'curr_acting_score',
            'blacklist_cnt',
            'flagged_cnt',
            'flagged_messages',
            'saw_bonus',
            'saw_quest',
            'characters_caught',
            'characters_caught_string',
            'games_played',
            'chosen_dialog',
            'episodeDone',
            'game_ended',
            'reported',
            'seen_welcome_message',
            'timeout',
            'first_observe',
            'bot_action_observe',
            'turn',
            'human_player_details',
            'bot_player_details',
            'location_details',
            'graph_json',
        ]

        game_state = {}
        for attr in attrs:
            if not hasattr(self, attr):
                self._log(f'WARNING! World does not have attribute `{attr}`')
            else:
                game_state[attr] = getattr(self, attr)

        game_state_json = json.dumps(game_state)

        self.agent.shutdown()
        return game_state_json

    def shutdown(self):
        if self.score > 0:
            game_data = self.save_data()
            self.service_strategy.log(game_data)
        self.agent.shutdown()

    def is_rookie_user(self):
        """
        Return true if the current user is likely
        to be unfamiliar with the game
        """
        total_score = self.agent.data.get('total_score', 0)
        total_score = total_score if total_score is not None else 0
        return total_score < ROOKIE_USER_MIN_SCORE

    def show_debug_info(self):
        """Print the bot's full history"""
        bot_history = self.bot.history.get_history_str()
        self.agent.observe({
            'id': '',
            'text': f"You are talking to a {self.model_name}",
        })
        self.agent.observe({
            'id': '',
            'text': f"Bot's history:\n```{bot_history}```",
        })

    def get_possible_events(self, return_count=6):
        """
        Return the possible events, up to the 
        amount requested. Always include the 
        goal if it's possible.
        """
        possible_events = self.world.get_possible_events(
            self.human_player_details['id'], 
            USE_ACTIONS,
        )
        possible_actions_by_name = {x.to_canonical_form(): x for x in possible_events}
        selectable_events = []
        to_select = 6
        if self.quest_goal in possible_actions_by_name:
            selectable_events.append(possible_actions_by_name[self.quest_goal])
            del possible_actions_by_name[self.quest_goal]
            to_select -= 1
        remaining_events = list(possible_actions_by_name.values())
        random.shuffle(remaining_events)
        selectable_events += remaining_events[:to_select]
        random.shuffle(selectable_events)
        return selectable_events

    def get_and_process_action(self):
        """
        Send action options to the user, and then
        have them select one.
        """
        events = self.get_possible_events()
        options = {str(i + 1): e for i, e in enumerate(events)}
        options_txt = '\n'.join(
            [f"{i}. {a.to_canonical_form()}" for i, a in options.items()]
        )
        choice_options = [i for i in options.keys()]
        self.observe_game_msg(
            "Pick one of the following actions:\n"
            f"{options_txt}",
            quick_replies=choice_options,
        )
        choice = self.get_act()
        while choice is None or choice['text'] not in choice_options:
            if choice is None:
                return

            self.observe_game_msg(
                "Please choose one of the following options",
                quick_replies=choice_options
            )
            choice = self.get_act()
            
        chosen_act = options[choice['text']]
        if chosen_act.to_canonical_form() == self.quest_goal:
            self.observe_game_msg(
                random.choice(utils.STAR_EMOJIS) * 5
            )
            self.score += 5
        
        self.dialogs.append(f"Human Act: {choice['text']}")
        chosen_act.execute(self.world)
        self.observe_game_msg(chosen_act.view_as(self.player_node))
        self.bot_action_observe = chosen_act.view_as(self.bot_node)
        self.graph_json = self.graph.to_json()
        self.curr_acting_score -= SCORE_TO_ACT

        if not self.saw_quest:
            self.observe_game_msg(
                "(After selecting an action, continue your "
                "dialogue with what you might say while doing it)"
            )

    def do_game_turn(self, player_act, flagged):
        act_text = player_act['text']
        self.log_human_reply(act_text)  # log human reply
        if self.bot_action_observe is None:
            self.bot.observe(player_act)  # bot observe act
        else:
            act_copy = player_act.copy()
            act_copy['text'] += ' ' + self.bot_action_observe
            self.bot.observe(act_copy)
            self.bot_action_observe = None
        score, score_message = self.get_acting_score(act_text)
        if score > 1:
            if not self.saw_bonus and self.is_rookie_user():
                score_message = (
                    f"The dungeon master thinks your "
                    f"reply is in-character: {score_message}"
                )
                self.saw_bonus = True
                self.agent.data['saw_bonus'] = True
            self.observe_game_msg(score_message)
        self.actingscore_agent.observe(player_act)
        self.score += score
        self.curr_acting_score += score
        self.produce_bot_reply(player_act, flagged)  # get and display bot messages
        # Clear any messages sent in a row
        a = self.agent.act()
        if a is not None:
            self.observe_game_msg(
                "*WARNING* Please only send one message at a "
                "time, others will be ignored."
            )
        while a is not None:
            a = self.agent.act()
        self.turn += 1  # update turn

    def episode_done(self):
        return self.episodeDone

    def parley(self):
        if not self.first_observe:
            if self.is_rookie_user():
                self.observe_welcome_msg()
            # bot observe persona
            self.bot.observe({
                'episode_done': False,
                'text': self.bot_persona_obs,
            })
            self.first_observe = True

        if self.game_ended or self.turn > MAX_TURNS:
            self.end_of_game()
            self.episodeDone = True
            return

        self.set_fixed_cand_scores()
        a = None
        while a is None:
            a = self.get_act()
            if self.game_ended:
                return

            if a['text'].strip() == "TAKE ACTION":
                if self.quest is None:
                    self.observe_game_msg(
                        "For now, you can only take actions when set "
                        "on a quest by the dungeon master."
                    )
                    a = None
                elif self.curr_acting_score < SCORE_TO_ACT:
                    self.observe_game_msg(
                        "You need to play your character more to take "
                        "an action in this dialogue."
                    )
                    a = None
                else:
                    self.get_and_process_action()
                    a = None

        self._log('Human is generating a reply...')
        if self.check_personal_info(a):
            return
        elif a['text'].upper() in ['END GAME', 'QUIT', 'EXIT']:
            self.game_ended = True
            self.agent.data['next_task'] = 'EXIT'
        elif a['text'].upper() == 'NEW GAME':
            self.end_of_game()
            self.episodeDone = True
            return
        elif a['text'].upper() == 'SEE CHARACTER':
            self.see_character()
        elif a['text'].upper() == 'REPORT MESSAGE':
            self.report_bot()
        elif a['text'].upper() == 'WHOLE CONVERSATION':
            self.show_whole_convo()
        elif a['text'] == "DEBUG":
            self.show_debug_info()
        else:
            if (a['text'].startswith('"')):
                self.observe_game_msg(
                    "*NOTE* Everything you type is interpreted as being said, "
                    "so there's no need to type quotation marks"
                )
            if self.has_offensive_language(a):
                return
            self.do_game_turn(a, False)