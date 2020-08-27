
import os
import json
import random

class QuestLoader():
    """
    Loads quests from a directory, then lets them be queried
    randomly

    TODO query by character or other attributes
    """

    def __init__(self, quest_dir):
        self.quests = []
        for quest_file in os.listdir(quest_dir):
            with open(os.path.join(quest_dir, quest_file), "r") as jsonfile:
                self.quests.append(json.load(jsonfile))

    def get_random_quest(self):
        """
        Get any random quest from the list of quests.
        """
        return random.choice(quests)