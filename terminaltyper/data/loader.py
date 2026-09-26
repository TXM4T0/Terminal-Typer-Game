"""
Data loader and word generator for Boss encounters and actions.
"""

import json
from pathlib import Path
import random
from typing import List, Optional
from terminaltyper.core.models import Boss, ActionType, StatusType, DifficultyMode

EMERGENCY_WORDS = ["run", "fix", "hop", "tag", "pop", "zap", "cut", "key", "hex", "cpu", "bot", "log"]
GLITCH_SYMBOLS = ["#", "@", "%", "*"]

BABY_WORD_BANKS = {
    "boss_01": {  # Slime Core - 2-3 arrow repetitions
        "jab": ["↑ ↑", "↓ ↓", "↑ ↓", "→ →", "← ←", "↓ ↑"],
        "heavy": ["↑ ↓ ↑", "← → ←", "↑ ↑ ↓", "↓ ↓ ↑", "→ → ←"],
        "parry": ["← →", "↑ ↓", "→ ←", "↓ ↑"],
        "rest": ["↑ ↑ ↑", "↓ ↓ ↓", "← ← ←"],
    },
    "boss_02": {  # Iron Golem - 3-4 arrows
        "jab": ["↑ ↓ ↑", "← → ←", "↓ ↑ ↓", "→ ← →"],
        "heavy": ["↑ ↑ ↓ ↓", "← ← → →", "↓ ↓ ↑ ↑", "→ → ← ←"],
        "parry": ["← → ← →", "↑ ↓ ↑ ↓"],
        "rest": ["↓ ↓ ↑ ↑", "↑ ↑ ↓ ↓", "← ← → →"],
    },
    "boss_03": {  # Swift Falcon - Sweeps & directional circles
        "jab": ["↑ → ↓", "↓ ← ↑", "→ ↓ ←", "← ↑ →"],
        "heavy": ["↑ → ↓ ← ↑", "↑ ← ↓ → ↑", "→ ↓ ← ↑ →"],
        "parry": ["← ↑ → ↓", "→ ↓ ← ↑"],
        "rest": ["↑ ↓ ← →", "→ ← ↓ ↑"],
    },
    "boss_04": {  # Shadow Doppelgänger - Inversions & mirrors
        "jab": ["↑ ↓ ↓ ↑", "← → → ←", "↓ ↑ ↑ ↓"],
        "heavy": ["↑ ← → ↓ → ←", "← ↑ ↓ → ↓ ↑", "→ ↓ ↑ ← ↑ →"],
        "parry": ["← → ← →", "↑ ↓ ↑ ↓", "→ ← → ←"],
        "rest": ["← ↑ ↑ ←", "→ ↓ ↓ →", "↑ ← ← ↑"],
    },
    "boss_05": {  # Frost Lich - Jagged zig-zags
        "jab": ["↑ ← ↑ →", "↓ → ↓ ←", "← ↑ ← ↓"],
        "heavy": ["↑ ↓ ← → ↑ ↓", "← → ↑ ↓ ← →", "↓ ↑ → ← ↓ ↑"],
        "parry": ["← ← → → ↑", "↑ ↑ ↓ ↓ →", "→ → ← ← ↓"],
        "rest": ["↓ ↑ ↓ ↑ ↓", "← → ← → ←"],
    },
    "boss_06": {  # Cyber Mech - Geometric circuits
        "jab": ["↑ → → ↑", "↓ ← ← ↓", "← ↑ ↑ ←", "→ ↓ ↓ →"],
        "heavy": ["↑ ↑ → → ↓ ↓ ←", "→ → ↓ ↓ ← ← ↑", "↓ ↓ ← ← ↑ ↑ →"],
        "parry": ["← ↑ → ↓ ←", "→ ↓ ← ↑ →", "↑ → ↓ ← ↑"],
        "rest": ["↑ ↓ ↑ ↓ ↑", "↓ ↑ ↓ ↑ ↓", "← → ← → ←"],
    },
    "boss_07": {  # Void Sovereign - Grand choreography (including Konami cadence!)
        "jab": ["↑ ↑ ↓ ↓ ←", "← → ← → ↑", "↓ ↓ ↑ ↑ →"],
        "heavy": ["↑ ↑ ↓ ↓ ← → ← →", "↑ → ↓ ← ↑ → ↓ ←", "→ ← ↓ ↑ → ← ↓ ↑"],
        "parry": ["← → ← → ↑ ↓", "↑ ↓ ↑ ↓ ← →"],
        "rest": ["↓ ↓ ↑ ↑ ← →", "↑ ↑ ↓ ↓ → ←"],
    },
}

BABY_EMERGENCY_WORDS = ["↑ ↓ ↑", "← → ←", "↑ ↑ ↑", "↓ ↓ ↓", "→ ← →"]

KING_HELL_PARAGRAPHS = {
    "boss_01": {  # Slime Core
        "jab": [
            "You lunge forward with calculated precision, slicing through the viscous jelly before the acidic core can react.",
            "A rapid burst of strikes disperses the gelatinous membrane, scattering caustic droplets harmlessly across the stone floor.",
        ],
        "heavy": [
            "Gathering all your kinetic momentum into a thunderous overhead blow, you drive your blade deep into the bubbling center. Caustic acid erupts in violent waves as the core ruptures under the overwhelming concussive force.",
            "You channel pure kinetic velocity through your boots and unleash a devastating shockwave that tears the slime puddle apart. Violent tremors ripple through the chamber as the destabilized slime collapses into steaming residue.",
        ],
        "parry": [
            "Bracing your guard against the acidic spray, you angle your shield so the caustic slime slides harmlessly away into the gutter.",
            "You anticipate the sudden gelatinous wave and deflect it with a sharp sidestep, preserving your posture and armor integrity.",
        ],
        "rest": [
            "Stepping back from the corrosive data pool, you activate internal thermal scrubbers to neutralize lingering acid and restore vital energy.",
            "You breathe deeply through your respirator, regulating your heartbeat as nanite repair fluids circulate to mend damaged tissue.",
        ],
    },
    "boss_02": {  # Iron Golem
        "jab": [
            "Dashing beneath the swinging iron fist, you deliver a rapid strike against the unarmored hydraulic joints of the towering automaton.",
            "Your swift blows strike the exposed rivets along the iron plating, sending resonant metallic clangs reverberating through the hall.",
        ],
        "heavy": [
            "You wind up an earth-shattering blow aimed directly at the golem's central furnace valve. The sheer impact buckles heavy steel plating, releasing a deafening hiss of pressurized steam and shattering internal iron gears into jagged shrapnel.",
            "Charging headlong into the behemoth, you strike with apocalyptic fury against the structural foundation of the automaton. Heavy tremors violently shake the arena as solid iron fractures under your merciless assault.",
        ],
        "parry": [
            "Planting your boots firmly into the stone ground, you lock your gauntlets together to deflect the descending iron fist.",
            "You redirect the brutal downward swing of the golem with an angled parry, letting kinetic momentum crash harmlessly into the floor.",
        ],
        "rest": [
            "Taking refuge behind a fallen stone pillar, you vent thermal heat registers and allow cooling conduits to restore combat readiness.",
            "You take a measured tactical pause to stabilize your breathing, allowing emergency repair subroutines to weld cracked armor seams.",
        ],
    },
    "boss_03": {  # Swift Falcon
        "jab": [
            "Tracking the blur of feathers through your optical sensors, you snap a lightning-quick jab into the falcon's flight vector.",
            "With razor reflexes, you intercept the diving raptor mid-swoop, clipping its wingtip with a sharp and decisive counter.",
        ],
        "heavy": [
            "Predicting the exact apex of the aerial descent, you unleash a catastrophic upward strike that shatters the sound barrier. The concussive sonic blast tears through the slipstream, ripping feathers away and sending the aerial predator crashing violently downward.",
            "You unleash a torrential flurry of devastating strikes that overwhelms the falcon's evasive instincts. Aerodynamic drag collapses entirely as your crushing onslaught drives the shrieking beast into the bedrock.",
        ],
        "parry": [
            "Tilting your defensive barrier at the last split second, you deflect the falcon's razor talons with an evasive barrel roll.",
            "You meet the supersonic dive with a calculated deflection, guiding the vicious aerodynamic strike harmlessly past your shoulder.",
        ],
        "rest": [
            "Scanning the turbulent skies for the next dive, you steady your trembling fingers and replenish depleted adrenaline stores.",
            "You draw a deep calming breath amidst the howling crosswinds, recalibrating your neural sync to match the falcon's tempo.",
        ],
    },
    "boss_04": {  # Shadow Doppelgänger
        "jab": [
            "Piercing the deceptive silhouette, you strike directly where the true reflection must anchor itself to physical reality.",
            "You feint to the left and drive a crisp strike through the dark mirage, shattering the illusion into dancing fragments of glass.",
        ],
        "heavy": [
            "Refusing to hesitate against your own twin image, you shatter the deceptive mirror with an all-out devastating assault. Black glass explodes outward in every direction as the twilight phantom dissolves into a shrieking cascade of severed shadows.",
            "You channel total mental focus to overpower the spectral double, striking through every mirrored defense with ruthless conviction. The silhouette fractures along jagged fault lines, collapsing into inert shadow dust.",
        ],
        "parry": [
            "Anticipating your own favorite attack angle, you counter the mirror blow with perfect symmetry, canceling all incoming kinetic force.",
            "You refuse to look into the phantom's hypnotic eyes, parrying the shadowy blade purely by acoustic telemetry and instinct.",
        ],
        "rest": [
            "Closing your eyes to clear lingering psychological illusions, you center your thoughts and restore mental equilibrium.",
            "You take a purposeful step back from the cracked mirror, steadying your pulse and expelling shadow corruption from your system.",
        ],
    },
    "boss_05": {  # Frost Lich
        "jab": [
            "Shattering the creeping rime on your knuckles, you snap a quick thrust into the pale aura of the spectral frost lord.",
            "You break through the brittle icicle barrier with a rapid jab, disrupting the lich's arcane invocation before frostbite takes hold.",
        ],
        "heavy": [
            "Igniting every ember of living warmth within your soul, you shatter the glacial tomb with an overwhelming volcanic strike. Superheated shockwaves incinerate the frozen mist, cracking the ancient crown and scattering brittle frozen bones across the permafrost.",
            "You deliver a merciless barrage of fiery strikes that overwhelms the freezing draft of absolute zero. Crystalline ice barriers disintegrate into boiling steam as your relentless fury obliterates the lich's icy defenses.",
        ],
        "parry": [
            "Raising your heated shield against the biting blizzard, you deflect the jagged hail of frozen needles with steadfast defiance.",
            "You absorb the freezing blast along your insulated guard, keeping kinetic warmth circulating through your hands to prevent numbness.",
        ],
        "rest": [
            "Cupping your hands around an internal heat coil, you thaw stiffened fingers and banish the paralyzing chill from your bloodstream.",
            "You kindle a slow and comforting breath of warm air, allowing thermal regulators to melt the frost encrusting your chest plate.",
        ],
    },
    "boss_06": {  # Cyber Mech
        "jab": [
            "Exploiting a brief millisecond delay in the targeting sweep, you drive a fast strike directly into the exposed sensory array.",
            "You slip past the whirring gatling barrel to deliver a pinpoint blow against the cooling manifold of the mechanized titan.",
        ],
        "heavy": [
            "Bypassing all mechanical safety limiters, you drive a devastating seismic impact straight into the mech's core reactor housing. Auxiliary cooling loops burst under the immense overload, spraying molten coolant and sending violent electrical arcs throughout the frame.",
            "You execute an unstoppable heavy demolition sequence against the structural chassis. Titanium joints crumple beneath your crushing blow as secondary explosions rip through the automated ammunition bays.",
        ],
        "parry": [
            "Angling your carbon-fiber barrier against the automated artillery volley, you disperse the concussive force into the grounding rails.",
            "You read the telltale whine of the charging laser and deflect the high-energy beam away from your vital power conduits.",
        ],
        "rest": [
            "Taking temporary cover behind a smoking blast door, you vent overheated heat sinks and initiate emergency system reboot cycles.",
            "You pause to flush corrupted memory registers, allowing auxiliary power cells to trickle charge your damaged kinetic capacitors.",
        ],
    },
    "boss_07": {  # Void Sovereign
        "jab": [
            "Defying the crushing gravitational tidal forces, you thrust forward to strike the shimmering boundary of the event horizon.",
            "You launch a focused kinetic dart into the singularity, maintaining your tangible physical form against the pull of nonexistence.",
        ],
        "heavy": [
            "With the fate of all remaining reality resting on your keys, you unleash an apocalyptic sequence that rips through the cosmic fabric. Blinding light detonates across the dark horizon, shattering the eternal singularity and rewriting the laws of entropy forever.",
            "You channel the collective memories of every fallen sector into a cataclysmic strike that pierces the infinite void. The cosmic silence shatters in an incandescent cascade of starlight that eradicates the sovereign from existence.",
        ],
        "parry": [
            "Holding fast against the infinite pull of entropy, you anchor your reality beacon to repel the gravitational collapse.",
            "You deflect the warping ripples of broken spacetime with sheer willpower, refusing to let your timeline unravel into oblivion.",
        ],
        "rest": [
            "Remembering the warmth of sunlight on distant worlds, you anchor your fleeting consciousness and rekindle the spark of living hope.",
            "You hold fast to your identity amidst the deafening void, allowing the quiet rhythm of your own heartbeat to restore vitality.",
        ],
    },
}

KING_HELL_EMERGENCY_WORDS = [
    "Emergency systems reboot as you shake off the concussive shock, clearing your vision and re-establishing combat protocol.",
    "You force your trembling hands back onto the controls, overriding sensory blackout and regaining stable tactical footing.",
    "Adrenaline surges through your veins as you break free from the disorienting haze, resetting your stance to engage once more.",
]


class DataLoader:
    def __init__(self, json_path: Optional[Path] = None):
        if json_path is None:
            json_path = Path(__file__).parent / "bosses.json"
        self.json_path = json_path
        self._raw_data = self._load_json()

    def _load_json(self) -> dict:
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_bosses(self) -> List[Boss]:
        """Loads and returns all 7 Boss objects in order."""
        boss_list = []
        for b_data in self._raw_data.get("boss_manifest", []):
            boss_list.append(Boss.from_dict(b_data))
        return boss_list

    def get_prompt_for_action(
        self,
        boss: Boss,
        action: ActionType,
        difficulty: Optional[DifficultyMode] = None
    ) -> str:
        """Selects a word, phrase, or arrow sequence according to action and difficulty."""
        diff_name = getattr(difficulty, "name", str(difficulty)) if difficulty else "NORMAL"

        if diff_name == "BABY":
            if action == ActionType.RECOVERY:
                return random.choice(BABY_EMERGENCY_WORDS)
            b_bank = BABY_WORD_BANKS.get(boss.id, BABY_WORD_BANKS["boss_01"])
            words = b_bank.get(action.value.lower(), ["↑ ↓ ← →"])
            return random.choice(words)

        if diff_name == "KING_HELL":
            if action == ActionType.RECOVERY:
                return random.choice(KING_HELL_EMERGENCY_WORDS)
            kh_boss = KING_HELL_PARAGRAPHS.get(boss.id, KING_HELL_PARAGRAPHS["boss_01"])
            paragraphs = kh_boss.get(action.value.lower(), [])
            if paragraphs:
                return random.choice(paragraphs)
            return random.choice(KING_HELL_EMERGENCY_WORDS)

        if action == ActionType.RECOVERY:
            return random.choice(EMERGENCY_WORDS)

        bank_key = action.value.lower()
        words = boss.word_banks.get(bank_key, [])
        if not words:
            # Fallback default banks
            defaults = {
                ActionType.JAB: ["fast", "dash", "hit", "kick"],
                ActionType.HEAVY: ["overwhelming", "devastating", "catastrophic"],
                ActionType.PARRY: ["defend", "counter", "shield"],
                ActionType.REST: ["take a breath", "restore energy"],
            }
            words = defaults.get(action, ["strike"])

        return random.choice(words)

    @staticmethod
    def apply_glitch_mask(prompt: str) -> str:
        """
        Masks 25% of prompt letters with terminal noise symbols (#, @, %, *).
        The player must still type the original correct letter.
        """
        chars = list(prompt)
        # Select indices of alphabetical or numeric characters
        eligible_indices = [i for i, c in enumerate(chars) if c not in (" ", "-", "'", "\"", ".", ":")]
        if not eligible_indices:
            return prompt

        count_to_mask = max(1, int(round(len(eligible_indices) * 0.25)))
        mask_indices = set(random.sample(eligible_indices, min(count_to_mask, len(eligible_indices))))

        masked = []
        for i, c in enumerate(chars):
            if i in mask_indices:
                masked.append(random.choice(GLITCH_SYMBOLS))
            else:
                masked.append(c)

        return "".join(masked)
