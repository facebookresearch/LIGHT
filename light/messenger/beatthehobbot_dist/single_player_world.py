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
from parlai_internal.projects.light.beatthehobbot_dist.strategies.light_chat_strategy import LIGHTChatStrategy
import parlai_internal.projects.light.beatthehobbot_dist.utils as utils


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

# ---------- LIGHT Dungeon World -------- #
class LIGHTSinglePlayerWorld(World):
    """World that pairs one human with a LIGHT bot"""

    GAME_EMOJIS = utils.GAMEPLAY_EMOJIS

    def __init__(self, opt, human_agents, bot, scoring_bot, model, task_state=None):
        self.opt = opt
        self.debug = opt.get('is_debug', False)
        self.agent = human_agents[0]

        self.bot = bot
        self.model_opt = bot.opt
        self.delimiter = self.model_opt.get('delimiter', '\n')

        # data
        self.dialogs = []
        self.model_name = model
        self.score = 0

        # offensive / personal info detection
        self.blacklist_cnt = 0
        self.flagged_cnt = 0
        self.flagged_messages = []

        self.service_strategy: LIGHTChatStrategy = opt["service_strategy"]

        # turn control
        self.chosen_dialog = None
        self.episodeDone = False
        self.game_ended = False
        self.reported = False
        self.seen_welcome_message = False
        self.timeout = False
        self.turn = 0

        # set up personas
        self.persona = []
        self.bot_persona = []
        self.persona_question = None
        self.set_up_personas()

        self.table_prefix = 'lightbot'
        self.actingscore_agent = scoring_bot
        self._init_acting_score_agent()
        self.saw_bonus = self.agent.data.get('saw_bonus', False)
        self.characters_caught = self.agent.data.get('characters_caught')
        self.characters_caught_string = self.agent.data.get('characters_caught_string')
        self.games_played = self.agent.data.get('light_games_played', 0)
        with open(self.opt['nonsequiturs_path'], 'r') as nonseq_file:
            self.nonsequiturs = nonseq_file.readlines()
        # Store pre-computed candidates
        self.prepped_cand_scores = []
        self.first_observe = False

        if task_state is not None:
            self.load_state(task_state)
        self._log('SinglePlayerWorld initialization complete...')

    @staticmethod
    def generate_world(opt, agents, task_state=None):
        shared_bot_params = opt['shared_bot_params']
        shared_scoring_params = opt['shared_scoring_params']
        scoring_bot = create_agent_from_shared(shared_scoring_params)
        bot = create_agent_from_shared(shared_bot_params)
        model = 'reddit_polyranker'
        return LIGHTSinglePlayerWorld(
            opt=opt,
            human_agents=agents,
            bot=bot,
            model=model,
            task_state=task_state,
            scoring_bot=scoring_bot,
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
            self.full_persona[0],  # character name
            self.full_persona[1]  # character description
        )
        # observe persona
        self.agent.observe({
            'id': '',
            'text': persona_text,
        })

    def set_up_personas(self):
        self._log('Setting up personas...')
        # get human's persona
        agent_data = self.agent.data
        if agent_data.get('persona') is None:
            self.full_persona = self.opt['persona_generator'].get_persona()
            self.send_persona()
        else:
            self.full_persona = agent_data['persona']
        self._log('Human persona:\n{}'.format(self.full_persona))

        # separate name, persona description, and location information
        self.name, self.persona_text, loc1 = self.full_persona
        # get list of persona sentences
        self.persona = self.persona_text.split('. ')

        # get bot's persona
        if agent_data.get('partner_persona') is None:
            self.bot_full_persona = self.opt['persona_generator'].get_persona()
        else:
            self.bot_full_persona = agent_data['partner_persona']
        # separate name, persona description, and location information
        self.bot_name, self.bot_persona_text, loc2 = self.bot_full_persona
        # get list of persona sentences
        self.bot_persona = self.bot_persona_text.split('. ')
        # choose and observe location
        if agent_data.get('setting') is None:
            self.location = random.choice([loc1, loc2])
        else:
            self.location = agent_data['setting']

        loc_name, loc_desc = self.location.split(', ', 1)
        self.bot_persona_obs = '\n'.join(
            [
                "_task_speech",
                utils.SETTING_NAME + loc_name,
                utils.SETTING_DESC + loc_desc,
                utils.PARTNER_NAME + self.name,
                utils.SELF_NAME + self.bot_name,
                utils.SELF_PERSONA + self.bot_persona_text,
            ]
        )
        self._log('Bot persona:\n{}'.format(self.bot_full_persona))
        # Create the acting score persona
        self.acting_persona_obs = '\n'.join(
            [
                utils.SETTING_NAME + loc_name,
                utils.SETTING_DESC + loc_desc,
                utils.PARTNER_NAME + self.bot_name,
                utils.SELF_NAME + self.name,
                utils.SELF_PERSONA + self.persona_text,
            ]
        )
        self._log('Acting persona:\n{}'.format(self.acting_persona_obs))
        # Human observe location if not the same setting
        if not agent_data.get('same_setting'):
            self.observe_game_msg(
                'You have just entered the following location: *{}* \n\n{}'.format(
                    loc_name,
                    loc_desc
                )
            )

        # Human observe bot's name
        article = 'an' if self.bot_name[0] in 'aeiou' else 'a'
        self.observe_game_msg(
            f'There is {article} *{self.bot_name}* here.'
        )

    def setup_next_game(self):
        new_personas = self.opt['persona_generator'].get_personas()
        loc1, loc2 = new_personas[0][2], new_personas[1][2]
        loc1_name, loc2_name = loc1.split(', ')[0], loc2.split(', ')[0]
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

        choice = choice['text']
        if choice == loc1_option:
            self.agent.data['setting'] = loc1
            self.agent.data['partner_persona'] = new_personas[0]
            self.agent.data['persona'] = self.full_persona
        elif choice == loc2_option:
            self.agent.data['setting'] = loc2
            self.agent.data['partner_persona'] = new_personas[1]
            self.agent.data['persona'] = self.full_persona
        elif choice == new_partner_option:
            self.agent.data['setting'] = self.location
            self.agent.data['partner_persona'] = new_personas[1]
            self.agent.data['persona'] = self.full_persona
            self.agent.data['same_setting'] = True
        elif choice == exit_option:
            self.agent.data['next_task'] = 'EXIT'
        self.dialogs.append(f'CHOICE: {choice}')
        return

    def see_character(self):
        persona_text = '*You are a:* {}\n*Persona:* {}'.format(
            self.name,  # character name
            self.persona_text  # character description
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
        article = 'an' if self.bot_name[0] in 'aeiou' else 'a'
        self.observe_game_msg(
            f'There is {article} *{self.bot_name}* here.',
        )

    def pick_endgame_flash_and_award_characters(self):
        """
        Handle selecting the correct end game flash, and awarding characters
        """
        base_text = random.choice(utils.END_GAME_FLASHES)
        has_self = utils.agent_has_character(self.agent, self.full_persona[0])
        has_partner = utils.agent_has_character(self.agent, self.bot_full_persona[0])
        had_duplicate = False
        emojis = ""
        emoji_text = ""
        if self.score >= SINGLE_CATCH_THRESHOLD:
            emoji_text = random.choice(utils.SELF_CAUGHT_FLASHES)
            emojis += utils.award_agent_character(self.agent, self.full_persona[0])
            if has_self:
                had_duplicate = True
        if self.score >= DOUBLE_CATCH_THRESHOLD:
            emoji_text = random.choice(utils.PARTNER_CAUGHT_FLASHES)
            emojis += utils.award_agent_character(self.agent, self.bot_full_persona[0])
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
            flash_text = self.pick_endgame_flash_and_award_characters()
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
            flash_text = random.choice(utils.END_GAME_FLASHES)
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
        format_bot_reply = '*{}.* {}'.format(self.bot_name, bot_replies[0])
        bot_reply_message = {'id': ''}
        bot_reply_message['text'] = format_bot_reply
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

        log_data = {
            'psid': self.agent.id,
            'model_name': self.model_name,
            'score': int(self.score),
            'human_persona': check_empty(self.full_persona),
            'bot_persona': check_empty(self.bot_full_persona),
            'persona_question': self.persona_question,
            'reported': self.reported,
            'timeout': self.timeout,
            'dialogue': check_empty([self.location] + self.dialogs),
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
            'blacklist_cnt',
            'flagged_cnt',
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

        self.observe_game_msg(
            "Sorry about that! You may now continue the game."
        )

    def offload_state(self):
        """Invoked when a worker is going down and we want to transfer state to
        a new worker. When we call this, shutdown is not called so we need to
        invoke agent shutdown ourselves."""
        self.observe_game_msg(
            "Uh oh! We encountered a small problem. Please give us up to 30 "
            "seconds to resolve it. We'll tell you when you can send another "
            "message."
        )
        attrs = [
            'dialogs',
            'score',
            'blacklist_cnt',
            'chosen_dialog',
            'episodeDone',
            'game_ended',
            'flagged_cnt',
            'flagged_messages',
            'reported',
            'seen_welcome_message',
            'timeout',
            'turn',
            'persona',
            'bot_persona',
            'bot_persona_txt',
            'fake_persona',
            'persona_question',
            'location',
            'name',
            'persona_text',
            'bot_full_persona',
            'bot_name',
            'bot_persona_text',
            'bot_persona_obs',
            'prepped_cand_scores',
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
            'text': f"Bot's history:\n```{bot_history}```",
        })

    def do_game_turn(self, a, flagged):
        self.log_human_reply(a['text'])  # log human reply
        self.bot.observe(a)  # bot observe act
        score, score_message = self.get_acting_score(a['text'])
        if score > 1:
            if not self.saw_bonus and self.is_rookie_user():
                score_message = (
                    f"The dungeon master thinks your "
                    f"reply is in-character: {score_message}"
                )
                self.saw_bonus = True
                self.agent.data['saw_bonus'] = True
            self.observe_game_msg(score_message)
        self.actingscore_agent.observe(a)
        self.score += score
        self.produce_bot_reply(a, flagged)  # get and display bot messages
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
        a = self.get_act()
        if self.game_ended:
            return

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
