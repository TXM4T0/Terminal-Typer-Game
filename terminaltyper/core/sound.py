"""
Retro 8-bit sound effects engine.
Supports high-fidelity 8-bit WAV samples with asynchronous playback via winsound.PlaySound.
Gracefully falls back to winsound.Beep tone synthesis or silence if unsupported or disabled.
"""

import os
import sys
import threading
import time
from pathlib import Path

_winsound = None
if sys.platform == "win32":
    try:
        import winsound
        _winsound = winsound
    except ImportError:
        _winsound = None


class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.enabled = True
            cls._instance._sfx_dir = Path(__file__).resolve().parent.parent / "assets" / "sfx"
        return cls._instance

    def _play_wav(self, filename: str) -> bool:
        """Plays a WAV file asynchronously if available."""
        if not self.enabled or not _winsound:
            return False
        wav_path = self._sfx_dir / filename
        if wav_path.is_file():
            try:
                _winsound.PlaySound(str(wav_path), _winsound.SND_FILENAME | _winsound.SND_ASYNC)
                return True
            except Exception:
                return False
        return False

    def _play_pattern(self, pattern: list[tuple[int, int]]):
        """Plays a sequence of (frequency, duration_ms) tones asynchronously."""
        if not self.enabled or not _winsound:
            return

        def worker():
            for freq, dur in pattern:
                try:
                    if freq > 37:
                        _winsound.Beep(int(freq), int(dur))
                    else:
                        time.sleep(dur / 1000.0)
                except Exception:
                    pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def key_click(self):
        """Subtle blip when typing a key."""
        if not self._play_wav("click.wav"):
            self._play_pattern([(1400, 15)])

    def key_error(self):
        """Small buzz on mistyped key."""
        if not self._play_wav("error.wav"):
            self._play_pattern([(220, 30)])

    def menu_select(self):
        """Crisp two-tone menu interaction."""
        if not self._play_wav("select.wav"):
            self._play_pattern([(800, 30), (1200, 45)])

    def jab_hit(self):
        """Quick sharp strike."""
        if not self._play_wav("jab.wav"):
            self._play_pattern([(950, 40), (1150, 40)])

    def heavy_hit(self):
        """Heavier concussive strike."""
        if not self._play_wav("heavy.wav"):
            self._play_pattern([(400, 60), (280, 80)])

    def critical_hit(self):
        """Electrifying critical strike fanfare."""
        if not self._play_wav("crit.wav"):
            self._play_pattern([(880, 50), (1175, 60), (1760, 90)])

    def parry_defend(self):
        """Metallic shield block."""
        if not self._play_wav("parry.wav"):
            self._play_pattern([(1500, 30), (1800, 50), (1200, 40)])

    def heal_rest(self):
        """Warm soothing pulse."""
        if not self._play_wav("heal.wav"):
            self._play_pattern([(440, 60), (554, 60), (659, 80)])

    def fumble(self):
        """Dissonant low buzz for fumble."""
        if not self._play_wav("fumble.wav"):
            self._play_pattern([(190, 90), (150, 120)])

    def boss_attack(self):
        """Menacing low boss impact."""
        if not self._play_wav("boss_attack.wav"):
            self._play_pattern([(260, 80), (180, 100)])

    def boss_crit(self):
        """Devastating boss critical slam."""
        if not self._play_wav("boss_crit.wav"):
            self._play_pattern([(160, 100), (130, 140)])

    def victory_fanfare(self):
        """Triumphant 8-bit victory melody."""
        if not self._play_wav("victory.wav"):
            self._play_pattern([
                (523, 100),
                (659, 100),
                (784, 120),
                (1046, 250),
            ])

    def game_over_tune(self):
        """Mournful descending death sequence."""
        if not self._play_wav("game_over.wav"):
            self._play_pattern([
                (440, 150),
                (370, 180),
                (311, 200),
                (220, 350),
            ])

    def status_alert(self):
        """Hazard warning chirp."""
        if not self._play_wav("alert.wav"):
            self._play_pattern([(800, 40), (0, 30), (800, 40)])

    def hp_drain_tick(self):
        """Fast tick sound for HP bar animation."""
        if not self._play_wav("tick.wav"):
            self._play_pattern([(1200, 10)])


sound = SoundManager()
