# Copyright (c) 2020 All Rights Reserved
# Author: William H. Guss, Brandon Houghton

from minerl.herobraine.env_specs.simple_embodiment import SimpleEmbodimentEnvSpec
from minerl.herobraine.hero.mc import MS_PER_STEP, STEPS_PER_MS
from minerl.herobraine.hero.handler import Handler
from typing import List

import minerl.herobraine
import minerl.herobraine.hero.handlers as handlers
from minerl.herobraine.env_spec import EnvSpec

# This is the text that would appear in the documentation online if this code were merged with MineRL
STONECOLLECT_DOC = """
In StoneCollection, the agent must collect 32 `minecraft:cobblestone`. This replicates a common scenario
in Minecraft, as cobblestone is necessary to craft a large amount of items in the game and is a
key resource in Minecraft. For example, stone pickaxes and furnaces, which are needed to mine and smelt iron.

The agent begins in a random starting location on a random survival map with a wooden pickaxe.
"""

# Defines how long each episode should last
STONECOLLECT_LENGTH = 8000

# This is the class that implements the environment specification,
# defining things such as the reward function, the starting items for the AI agent, etc.
class StoneCollection(SimpleEmbodimentEnvSpec):

    # Stone collection constructor
    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'StoneCollection-v0' # Add environment name if not added

        # End episode if the agent collects 32 cobblestone
        super().__init__(*args,
                         max_episode_steps=STONECOLLECT_LENGTH, reward_threshold=32.0,
                         **kwargs)

    # Produce a reward of 1 for each cobblestone block the agent collects
    def create_rewardables(self) -> List[Handler]:
        return [
            handlers.RewardForCollectingItems([
                dict(type="cobblestone", amount=1, reward=1.0),
            ])
        ]

    # Start the agent with a wooden pickaxe in its inventory
    def create_agent_start(self) -> List[Handler]:
        return [
            handlers.SimpleInventoryAgentStart([
                dict(type="wooden_pickaxe", quantity=1)
            ])
        ]

    def create_agent_handlers(self) -> List[Handler]:
        # Again, we will quit the episode if the agent reaches the 32 cobblestone threshold
        return [
            handlers.AgentQuitFromPossessingItem([
                dict(type="cobblestone", amount=32)]
            )
        ]

    def create_server_world_generators(self) -> List[Handler]:
        # We are using the default world generation because we want our agent to be able to mine cobblestone in any environment
        return [handlers.DefaultWorldGenerator(force_reset=True)]

    def create_server_quit_producers(self) -> List[Handler]:
        # Set a timeout to end the episode (to prevent it from running forever if the agent cannot collect 32 cobbelstone)
        return [
            handlers.ServerQuitFromTimeUp(
                (STONECOLLECT_LENGTH * MS_PER_STEP)),
            handlers.ServerQuitWhenAnyAgentFinishes()
        ]

    # This method can be used to change other things about the world such as drawing shapes or spawning a village
    # Not needed for stone collection
    def create_server_decorators(self) -> List[Handler]:
        return []

    # This method sets the conditions for the world the agent will spawn into
    # We will allow spawning and the passage of time to replicate a realistic Minecraft environment
    # and so that the conditions match the environment of the ObtainIronPickaxe dataset used for training
    def create_server_initial_conditions(self) -> List[Handler]:
        return [
            handlers.TimeInitialCondition(
                start_time=6000,
                allow_passage_of_time=True,
            ),
            handlers.SpawningInitialCondition(
                allow_spawning=True
            )
        ]

    # The agent succeeds if its reward surpasses the threshold we set (in our case, 32 cobblestone blocks)
    def determine_success_from_rewards(self, rewards: list) -> bool:
        return sum(rewards) >= self.reward_threshold

    def is_from_folder(self, folder: str) -> bool:
        return folder == 'stonecollection'

    # Returns documentation that would be displayed on the docs website for this environment
    def get_docstring(self):
        return STONECOLLECT_DOC
