"""
Initial Conditions: Cosmic Evolution & Hydrothermal Vent RNA Soup Puzzle.

Junior Dev Note:
----------------
This module models the opening act of the game:
1. Cosmic Timeline: Fast-forwarding from the Big Bang -> Galaxy formation ->
   Supernovae nucleosynthesis -> Yellow G-type star ignition -> Molten Earth
   cooling into primordial oceans.
2. Hydrothermal Vent RNA Puzzle: Before LUCA (Last Universal Common Ancestor)
   can emerge as a cellular organism, the player must fold a valid catalytic
   RNA strand by pairing complementary nucleotides (A-U, G-C) inside an
   alkaline hydrothermal vent.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from src.luca_engine.logger import get_game_logger

logger = get_game_logger("luca_engine.cosmos")

# Standard Watson-Crick RNA base-pairing rules
RNA_COMPLEMENT_MAP: Dict[str, str] = {
    "A": "U",
    "U": "A",
    "G": "C",
    "C": "G",
}


@dataclass
class CosmicStage:
    """Represents a single epoch in the cosmic prologue sequence."""

    stage_id: str
    title: str
    time_mya: float  # Millions of years ago
    temperature_kelvin: float
    description: str


COSMIC_TIMELINE: List[CosmicStage] = [
    CosmicStage(
        stage_id="big_bang",
        title="The Big Bang Singularity",
        time_mya=13800.0,
        temperature_kelvin=1.0e12,
        description="Rapid cosmic inflation expands quark-gluon plasma into hydrogen and helium.",
    ),
    CosmicStage(
        stage_id="stellar_forge",
        title="First Galaxies & Supernovae",
        time_mya=13200.0,
        temperature_kelvin=5.0e7,
        description="Massive Population III stars fuse heavy elements (C, N, O, Fe, P) and go supernova.",
    ),
    CosmicStage(
        stage_id="yellow_star",
        title="G-Type Yellow Star Ignition",
        time_mya=4600.0,
        temperature_kelvin=5778.0,
        description="A shockwave compresses a molecular cloud into our yellow sun and protoplanetary disk.",
    ),
    CosmicStage(
        stage_id="molten_earth",
        title="Hadean Molten Earth & Cooling Oceans",
        time_mya=4400.0,
        temperature_kelvin=450.0,
        description="Planetary crust solidifies; steam condenses into global oceans over alkaline vents.",
    ),
    CosmicStage(
        stage_id="luca_vent",
        title="Hydrothermal Vent RNA Soup",
        time_mya=4000.0,
        temperature_kelvin=345.0,
        description="Mineral pores concentrate nucleotides. Assemble the catalytic RNA ribozyme to awaken LUCA!",
    ),
]


@dataclass
class RNASoupPuzzle:
    """
    Interactive puzzle that simulates prebiotic RNA synthesis at a hydrothermal vent.

    Junior Dev Note:
    The player is given a template RNA strand (e.g., 'AUGCGAU') and must supply
    complementary bases ('UACGCUA') under thermal vent energy fluctuations.
    """

    template_strand: str = "AUGCGCAU"
    assembled_strand: List[str] = field(default_factory=list)
    vent_energy: float = 100.0
    is_luca_emerged: bool = False

    def __post_init__(self) -> None:
        """Validate template strand on initialization."""
        self.template_strand = self.template_strand.upper()
        for base in self.template_strand:
            if base not in RNA_COMPLEMENT_MAP:
                raise ValueError(f"Invalid RNA nucleotide in template: {base}")
        logger.info(
            "Initialized RNASoupPuzzle with template=%s", self.template_strand
        )

    def expected_next_base(self) -> str:
        """Return the complementary base required at the current cursor position."""
        if self.is_luca_emerged:
            return ""
        idx = len(self.assembled_strand)
        target_base = self.template_strand[idx]
        return RNA_COMPLEMENT_MAP[target_base]

    def attempt_pair(self, candidate_base: str) -> Tuple[bool, int, str]:
        """
        Attempt to bond a candidate nucleotide onto the growing RNA chain.

        Args:
            candidate_base: Single character ('A', 'U', 'G', or 'C').

        Returns:
            Tuple of (is_correct, bonus_dna_points, status_message).
        """
        if self.is_luca_emerged:
            return True, 0, "LUCA has already emerged from the hydrothermal vent!"

        candidate = candidate_base.upper().strip()
        if candidate not in RNA_COMPLEMENT_MAP:
            logger.warning("Rejected invalid nucleotide input: %s", candidate)
            return False, 0, f"Invalid base '{candidate}'. Choose A, U, G, or C."

        expected = self.expected_next_base()
        if candidate == expected:
            self.assembled_strand.append(candidate)
            logger.info(
                "RNA base paired: %s (%d/%d)",
                candidate,
                len(self.assembled_strand),
                len(self.template_strand),
            )
            if len(self.assembled_strand) == len(self.template_strand):
                self.is_luca_emerged = True
                reward = 50
                logger.info(
                    "LUCA EMERGED! Self-replicating ribozyme complete. Awarded %d DNA.",
                    reward,
                )
                return (
                    True,
                    reward,
                    "LUCA EMERGED! Proto-cell membrane formed around catalytic RNA!",
                )
            return True, 10, f"Hydrogen bond formed ({candidate})! +10 DNA Points."

        # Mismatch penalty reduces vent stability slightly
        self.vent_energy = max(10.0, self.vent_energy - 10.0)
        logger.debug(
            "RNA mismatch: tried %s but expected %s (vent_energy=%.1f)",
            candidate,
            expected,
            self.vent_energy,
        )
        return (
            False,
            0,
            f"Thermal mismatch! '{candidate}' does not pair with "
            f"'{self.template_strand[len(self.assembled_strand)]}'. Try '{expected}'.",
        )
