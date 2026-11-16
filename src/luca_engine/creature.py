"""
Creature Creator, Morphing Geometry, and Trait Stats Engine.

Junior Dev Note:
----------------
Every modification in the Creature Creator directly impacts gameplay physics
and survival stats:
- Hair / Fur (`fur_density`) -> Increases Cold Resistance (thermal insulation).
- Fins / Webbing (`fin_size`) -> Increases Swim Speed and lowers water drag.
- Limbs (`limb_count`, `limb_length`) -> Increases Land Speed and Button/Tool manipulation.
- Brain / Cortex (`brain_level`) -> Unlocks Cognitive & Social interactions,
  pack alliances, and advanced button/mechanism activation.
- Sensory Organs (`sensory_level`) -> Expands detection radius for food, predators,
  and rare mutagenic DNA nodes.
- Muscle Mass (`muscle_mass`) -> Boosts attack power and carrying/dash force,
  at the cost of higher metabolic calorie burn.
- Morph Sliders (`torso_scale`, `head_scale`, `extremity_stretch`) -> Driven by
  pinch-and-stretch touch/mouse gestures in the 3D Creature Creator.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from src.luca_engine.logger import get_game_logger

logger = get_game_logger("luca_engine.creature")


@dataclass
class EvolutionaryFeature:
    """
    Represents an unlockable biological trait or organ in the Creature Creator.
    """

    feature_id: str
    name: str
    category: str  # 'locomotion', 'sensory', 'cognitive', 'integument', 'metabolism'
    dna_cost: int
    stat_modifiers: Dict[str, float]
    description: str


# Catalog of unlockable features that can also be scavenged from NPCs/environment
FEATURE_CATALOG: Dict[str, EvolutionaryFeature] = {
    "flagella": EvolutionaryFeature(
        feature_id="flagella",
        name="Rotary Flagella",
        category="locomotion",
        dna_cost=15,
        stat_modifiers={"swim_speed": 2.5, "metabolic_rate": 0.2},
        description="Microscopic whip-like propeller for micro-vent propulsion.",
    ),
    "viral_capsid": EvolutionaryFeature(
        feature_id="viral_capsid",
        name="Icosahedral Viral Capsid",
        category="metabolism",
        dna_cost=30,
        stat_modifiers={"infection_power": 4.0, "stealth": 2.0, "size_factor": -0.4},
        description="Enables the Viral Evolutionary Path: hijack host cells to replicate rapidly.",
    ),
    "hydro_fins": EvolutionaryFeature(
        feature_id="hydro_fins",
        name="Hydrodynamic Dorsal & Pectoral Fins",
        category="locomotion",
        dna_cost=25,
        stat_modifiers={"swim_speed": 4.5, "agility": 2.0},
        description="Fins channel water flow for high-speed pelagic swimming.",
    ),
    "thermal_fur": EvolutionaryFeature(
        feature_id="thermal_fur",
        name="Insulating Mammalian Fur Coat",
        category="integument",
        dna_cost=30,
        stat_modifiers={"cold_resistance": 5.0, "defense": 1.5},
        description="Dense keratin hair traps warm air, keeping your creature warm in ice ages.",
    ),
    "chitin_carapace": EvolutionaryFeature(
        feature_id="chitin_carapace",
        name="Armored Chitin Exoskeleton",
        category="integument",
        dna_cost=35,
        stat_modifiers={"defense": 5.0, "land_speed": -0.5},
        description="Deflects predator bites and abyssal pressure.",
    ),
    "articulated_limbs": EvolutionaryFeature(
        feature_id="articulated_limbs",
        name="Tetrapod Articulated Limbs",
        category="locomotion",
        dna_cost=40,
        stat_modifiers={"land_speed": 4.5, "dexterity": 3.0},
        description="Load-bearing limbs for terrestrial locomotion and button/object interaction.",
    ),
    "avian_wings": EvolutionaryFeature(
        feature_id="avian_wings",
        name="Pneumatic Feathered Wings",
        category="locomotion",
        dna_cost=55,
        stat_modifiers={"flight_speed": 6.0, "agility": 3.5, "cold_resistance": 2.0},
        description="Conquer the skies and glide between continental biomes.",
    ),
    "compound_eyes": EvolutionaryFeature(
        feature_id="compound_eyes",
        name="Multispectral Compound Eyes",
        category="sensory",
        dna_cost=25,
        stat_modifiers={"sensory_range": 4.0, "agility": 1.0},
        description="Detects predators and rich DNA food sources from afar.",
    ),
    "neocortex_synapse": EvolutionaryFeature(
        feature_id="neocortex_synapse",
        name="Expanded Prefrontal Neocortex",
        category="cognitive",
        dna_cost=50,
        stat_modifiers={"cognition": 5.0, "social_skill": 4.0, "dexterity": 2.5},
        description="Unlocks tool use, environmental button mechanisms, and cooperative packs.",
    ),
    "apex_muscle_fibers": EvolutionaryFeature(
        feature_id="apex_muscle_fibers",
        name="Fast-Twitch Myofibril Bundles",
        category="locomotion",
        dna_cost=40,
        stat_modifiers={"attack_power": 4.5, "land_speed": 2.0, "metabolic_rate": 1.2},
        description="Dense musculature boosts bite/strike force and sprint burst.",
    ),
}


@dataclass
class CreatureMorphology:
    """
    Stores 3D procedural body-shaping parameters adjusted via pinch/stretch gestures.
    """

    torso_length: float = 1.0  # Range: 0.4 to 3.0
    torso_radius: float = 1.0  # Range: 0.4 to 2.5
    head_scale: float = 1.0  # Range: 0.5 to 2.5
    extremity_stretch: float = 1.0  # Range: 0.3 to 3.0
    spine_curvature: float = 0.0  # Range: -1.0 to 1.0
    skin_pattern: str = "bioluminescent"  # 'bioluminescent', 'scales', 'fur', 'chitin', 'viral'
    primary_color: str = "#00f5d4"
    secondary_color: str = "#7b2cbf"

    def apply_pinch_stretch(
        self, region: str, delta_stretch: float, delta_pinch: float = 0.0
    ) -> None:
        """
        Update morphology in response to user pinch/stretch touch or mouse gestures.

        Args:
            region: 'torso', 'head', or 'extremities'.
            delta_stretch: Longitudinal stretch factor change.
            delta_pinch: Radial thickness pinch/expand change.
        """
        if region == "torso":
            self.torso_length = max(0.4, min(3.0, self.torso_length + delta_stretch))
            self.torso_radius = max(0.4, min(2.5, self.torso_radius + delta_pinch))
        elif region == "head":
            self.head_scale = max(0.5, min(2.5, self.head_scale + delta_stretch))
        elif region == "extremities":
            self.extremity_stretch = max(
                0.3, min(3.0, self.extremity_stretch + delta_stretch)
            )
        else:
            raise ValueError(f"Unknown body region for morphing: {region}")

        logger.debug(
            "Morphed region=%s -> torso_L=%.2f, torso_R=%.2f, head=%.2f, ext=%.2f",
            region,
            self.torso_length,
            self.torso_radius,
            self.head_scale,
            self.extremity_stretch,
        )


@dataclass
class Creature:
    """
    Represents either the Player's evolving lineage or an NPC co-evolving species.
    """

    name: str
    generation: int = 1
    dna_points: int = 60
    health: float = 100.0
    max_health: float = 100.0
    energy: float = 100.0
    diet_preference: str = "omnivore"  # 'herbivore', 'carnivore', 'omnivore', 'viral'
    evolution_path: str = "cellular"  # 'viral', 'cellular', 'aquatic', 'terrestrial', 'aerial', 'cosmic_leviathan'
    unlocked_dna_pool: Set[str] = field(
        default_factory=lambda: {"flagella", "hydro_fins", "thermal_fur"}
    )
    active_features: Set[str] = field(default_factory=lambda: {"flagella"})
    morphology: CreatureMorphology = field(default_factory=CreatureMorphology)

    def compute_stats(self) -> Dict[str, float]:
        """
        Calculate effective gameplay stats from active features and 3D body morphology.

        Junior Dev Note:
        Notice how both genetic features AND physical pinch/stretch dimensions
        contribute to stats. A larger torso increases health and heat retention,
        while stretched extremities improve speed and reach!
        """
        stats: Dict[str, float] = {
            "swim_speed": 2.0,
            "land_speed": 1.0,
            "flight_speed": 0.0,
            "cold_resistance": 1.0,
            "heat_resistance": 2.0,
            "attack_power": 2.0,
            "defense": 1.5,
            "sensory_range": 3.0,
            "cognition": 1.0,
            "social_skill": 1.0,
            "dexterity": 1.0,
            "infection_power": 0.0,
            "stealth": 1.0,
            "metabolic_rate": 1.0,
            "size_factor": 1.0,
        }

        # 1. Aggregate modifiers from all active evolutionary features
        for feat_id in self.active_features:
            feature = FEATURE_CATALOG.get(feat_id)
            if feature:
                for stat_name, delta in feature.stat_modifiers.items():
                    stats[stat_name] = stats.get(stat_name, 0.0) + delta

        # 2. Apply morphology geometry multipliers (pinch/stretch impact)
        body_volume = (
            self.morphology.torso_length * (self.morphology.torso_radius ** 2)
        )
        stats["size_factor"] = max(0.2, stats["size_factor"] * body_volume)
        stats["cold_resistance"] += (self.morphology.torso_radius - 1.0) * 1.5
        stats["land_speed"] += (self.morphology.extremity_stretch - 1.0) * 1.2
        stats["swim_speed"] += (self.morphology.torso_length - 1.0) * 0.8
        stats["cognition"] += (self.morphology.head_scale - 1.0) * 2.0

        # Skin texture bonus
        if self.morphology.skin_pattern == "fur":
            stats["cold_resistance"] += 2.5
        elif self.morphology.skin_pattern == "chitin":
            stats["defense"] += 2.5
        elif self.morphology.skin_pattern == "scales":
            stats["swim_speed"] += 1.5
            stats["heat_resistance"] += 1.5
        elif self.morphology.skin_pattern == "viral":
            stats["infection_power"] += 2.0

        return stats

    def can_use_buttons_and_mechanisms(self) -> bool:
        """
        Return True if the creature has evolved sufficient limbs/dexterity and cognition
        to operate advanced environmental buttons and selection mechanisms.
        """
        stats = self.compute_stats()
        return stats["cognition"] >= 3.5 and stats["dexterity"] >= 2.5

    def evolve_feature(self, feature_id: str) -> Tuple[bool, str]:
        """
        Spend DNA points to add a biological feature in the Creature Creator.
        """
        if feature_id not in FEATURE_CATALOG:
            return False, f"Unknown feature '{feature_id}'."
        if feature_id in self.active_features:
            return False, f"Feature '{FEATURE_CATALOG[feature_id].name}' is already active."
        if feature_id not in self.unlocked_dna_pool:
            return (
                False,
                f"DNA for '{FEATURE_CATALOG[feature_id].name}' has not been discovered yet!",
            )

        feature = FEATURE_CATALOG[feature_id]
        if self.dna_points < feature.dna_cost:
            return (
                False,
                f"Insufficient DNA points ({self.dna_points}/{feature.dna_cost}).",
            )

        self.dna_points -= feature.dna_cost
        self.active_features.add(feature_id)
        self._update_evolution_path()
        logger.info(
            "Creature '%s' evolved feature '%s' (remaining DNA=%d)",
            self.name,
            feature.name,
            self.dna_points,
        )
        return True, f"Evolved {feature.name}!"

    def devolve_feature(self, feature_id: str) -> Tuple[bool, str]:
        """
        Remove an active feature and refund 50% of its DNA cost.
        """
        if feature_id not in self.active_features:
            return False, f"Feature '{feature_id}' is not currently active."

        feature = FEATURE_CATALOG[feature_id]
        refund = feature.dna_cost // 2
        self.active_features.remove(feature_id)
        self.dna_points += refund
        self._update_evolution_path()
        logger.info(
            "Creature '%s' devolved feature '%s' (refunded %d DNA)",
            self.name,
            feature.name,
            refund,
        )
        return True, f"Devolved {feature.name} (+{refund} DNA refunded)."

    def produce_offspring(self) -> "Creature":
        """
        Pass all evolved traits and morphed geometry onto the next generation.
        """
        self.generation += 1
        stats = self.compute_stats()
        self.max_health = round(100.0 + stats["size_factor"] * 25.0 + stats["defense"] * 8.0, 1)
        self.health = self.max_health
        self.energy = 100.0
        logger.info(
            "Lineage '%s' advanced to Generation %d (max_health=%.1f)",
            self.name,
            self.generation,
            self.max_health,
        )
        return self

    def _update_evolution_path(self) -> None:
        """Determine evolutionary archetype from active traits."""
        if "viral_capsid" in self.active_features:
            self.evolution_path = "viral"
        elif "avian_wings" in self.active_features:
            self.evolution_path = "aerial"
        elif "articulated_limbs" in self.active_features:
            self.evolution_path = "terrestrial"
        elif "hydro_fins" in self.active_features:
            self.evolution_path = "aquatic"
        else:
            self.evolution_path = "cellular"
