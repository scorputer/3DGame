"""
World Map, Biome Physics, Co-Evolution NPC AI, and Bump/Mechanism Interactions.

Junior Dev Note:
----------------
This module governs the World Map screen:
1. Biomes from Micro to Macro: Each biome defines viscosity/fluid drag, gravity,
   ambient temperature, and locomotion multipliers.
2. Bump-Style Interactions:
   - Bump into Food -> Restore health, shift diet adaptation, earn DNA points.
   - Bump into Predator / Rival -> Exchange combat damage based on Attack/Defense;
     defeating or scavenging creatures with novel traits unlocks their DNA in
     the player's `unlocked_dna_pool`!
3. Advanced Cognitive Mechanism Interaction:
   - Once a creature evolves limbs + neocortex, it can trigger environmental
     buttons/mechanisms (e.g., Geo-Thermal Resonator, Seed Vault, Orbital Beacon).
4. Co-Evolution & Difficulty Sliders:
   - NPC species co-evolve every epoch in response to climate shifts, predation
     pressure, and resource scarcity sliders.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from src.luca_engine.creature import Creature, FEATURE_CATALOG
from src.luca_engine.logger import get_game_logger

logger = get_game_logger("luca_engine.world")


@dataclass
class BiomePhysics:
    """
    Defines environmental physics and survival conditions for a World Map biome.
    """

    biome_id: str
    name: str
    scale_label: str  # 'Micro (10 µm)', 'Mesoscopic (10 cm)', 'Macro (10 m)', 'Planetary (100 km)'
    fluid_viscosity: float  # Higher viscosity penalizes non-flagellar/non-fin movement
    gravity_g: float
    ambient_temp_celsius: float
    primary_medium: str  # 'water', 'land', 'air', 'micro_fluid'
    description: str


BIOMES: Dict[str, BiomePhysics] = {
    "hydrothermal_micro": BiomePhysics(
        biome_id="hydrothermal_micro",
        name="Alkaline Hydrothermal Vent (Micro)",
        scale_label="Microscale (10 µm - 1 mm)",
        fluid_viscosity=0.85,
        gravity_g=0.05,
        ambient_temp_celsius=68.0,
        primary_medium="micro_fluid",
        description="High-viscosity mineral plumes where LUCA, viruses, and archaea compete.",
    ),
    "pelagic_ocean": BiomePhysics(
        biome_id="pelagic_ocean",
        name="Cambrian Pelagic Ocean",
        scale_label="Macro-Aquatic (10 cm - 15 m)",
        fluid_viscosity=0.45,
        gravity_g=0.15,
        ambient_temp_celsius=18.0,
        primary_medium="water",
        description="Sunlit reefs and abyssal trenches governed by hydrodynamic drag and buoyancy.",
    ),
    "pangaea_jungle": BiomePhysics(
        biome_id="pangaea_jungle",
        name="Carboniferous Continental Jungle",
        scale_label="Macro-Terrestrial (1 m - 30 m)",
        fluid_viscosity=0.05,
        gravity_g=1.0,
        ambient_temp_celsius=28.0,
        primary_medium="land",
        description="Gravity-dominated terrain requiring articulated limbs or muscular slithering.",
    ),
    "pleistocene_tundra": BiomePhysics(
        biome_id="pleistocene_tundra",
        name="Glacial Ice Age Tundra",
        scale_label="Macro-Cryogenic (1 m - 25 m)",
        fluid_viscosity=0.08,
        gravity_g=1.0,
        ambient_temp_celsius=-22.0,
        primary_medium="land",
        description="Freezing blizzards that drain health rapidly without insulating fur or blubber.",
    ),
    "sky_archipelago": BiomePhysics(
        biome_id="sky_archipelago",
        name="Stratospheric Floating Archipelago",
        scale_label="Planetary Canopy (10 m - 500 m)",
        fluid_viscosity=0.02,
        gravity_g=0.65,
        ambient_temp_celsius=-5.0,
        primary_medium="air",
        description="High-altitude thermals where winged leviathans and airborne spores rule.",
    ),
}


@dataclass
class GameDifficultySettings:
    """
    User-configurable sliders for climate harshness, predation, and resource scarcity.
    """

    climate_severity: float = 1.0  # 0.2 (Mild) to 2.5 (Extinction-level shifts)
    predation_aggression: float = 1.0  # 0.2 (Peaceful) to 2.5 (Apex Carnage)
    resource_scarcity: float = 1.0  # 0.2 (Abundant) to 2.5 (Famine)
    multiplayer_sync_enabled: bool = True


@dataclass
class NPCSpecies:
    """
    Represents an autonomous NPC species that co-evolves alongside the player.
    """

    species_id: str
    name: str
    archetype: str  # 'predator', 'grazer', 'symbiote', 'viral_swarm'
    level: int = 1
    attack: float = 3.0
    defense: float = 2.0
    speed: float = 2.5
    signature_dna_feature: str = "chitin_carapace"
    population: int = 25


@dataclass
class WorldSimulation:
    """
    Manages the World Map state, biome physics calculations, bump interactions,
    and NPC co-evolution cycles.
    """

    current_biome_id: str = "hydrothermal_micro"
    epoch_age_mya: float = 3800.0
    settings: GameDifficultySettings = field(default_factory=GameDifficultySettings)
    npc_species: List[NPCSpecies] = field(default_factory=list)
    co_op_ally_species: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Seed initial NPC species if none provided."""
        if not self.npc_species:
            self.npc_species = [
                NPCSpecies(
                    species_id="npc_anomalocaris",
                    name="Radiodont Apex Hunter",
                    archetype="predator",
                    level=1,
                    attack=4.0,
                    defense=2.5,
                    speed=3.2,
                    signature_dna_feature="compound_eyes",
                ),
                NPCSpecies(
                    species_id="npc_trilobite",
                    name="Benthic Trilobite Grazer",
                    archetype="grazer",
                    level=1,
                    attack=1.5,
                    defense=4.5,
                    speed=1.8,
                    signature_dna_feature="chitin_carapace",
                ),
                NPCSpecies(
                    species_id="npc_phage",
                    name="T4 Bacteriophage Swarm",
                    archetype="viral_swarm",
                    level=1,
                    attack=3.5,
                    defense=1.0,
                    speed=4.0,
                    signature_dna_feature="viral_capsid",
                ),
                NPCSpecies(
                    species_id="npc_therapsid",
                    name="Proto-Mammalian Strider",
                    archetype="symbiote",
                    level=2,
                    attack=3.5,
                    defense=3.0,
                    speed=3.8,
                    signature_dna_feature="articulated_limbs",
                ),
            ]
        logger.info("WorldSimulation initialized in biome=%s", self.current_biome_id)

    def calculate_locomotion_speed(self, creature: Creature) -> float:
        """
        Compute the creature's effective movement speed in the active biome
        based on biome physics (viscosity, gravity, medium) and creature traits.
        """
        biome = BIOMES[self.current_biome_id]
        stats = creature.compute_stats()

        if biome.primary_medium in ("water", "micro_fluid"):
            base_speed = stats["swim_speed"]
            # High fluid viscosity slows large creatures unless they have fins/flagella
            drag_penalty = biome.fluid_viscosity * (stats["size_factor"] * 0.35)
            effective = max(0.8, base_speed - drag_penalty)
        elif biome.primary_medium == "land":
            base_speed = stats["land_speed"] + (stats["flight_speed"] * 0.4)
            # High gravity penalizes creatures lacking articulated limbs
            limb_bonus = 1.35 if "articulated_limbs" in creature.active_features else 0.65
            effective = max(0.5, (base_speed * limb_bonus) / max(0.3, biome.gravity_g))
        else:  # 'air'
            base_speed = stats["flight_speed"] + (stats["land_speed"] * 0.3)
            effective = max(0.6, base_speed / max(0.2, biome.gravity_g))

        return round(effective, 2)

    def evaluate_climate_stress(self, creature: Creature) -> float:
        """
        Calculate per-tick health drain (or 0.0 if adapted) caused by biome temperature.
        """
        biome = BIOMES[self.current_biome_id]
        stats = creature.compute_stats()

        if biome.ambient_temp_celsius < 0.0:
            # Cold biome: hair/fur (`cold_resistance`) protects the creature
            cold_gap = abs(biome.ambient_temp_celsius) / 6.0 - stats["cold_resistance"]
            if cold_gap > 0:
                return round(cold_gap * self.settings.climate_severity, 2)
        elif biome.ambient_temp_celsius > 45.0:
            heat_gap = (biome.ambient_temp_celsius - 40.0) / 10.0 - stats["heat_resistance"]
            if heat_gap > 0:
                return round(heat_gap * self.settings.climate_severity, 2)

        return 0.0

    def handle_bump_food(
        self, creature: Creature, food_type: str, nutrition_value: float = 20.0
    ) -> Dict[str, object]:
        """
        Process a bump interaction between the player's creature and a food resource.
        """
        effective_nutrition = nutrition_value / max(0.4, self.settings.resource_scarcity)
        dna_gained = max(5, int(effective_nutrition * 0.6))

        creature.health = min(creature.max_health, creature.health + effective_nutrition)
        creature.energy = min(100.0, creature.energy + effective_nutrition * 0.8)
        creature.dna_points += dna_gained

        # Update diet adaptation based on what the player chooses to eat
        if food_type == "meat":
            creature.diet_preference = "carnivore"
        elif food_type == "flora":
            creature.diet_preference = "herbivore"
        elif food_type == "host_cell":
            creature.diet_preference = "viral"

        logger.info(
            "Creature '%s' ate %s: +%.1f HP, +%d DNA (diet=%s)",
            creature.name,
            food_type,
            effective_nutrition,
            dna_gained,
            creature.diet_preference,
        )
        return {
            "event": "food_consumed",
            "food_type": food_type,
            "health_restored": round(effective_nutrition, 1),
            "dna_gained": dna_gained,
            "new_diet": creature.diet_preference,
        }

    def handle_bump_npc(
        self, creature: Creature, npc: NPCSpecies
    ) -> Dict[str, object]:
        """
        Process a bump interaction with an NPC creature (combat/predation or viral infection).
        If the player wins or assimilates the NPC, unlock the NPC's signature DNA!
        """
        stats = creature.compute_stats()
        player_power = stats["attack_power"] + stats["infection_power"]
        incoming_damage = max(
            2.0,
            (npc.attack * self.settings.predation_aggression) - (stats["defense"] * 0.6),
        )
        creature.health = max(0.0, round(creature.health - incoming_damage, 1))

        unlocked_feature = None
        dna_reward = 0

        if player_power >= npc.defense:
            dna_reward = 25 * npc.level
            creature.dna_points += dna_reward
            if npc.signature_dna_feature not in creature.unlocked_dna_pool:
                creature.unlocked_dna_pool.add(npc.signature_dna_feature)
                unlocked_feature = npc.signature_dna_feature
                logger.info(
                    "Unlocked new DNA '%s' from NPC '%s'!",
                    unlocked_feature,
                    npc.name,
                )

        return {
            "event": "npc_bump",
            "npc_name": npc.name,
            "damage_taken": round(incoming_damage, 1),
            "victory": player_power >= npc.defense,
            "dna_reward": dna_reward,
            "unlocked_dna_feature": unlocked_feature,
        }

    def activate_environmental_mechanism(
        self, creature: Creature, mechanism_name: str
    ) -> Tuple[bool, int, str]:
        """
        Attempt to use evolved limbs and cognitive/social abilities to press buttons
        or operate ancient/environmental selection mechanisms.
        """
        if not creature.can_use_buttons_and_mechanisms():
            return (
                False,
                0,
                "Requires higher Cognition (>=3.5) and Limb Dexterity (>=2.5) to operate mechanisms!",
            )

        reward_dna = 45
        creature.dna_points += reward_dna
        # Unlock neocortex or wings if not yet discovered
        for bonus_feat in ("neocortex_synapse", "avian_wings", "apex_muscle_fibers"):
            if bonus_feat not in creature.unlocked_dna_pool:
                creature.unlocked_dna_pool.add(bonus_feat)
                break

        logger.info(
            "Creature '%s' activated mechanism '%s' (+%d DNA)",
            creature.name,
            mechanism_name,
            reward_dna,
        )
        return (
            True,
            reward_dna,
            f"Mechanism '{mechanism_name}' activated via limb/cognitive interface! +{reward_dna} DNA!",
        )

    def advance_coevolution_epoch(self) -> List[str]:
        """
        Advance geological time and co-evolve all NPC species in response to
        climate severity, predation pressure, and resource restrictions.
        """
        self.epoch_age_mya = max(0.0, round(self.epoch_age_mya - 250.0, 1))
        events: List[str] = []

        for npc in self.npc_species:
            npc.level += 1
            npc.attack = round(
                npc.attack + 1.2 * self.settings.predation_aggression, 2
            )
            npc.defense = round(
                npc.defense + 1.0 * self.settings.climate_severity, 2
            )
            npc.speed = round(
                npc.speed + 0.4 * self.settings.resource_scarcity, 2
            )
            msg = (
                f"{npc.name} co-evolved to Lv.{npc.level} "
                f"(ATK {npc.attack}, DEF {npc.defense}, SPD {npc.speed})"
            )
            events.append(msg)

        logger.info(
            "Advanced epoch to %.1f MYA; %d NPC species co-evolved.",
            self.epoch_age_mya,
            len(self.npc_species),
        )
        return events
