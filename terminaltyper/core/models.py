"""
Data models and state structures for Terminal Typer: Battle Protocol.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
import random
from terminaltyper.core.metrics import TypingMetrics


class ActionType(Enum):
    JAB = "JAB"
    HEAVY = "HEAVY"
    PARRY = "PARRY"
    REST = "REST"
    RECOVERY = "RECOVERY"

    @property
    def label(self) -> str:
        labels = {
            ActionType.JAB: "JAB (Fast)",
            ActionType.HEAVY: "HEAVY (Power)",
            ActionType.PARRY: "PARRY (Guard)",
            ActionType.REST: "REST (Heal)",
            ActionType.RECOVERY: "EMERGENCY RECOVERY",
        }
        return labels.get(self, self.value)

    @property
    def accuracy_threshold(self) -> float:
        thresholds = {
            ActionType.JAB: 0.70,
            ActionType.HEAVY: 0.80,
            ActionType.PARRY: 0.90,
            ActionType.REST: 0.85,
            ActionType.RECOVERY: 0.70,
        }
        return thresholds.get(self, 0.70)


class StatusType(Enum):
    GLITCH = "GLITCH"
    CHILL = "CHILL"
    BURN = "BURN"
    STUMBLE = "STUMBLE"

    @property
    def description(self) -> str:
        descriptions = {
            StatusType.GLITCH: "25% of letters masked by terminal noise symbols",
            StatusType.CHILL: "Input timer window reduced by 30%",
            StatusType.BURN: "Deals 10 unblockable heat damage each round",
            StatusType.STUMBLE: "Command menu skipped; emergency recovery prompt forced",
        }
        return descriptions.get(self, "")

    @property
    def default_duration(self) -> int:
        durations = {
            StatusType.GLITCH: 2,
            StatusType.CHILL: 2,
            StatusType.BURN: 3,
            StatusType.STUMBLE: 1,
        }
        return durations.get(self, 1)


@dataclass
class BossMove:
    name: str
    min_dmg: int
    max_dmg: int
    weight: int
    status: Optional[StatusType | str] = None

    def roll_damage(self) -> tuple[int, bool]:
        """Rolls base boss damage and 10% critical roll (1.35x)."""
        base_dmg = random.randint(self.min_dmg, self.max_dmg)
        is_crit = random.random() < 0.10
        final_dmg = round(base_dmg * 1.35) if is_crit else base_dmg
        return final_dmg, is_crit


@dataclass
class Boss:
    id: str
    name: str
    level: int
    max_hp: int
    current_hp: int
    ascii_art: List[str]
    moves: List[BossMove]
    dialogue: Dict[str, str]
    word_banks: Dict[str, List[str]]
    theme: str = ""
    is_midfight_triggered: bool = False
    speed_limit_seconds: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Boss":
        moves = []
        for m in data.get("moves", []):
            st_raw = m.get("status")
            if st_raw == "RANDOM":
                st = "RANDOM"
            elif st_raw:
                st = StatusType[st_raw]
            else:
                st = None
            moves.append(
                BossMove(
                    name=m["name"],
                    min_dmg=m["min_dmg"],
                    max_dmg=m["max_dmg"],
                    weight=m["weight"],
                    status=st,
                )
            )

        return cls(
            id=data["id"],
            name=data["name"],
            level=data["level"],
            max_hp=data["max_hp"],
            current_hp=data["max_hp"],
            ascii_art=data.get("ascii", []),
            moves=moves,
            dialogue=data.get("dialogue", {}),
            word_banks=data.get("word_banks", {}),
            theme=data.get("theme", ""),
            speed_limit_seconds=data.get("speed_limit_seconds"),
        )

    def select_move(self) -> BossMove:
        """Weighted random selection of boss move."""
        weights = [m.weight for m in self.moves]
        return random.choices(self.moves, weights=weights, k=1)[0]


@dataclass
class Player:
    name: str = "COURIER"
    level: int = 1
    max_hp: int = 100
    current_hp: int = 100
    statuses: Dict[StatusType, int] = field(default_factory=dict)
    active_parry_mitigation: float = 0.0  # Percentage 0.0 to 0.75
    # Career telemetry
    total_damage_dealt: float = 0.0
    total_damage_taken: float = 0.0
    total_crits: int = 0
    total_fumbles: int = 0
    total_words_typed: int = 0
    highest_wpm: float = 0.0

    def add_status(self, status: StatusType, duration: Optional[int] = None) -> None:
        dur = duration if duration is not None else status.default_duration
        self.statuses[status] = dur

    def tick_statuses(self) -> List[str]:
        """Ticks active statuses and applies burn damage. Returns event logs."""
        logs = []
        expired = []

        if StatusType.BURN in self.statuses:
            self.current_hp = max(0, self.current_hp - 10)
            logs.append("> ALERT: High heat signature! Taking 10 residual burn damage.")

        for st in list(self.statuses.keys()):
            self.statuses[st] -= 1
            if self.statuses[st] <= 0:
                expired.append(st)

        for st in expired:
            del self.statuses[st]
            logs.append(f"> RECOVERY: Status effect [{st.name}] has cleared.")

        return logs

    def has_status(self, status: StatusType) -> bool:
        return status in self.statuses and self.statuses[status] > 0

    def get_status_display(self) -> str:
        if not self.statuses:
            return "NORMAL"
        return ", ".join(f"{st.name}({dur})" for st, dur in self.statuses.items())


@dataclass
class PlayerActionResult:
    action: ActionType
    metrics: TypingMetrics
    is_fumble: bool
    damage_dealt: float = 0.0
    hp_recovered: float = 0.0
    mitigation_pct: float = 0.0
    combat_logs: List[str] = field(default_factory=list)


class DifficultyMode(Enum):
    BABY = "BABY"
    NORMAL = "NORMAL"
    HARD = "HARD"
    KING_HELL = "KING_HELL"

    @property
    def label(self) -> str:
        labels = {
            DifficultyMode.BABY: "BABY (Novice / Arrow-Only)",
            DifficultyMode.NORMAL: "NORMAL (Tactical Standard)",
            DifficultyMode.HARD: "HARD (Cyber Overclock)",
            DifficultyMode.KING_HELL: "KING HELL (Paragraph Warfare)",
        }
        return labels.get(self, self.value)

    @property
    def timer_multiplier(self) -> float:
        """Time limit scaling per difficulty."""
        multipliers = {
            DifficultyMode.BABY: 1.5,
            DifficultyMode.NORMAL: 1.0,
            DifficultyMode.HARD: 0.75,
            DifficultyMode.KING_HELL: 0.55,
        }
        return multipliers.get(self, 1.0)

    @property
    def boss_damage_multiplier(self) -> float:
        """Boss damage scaling per difficulty."""
        multipliers = {
            DifficultyMode.BABY: 0.6,
            DifficultyMode.NORMAL: 1.0,
            DifficultyMode.HARD: 1.25,
            DifficultyMode.KING_HELL: 1.5,
        }
        return multipliers.get(self, 1.0)

    @property
    def accuracy_offset(self) -> float:
        """Offset applied to action accuracy success thresholds."""
        offsets = {
            DifficultyMode.BABY: -0.10,  # 10% more lenient
            DifficultyMode.NORMAL: 0.0,
            DifficultyMode.HARD: 0.05,   # 5% stricter
            DifficultyMode.KING_HELL: 0.08,  # 8% stricter (high discipline)
        }
        return offsets.get(self, 0.0)

    @property
    def crit_wpm_threshold(self) -> float:
        """Net WPM threshold to trigger Critical Strike."""
        thresholds = {
            DifficultyMode.BABY: 35.0,   # Accessible crits for baby mode
            DifficultyMode.NORMAL: 70.0,
            DifficultyMode.HARD: 75.0,
            DifficultyMode.KING_HELL: 80.0,
        }
        return thresholds.get(self, 70.0)


class ControlScheme(Enum):
    HYBRID = "HYBRID"   # Arrow Keys + WASD (Universal)
    ARROWS = "ARROWS"   # Arrow Keys Only
    WASD = "WASD"       # WASD Keys Only

    @property
    def label(self) -> str:
        labels = {
            ControlScheme.HYBRID: "ARROWS + WASD (Universal)",
            ControlScheme.ARROWS: "ARROW KEYS ONLY",
            ControlScheme.WASD: "WASD KEYS ONLY",
        }
        return labels.get(self, self.value)


@dataclass
class GameSettings:
    sound_enabled: bool = True
    text_speed_delay: float = 0.015  # seconds per char for typewriter (0 for instant)
    timer_multiplier: float = 1.0     # 1.0 standard, 1.5 relaxed, 0.7 hardcore
    color_enabled: bool = True
    screen_shake: bool = True
    animations_enabled: bool = True
    difficulty: DifficultyMode = DifficultyMode.NORMAL
    control_scheme: ControlScheme = ControlScheme.HYBRID

