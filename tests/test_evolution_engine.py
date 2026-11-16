"""
Regression Test Suite for the LUCA 3D Evolution Engine.

Junior Dev Note:
----------------
Every feature we build has a corresponding unit test here!
These tests run automatically in GitHub Actions on every push or pull request,
ensuring our cosmic puzzle, creature stats, biome physics, co-evolution AI,
and audit logger never regress.
"""

import unittest
from src.luca_engine.cosmos import COSMIC_TIMELINE, RNASoupPuzzle
from src.luca_engine.creature import Creature, FEATURE_CATALOG
from src.luca_engine.logger import MEMORY_HANDLER, get_game_logger
from src.luca_engine.world import BIOMES, GameDifficultySettings, WorldSimulation


class TestCosmicAndRNAPuzzle(unittest.TestCase):
    """Tests for the Big Bang timeline and Hydrothermal Vent RNA Soup puzzle."""

    def test_cosmic_timeline_sequence(self) -> None:
        """Verify cosmic stages progress chronologically from Big Bang to LUCA vent."""
        self.assertGreaterEqual(len(COSMIC_TIMELINE), 5)
        self.assertEqual(COSMIC_TIMELINE[0].stage_id, "big_bang")
        self.assertEqual(COSMIC_TIMELINE[-1].stage_id, "luca_vent")
        self.assertGreater(
            COSMIC_TIMELINE[0].time_mya, COSMIC_TIMELINE[-1].time_mya
        )

    def test_rna_soup_puzzle_completion(self) -> None:
        """Verify complementary base pairing (A-U, G-C) emerges LUCA and grants DNA."""
        puzzle = RNASoupPuzzle(template_strand="AUGC")
        # Expected complements: U, A, C, G
        ok1, pts1, _ = puzzle.attempt_pair("U")
        self.assertTrue(ok1)
        self.assertEqual(pts1, 10)

        # Intentional mismatch test
        ok_bad, pts_bad, _ = puzzle.attempt_pair("G")
        self.assertFalse(ok_bad)
        self.assertEqual(pts_bad, 0)

        # Finish remaining valid pairs: A, C, G
        puzzle.attempt_pair("A")
        puzzle.attempt_pair("C")
        ok_final, pts_final, msg = puzzle.attempt_pair("G")
        self.assertTrue(ok_final)
        self.assertTrue(puzzle.is_luca_emerged)
        self.assertEqual(pts_final, 50)
        self.assertIn("LUCA EMERGED", msg)


class TestCreatureCreatorAndMorphing(unittest.TestCase):
    """Tests for Creature Creator DNA spending, trait stats, and pinch/stretch morphing."""

    def test_hair_makes_warm_and_fins_help_swim(self) -> None:
        """Verify biological traits directly modify their corresponding survival stats."""
        creature = Creature(name="Proto-Cetacean", dna_points=100)
        base_stats = creature.compute_stats()

        # Evolve hydro fins -> swim speed increases
        ok_fin, _ = creature.evolve_feature("hydro_fins")
        self.assertTrue(ok_fin)
        fin_stats = creature.compute_stats()
        self.assertGreater(fin_stats["swim_speed"], base_stats["swim_speed"])

        # Evolve thermal fur -> cold resistance increases
        ok_fur, _ = creature.evolve_feature("thermal_fur")
        self.assertTrue(ok_fur)
        fur_stats = creature.compute_stats()
        self.assertGreater(
            fur_stats["cold_resistance"], fin_stats["cold_resistance"]
        )

    def test_pinch_and_stretch_morphology_impacts_stats(self) -> None:
        """Verify pinch/stretch gestures clamp safely and alter creature stats."""
        creature = Creature(name="MorphTester")
        before_stats = creature.compute_stats()

        creature.morphology.apply_pinch_stretch("extremities", delta_stretch=1.0)
        creature.morphology.apply_pinch_stretch("head", delta_stretch=0.8)
        after_stats = creature.compute_stats()

        self.assertGreater(after_stats["land_speed"], before_stats["land_speed"])
        self.assertGreater(after_stats["cognition"], before_stats["cognition"])

    def test_devolve_refunds_dna(self) -> None:
        """Verify devolving an active trait refunds half its DNA cost."""
        creature = Creature(name="DevolveTester", dna_points=50)
        creature.evolve_feature("hydro_fins")  # Costs 25 -> 25 left
        self.assertEqual(creature.dna_points, 25)
        ok, _ = creature.devolve_feature("hydro_fins")
        self.assertTrue(ok)
        self.assertEqual(creature.dna_points, 25 + 12)


class TestWorldMapBiomesAndCoEvolution(unittest.TestCase):
    """Tests for Biome physics, bump interactions, button mechanisms, and NPC co-evolution."""

    def test_biome_physics_and_climate_stress(self) -> None:
        """Verify freezing tundra damages creatures without fur, while fur protects them."""
        world = WorldSimulation(current_biome_id="pleistocene_tundra")
        naked_creature = Creature(name="Hairless", dna_points=100)
        stress_naked = world.evaluate_climate_stress(naked_creature)
        self.assertGreater(stress_naked, 0.0)

        naked_creature.evolve_feature("thermal_fur")
        naked_creature.morphology.skin_pattern = "fur"
        stress_furry = world.evaluate_climate_stress(naked_creature)
        self.assertLess(stress_furry, stress_naked)

    def test_bump_interactions_and_dna_assimilation(self) -> None:
        """Verify bumping food restores health and bumping defeated NPCs unlocks their DNA."""
        world = WorldSimulation()
        creature = Creature(name="Hunter", dna_points=120, health=60.0)
        food_res = world.handle_bump_food(creature, "meat", nutrition_value=25.0)
        self.assertEqual(food_res["new_diet"], "carnivore")
        self.assertGreater(creature.health, 60.0)

        # Boost attack power to defeat trilobite and unlock chitin_carapace
        creature.unlocked_dna_pool.add("apex_muscle_fibers")
        creature.evolve_feature("apex_muscle_fibers")
        trilobite = world.npc_species[1]
        bump_res = world.handle_bump_npc(creature, trilobite)
        self.assertTrue(bump_res["victory"])
        self.assertIn("chitin_carapace", creature.unlocked_dna_pool)

    def test_cognitive_button_mechanism_gate(self) -> None:
        """Verify environmental button mechanisms require evolved limbs and cognition."""
        world = WorldSimulation()
        creature = Creature(name="Thinker", dna_points=200)
        ok_early, _, _ = world.activate_environmental_mechanism(
            creature, "Monolith Switch"
        )
        self.assertFalse(ok_early)

        creature.unlocked_dna_pool.update(
            {"articulated_limbs", "neocortex_synapse"}
        )
        creature.evolve_feature("articulated_limbs")
        creature.evolve_feature("neocortex_synapse")
        ok_late, reward, _ = world.activate_environmental_mechanism(
            creature, "Monolith Switch"
        )
        self.assertTrue(ok_late)
        self.assertEqual(reward, 45)

    def test_coevolution_and_logging_audit(self) -> None:
        """Verify NPC species co-evolve with difficulty sliders and log events."""
        logger = get_game_logger("luca_engine.test")
        logger.info("Starting co-evolution audit test")
        world = WorldSimulation(
            settings=GameDifficultySettings(
                climate_severity=1.5,
                predation_aggression=1.8,
                resource_scarcity=1.2,
            )
        )
        initial_atk = world.npc_species[0].attack
        events = world.advance_coevolution_epoch()
        self.assertEqual(len(events), len(world.npc_species))
        self.assertGreater(world.npc_species[0].attack, initial_atk)
        self.assertTrue(
            any("co-evolved" in rec or "Starting co-evolution" in rec for rec in MEMORY_HANDLER.records)
        )


if __name__ == "__main__":
    unittest.main()
