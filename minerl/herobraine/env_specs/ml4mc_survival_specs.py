# Copyright (c) 2020 All Rights Reserved
# Author: William H. Guss, Brandon Houghton
from minerl.herobraine.env_specs.simple_embodiment import SimpleEmbodimentEnvSpec
from minerl.herobraine.hero.handler import Handler
from typing import List

import minerl.herobraine.hero.handlers as handlers
from minerl.herobraine.hero.mc import ALL_ITEMS


"""
The intent of this env_spec is to create a survival environment for our agent to be evaluated in.
This environment allows us to tailor the observation and action spaces to our agent's and UI's needs.
"""

NONE = 'none'
OTHER = 'other'

MS_PER_STEP = 50

ML4MC_SURVIVAL_LENGTH = 1 * 60 * 60 * 20  # 1 hour * 60 minutes * 60 seconds * 20 ticks/steps per second

class ML4MCSurvival(SimpleEmbodimentEnvSpec):
    # ML4MCSurvival constructor
    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'ML4MCSurvival-v0' # Add environment name if not added

        super().__init__(*args, max_episode_steps=ML4MC_SURVIVAL_LENGTH, **kwargs)

    # Allows scripts to observe inventory, equipped item, and current location related stats
    def create_observables(self) -> List[Handler]:
        return super().create_observables() + [
            handlers.FlatInventoryObservation(ALL_ITEMS),
            handlers.EquippedItemObservation(items=[
                'air', 'wooden_axe', 'wooden_pickaxe', 'stone_axe', 'stone_pickaxe', 'iron_axe', 'iron_pickaxe', NONE,
                OTHER
            ], _default='air', _other=OTHER),
            handlers.ObservationFromCurrentLocation(),
        ]

    # Allows scripts to place blocks, equip items, craft items, and smelt items
    def create_actionables(self):
        return super().create_actionables() + [
            handlers.PlaceBlock([NONE, 'dirt', 'stone', 'cobblestone', 'crafting_table', 'furnace', 'torch'],
                                _other=NONE, _default=NONE),
            handlers.EquipAction([NONE, 'air', 'wooden_axe', 'wooden_pickaxe', 'stone_axe', 'stone_pickaxe', 'iron_axe',
                                  'iron_pickaxe'], _other=NONE, _default=NONE),
            handlers.CraftAction([NONE, 'torch', 'stick', 'planks', 'crafting_table'], _other=NONE, _default=NONE),
            handlers.CraftNearbyAction(
                [NONE, 'wooden_axe', 'wooden_pickaxe', 'stone_axe', 'stone_pickaxe', 'iron_axe', 'iron_pickaxe',
                 'furnace'], _other=NONE, _default=NONE),
            handlers.SmeltItemNearby([NONE, 'iron_ingot', 'coal'], _other=NONE, _default=NONE),
        ]

    # No rewards for now with this environment
    def create_rewardables(self) -> List[Handler]:
        return []

    # Start the agent with nothing by default, can be modified for testing
    def create_agent_start(self) -> List[Handler]:
        return []

    # No agent handlers needed as we are not using any rewards
    def create_agent_handlers(self) -> List[Handler]:
        return []

    # Use the default world generator
    def create_server_world_generators(self) -> List[Handler]:
        return [handlers.DefaultWorldGenerator(force_reset=True)]

    def create_server_quit_producers(self) -> List[Handler]:
        # Set a timeout to end the episode to prevent it from running forever
        return [
            handlers.ServerQuitFromTimeUp(time_limit_ms=self.max_episode_steps * MS_PER_STEP),
            handlers.ServerQuitWhenAnyAgentFinishes()
        ]

    # This method can be used to change other things about the world such as drawing shapes or spawning a village
    # Not needed for ML4MCSurvival
    def create_server_decorators(self) -> List[Handler]:
        return []

    # This method sets the conditions for the world the agent will spawn into
    # We will allow spawning and the passage of time to replicate a realistic Minecraft environment
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

    def is_from_folder(self, folder: str) -> bool:
        return folder == 'ml4mc_survival'

    # Don't need docstring as we're not publishing this environment to MineRL's website
    def get_docstring(self):
        return ""

    def determine_success_from_rewards(self, rewards: list) -> bool:
        # All survival experiemnts are a success =)
        return True