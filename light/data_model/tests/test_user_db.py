#!/usr/bin/env python3

import unittest
from omegaconf import OmegaConf
from sqlalchemy.exc import IntegrityError
from light.data_model.db.base import LightDBConfig
from light.data_model.db.users import UserDB, PlayerStatus
from light.data_model.db.environment import EnvDB

config = LightDBConfig(backend="test", file_root="unused")


class TestUserDB(unittest.TestCase):
    """Test cases for setting up a structured graph"""

    def test_init(self):
        """Ensure we can initialize a UserDB successfully"""
        hydra_config = OmegaConf.structured(config)
        db = UserDB(config)
        self.assertIsNotNone(db)
        self.assertIsNotNone(db.engine)

    def test_create_find_users(self):
        """Ensure we can initialize players properly and find them"""
        hydra_config = OmegaConf.structured(config)
        db = UserDB(config)

        extern_id_1 = "TEST_LOGIN"
        extern_id_2 = "TEST_PREAUTH"

        # Create players

        player_id_1 = db.create_user(extern_id_1, is_preauth=False)
        player_id_2 = db.create_user(extern_id_2, is_preauth=True)

        # Assert created players as expected

        self.assertIsNotNone(player_id_1, "No player ID returned for first")
        self.assertIsNotNone(player_id_2, "No player ID returned for second")

        # Assert duplicates return same id

        player_id_3 = db.create_user(extern_id_1, is_preauth=False)
        self.assertEqual(player_id_1, player_id_3)
        player_id_4 = db.create_user(extern_id_1, is_preauth=True)
        self.assertEqual(player_id_1, player_id_4)

        # Assert can find given players, and that their values are initialized

        player_1_by_id = db.get_player(player_id_1)
        player_2_by_id = db.get_player(player_id_2)
        player_1_by_extern = db.get_player_by_extern_id(extern_id_1)
        player_2_by_extern = db.get_player_by_extern_id(extern_id_2)

        self.assertEqual(
            player_1_by_id.db_id, player_id_1, "Gotten player by ID mismatch"
        )
        self.assertEqual(
            player_1_by_extern.db_id, player_id_1, "Gotten player by extern mismatch"
        )
        self.assertEqual(
            player_1_by_id.extern_id, extern_id_1, "Gotten player by ID mismatch"
        )
        self.assertEqual(
            player_1_by_extern.extern_id,
            extern_id_1,
            "Gotten player by extern mismatch",
        )
        self.assertEqual(
            player_1_by_id.is_preauth, False, "Did not retain preauth status"
        )
        self.assertEqual(player_1_by_id.flag_count, 0, "Did not initialize flags to 0")
        self.assertEqual(
            player_1_by_id.safety_trigger_count,
            0,
            "Did not initialize safety triggers to 0",
        )
        self.assertEqual(
            player_1_by_id.total_messages, 0, "Did not intialize messages to 0"
        )
        self.assertEqual(
            player_1_by_id.account_status,
            PlayerStatus.TUTORIAL,
            "Did not initialize to tutorial",
        )

        self.assertEqual(
            player_2_by_id.db_id, player_id_2, "Gotten player by ID mismatch"
        )
        self.assertEqual(
            player_2_by_extern.db_id, player_id_2, "Gotten player by extern mismatch"
        )
        self.assertEqual(
            player_2_by_id.extern_id, extern_id_2, "Gotten player by ID mismatch"
        )
        self.assertEqual(
            player_2_by_extern.extern_id,
            extern_id_2,
            "Gotten player by extern mismatch",
        )
        self.assertEqual(
            player_2_by_id.is_preauth, True, "Did not retain preauth status"
        )
        self.assertEqual(player_2_by_id.flag_count, 0, "Did not initialize flags to 0")
        self.assertEqual(
            player_2_by_id.safety_trigger_count,
            0,
            "Did not initialize safety triggers to 0",
        )
        self.assertEqual(
            player_2_by_id.total_messages, 0, "Did not intialize messages to 0"
        )
        self.assertEqual(
            player_2_by_id.account_status,
            PlayerStatus.TUTORIAL,
            "Did not initialize to tutorial",
        )

        # Assert cannot find non-existent players

        with self.assertRaises(KeyError):
            player_5 = db.get_player(-1)
        with self.assertRaises(KeyError):
            player_5 = db.get_player_by_extern_id("FakePlayer")

    def test_update_scores(self):
        """Ensure we can increment scores successfully"""
        hydra_config = OmegaConf.structured(config)
        db = UserDB(config)

        extern_id_1 = "TEST_LOGIN"
        player_id_1 = db.create_user(extern_id_1, is_preauth=False)
        agent_id_1 = 1
        agent_id_2 = 2

        # Check default score is present and 0
        base_score = db.get_agent_score(player_id_1)
        self.assertEqual(base_score.score, 0, "Default score not 0")
        self.assertEqual(base_score.count, 0, "Default count not 0")

        # Check that querying non-existent score fails
        with self.assertRaises(KeyError, msg="Able to find nonexisting score"):
            base_score = db.get_agent_score(player_id_1, -1)
        with self.assertRaises(
            KeyError, msg="Able to find score for nonexisting player"
        ):
            base_score = db.get_agent_score(-1)

        # Add a few scores for at least 2 different agent names
        db.update_agent_score(player_id_1, agent_id_1, 1, 4, 5)
        db.update_agent_score(player_id_1, agent_id_2, 2, 5, -4)
        db.update_agent_score(player_id_1, agent_id_2, 3, 6, 2)

        # Ensure all of the values add up as expected
        base_score = db.get_agent_score(player_id_1)
        score_1 = db.get_agent_score(player_id_1, agent_id_1)
        score_2 = db.get_agent_score(player_id_1, agent_id_2)

        self.assertEqual(base_score.score, 6, "Scores did not add to 6")
        self.assertEqual(base_score.count, 3, "Other than 3 episodes marked")
        self.assertEqual(base_score.reward_xp, 3, "Reward xp not summed")
        self.assertEqual(score_1.score, 1, "Expected 1 score for agent 1")
        self.assertEqual(score_1.count, 1, "Expected one episode for agent 1")
        self.assertEqual(score_2.score, 5, "Expected 5 score for agent 2")
        self.assertEqual(score_2.count, 2, "Expected two episodes for agent 2")

        # Ensure that counts propogate up to player
        player = db.get_player(player_id_1)
        self.assertEqual(player.total_messages, 15, "Expected 15 actions")

        # Assert can delete player
        env_db = EnvDB(config)
        db.delete_player(player_id_1, env_db)

        with self.assertRaises(KeyError):
            player_1_by_id = db.get_player(player_id_1)
        with self.assertRaises(KeyError):
            base_score = db.get_agent_score(player_id_1)
        with self.assertRaises(KeyError):
            score_1 = db.get_agent_score(player_id_1, agent_id_1)
        with self.assertRaises(KeyError):
            score_2 = db.get_agent_score(player_id_1, agent_id_2)

    def test_flag_scores(self):
        """Ensure we can flag players successfully"""
        hydra_config = OmegaConf.structured(config)
        db = UserDB(config)

        extern_id_1 = "TEST_LOGIN"
        player_id_1 = db.create_user(extern_id_1, is_preauth=False)

        # Ensure we can flag and safety trigger users
        db.mark_flag(player_id_1)
        db.mark_flag(player_id_1)
        db.mark_safety_trigger(player_id_1)
        db.mark_safety_trigger(player_id_1)
        db.mark_safety_trigger(player_id_1)

        # Ensure the values add up as expected
        player = db.get_player(player_id_1)
        self.assertEqual(player.flag_count, 2, "Expected 2 flags")
        self.assertEqual(player.safety_trigger_count, 3, "Expected 3 safety triggers")

        # Ensure we cannot flag or trigger non-existing users
        with self.assertRaises(KeyError, msg="Could mark non-existing player"):
            db.mark_flag(-1)
        with self.assertRaises(KeyError, msg="Could mark non-existing player"):
            db.mark_safety_trigger(-1)

    def test_update_player_status(self):
        """Ensure we can flag players successfully"""
        hydra_config = OmegaConf.structured(config)
        db = UserDB(config)

        extern_id_1 = "TEST_LOGIN"
        player_id_1 = db.create_user(extern_id_1, is_preauth=False)

        # Ensure we can cycle through all statuses
        for player_status in [
            PlayerStatus.STANDARD,
            PlayerStatus.BLOCKED,
            PlayerStatus.TUTORIAL,
            PlayerStatus.ADMIN,
        ]:
            db.update_player_status(player_id_1, player_status)
            player = db.get_player(player_id_1)
            self.assertEqual(
                player.account_status,
                player_status,
                f"Did not find expected status {player_status}, instead {player.account_status}",
            )

        # Ensure update on nonexisting player fails
        with self.assertRaises(KeyError, msg="Could change existing player status"):
            db.update_player_status(-1, PlayerStatus.STANDARD)


if __name__ == "__main__":
    unittest.main()
