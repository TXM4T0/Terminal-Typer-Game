"""
Turn-based combat state machine and real-time keystroke typing engine.
Implements the full 80-column ANSI battle loop, action resolution,
damage formulas, and status debuffs.
"""

import random
import sys
import time
from typing import Optional, Tuple

from terminaltyper.core.terminal import Terminal
from terminaltyper.core.metrics import calculate_metrics, TypingMetrics
from terminaltyper.core.models import Boss, Player, ActionType, StatusType, GameSettings, BossMove, DifficultyMode, ControlScheme
from terminaltyper.core.sound import sound
from terminaltyper.data.loader import DataLoader
from terminaltyper.ui.renderer import BattleRenderer
from terminaltyper.ui.animations import flash_screen, generate_dissolved_art
from terminaltyper.ui.ansi import (
    RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_MAGENTA, BRIGHT_WHITE
)


class BattleSession:
    def __init__(
        self,
        boss: Boss,
        player: Player,
        data_loader: DataLoader,
        settings: GameSettings
    ):
        self.boss = boss
        self.player = player
        self.loader = data_loader
        self.settings = settings
        self.renderer = BattleRenderer(width=80)
        self.current_dialogue = boss.dialogue.get("encounter", "A hostile entity blocks the datapath!")
        self.combat_log_history = []

    def _draw_frame(
        self,
        prompt: Optional[str] = None,
        typed: str = "",
        target_original: Optional[str] = None,
        telemetry_line: Optional[str] = None,
        status_msg: Optional[str] = None,
        show_actions: bool = True
    ) -> None:
        baby_mode = (getattr(self.settings, 'difficulty', None) == DifficultyMode.BABY)
        frame = self.renderer.render_full_screen(
            boss=self.boss,
            player=self.player,
            dialogue=self.current_dialogue,
            prompt=prompt,
            typed=typed,
            target_original=target_original,
            telemetry_line=telemetry_line,
            status_msg=status_msg,
            show_actions=show_actions,
            baby_mode=baby_mode
        )
        sys.stdout.write(f"\x1b[H{frame}\x1b[J")
        sys.stdout.flush()

    def _wait_for_advance(self, prompt_text: str = "PRESS [ENTER] TO ADVANCE...") -> None:
        self._draw_frame(
            status_msg=f"{BRIGHT_YELLOW}{prompt_text}{RESET}",
            show_actions=False
        )
        time.sleep(0.22)
        Terminal.flush_input()
        while True:
            ch = Terminal.get_char(timeout=0.1)
            if ch in ('\n', ' '):
                sound.menu_select()
                return

    def _animate_strike(self, action: ActionType, is_crit: bool) -> None:
        """Visual kinetic attack animations in the execution box."""
        if not getattr(self.settings, 'animations_enabled', True):
            return

        frames = []
        if action == ActionType.JAB:
            frames = [
                f"{BRIGHT_CYAN}>>>>>> [ JAB: HIGH-VELOCITY KINETIC BURST ] >>>>>>{RESET}",
                f"{BRIGHT_YELLOW}═════════ ✦ ✦ ✦ IMPACT DETONATION ✦ ✦ ✦ ═════════{RESET}"
            ]
        elif action == ActionType.HEAVY:
            frames = [
                f"{BRIGHT_YELLOW}(((( RESONANCE OVERLOAD: CYBERNETIC COIL CHARGING )))){RESET}",
                f"{BRIGHT_RED}▓▓▓▓▓▓▓▓▓▓▓▓▓ ⚡ ⚡ ⚡ SEISMIC CRUSH ⚡ ⚡ ⚡ ▓▓▓▓▓▓▓▓▓▓▓▓▓{RESET}"
            ]
        elif action == ActionType.PARRY:
            frames = [
                f"{BRIGHT_GREEN}┌────────────────────────────────────────────────────────┐{RESET}",
                f"{BRIGHT_GREEN}│ ⟨⟨⟨⟨⟨ KINETIC DEFLECTION MATRIX LINKED: 75% GUARD ⟩⟩⟩⟩ │{RESET}"
            ]
        elif action == ActionType.REST:
            frames = [
                f"{BRIGHT_MAGENTA}. : + + NANITE RESTORATION PROTOCOL + + : .{RESET}",
                f"{BRIGHT_MAGENTA}<< ⯌ ⯌ ⯌ REPAIRING CORE ARCHITECTURE ⯌ ⯌ ⯌ >>{RESET}"
            ]
        elif action == ActionType.RECOVERY:
            frames = [
                f"{BRIGHT_WHITE}[CLEARING CONCUSSION BUFFER...]{RESET}",
                f"{BRIGHT_GREEN}[RECOVERY SUCCESSFUL - STUMBLE CLEARED]{RESET}"
            ]

        for frame in frames:
            self._draw_frame(status_msg=frame, show_actions=False)
            time.sleep(0.06)

    def _animate_hp_drain(self, entity, start_hp: int, target_hp: int) -> None:
        """Smooth animated chunk-down / fill-up of HP bar with tick sound."""
        if not getattr(self.settings, 'animations_enabled', True):
            entity.current_hp = target_hp
            return

        diff = target_hp - start_hp
        if diff == 0:
            entity.current_hp = target_hp
            return

        steps = min(8, max(1, abs(diff) // 5))
        for i in range(1, steps + 1):
            curr = int(round(start_hp + (diff * (i / steps))))
            entity.current_hp = curr
            self._draw_frame(show_actions=False)
            sound.hp_drain_tick()
            time.sleep(0.025)

        entity.current_hp = target_hp

    def _animate_boss_defeat_dissolve(self) -> None:
        """Matrix noise dissolve animation for defeated boss."""
        if not getattr(self.settings, 'animations_enabled', True):
            return

        original_art = list(self.boss.ascii_art)
        for step in range(1, 5):
            self.boss.ascii_art = generate_dissolved_art(original_art, step=step, total_steps=4)
            self._draw_frame(
                status_msg=f"{BRIGHT_RED}[!] TARGET MATRIX DESTABILIZING...{RESET}",
                show_actions=False
            )
            sound.fumble()
            time.sleep(0.07)

        self.boss.ascii_art = original_art

    def _animate_boss_attack(self, move: BossMove, is_crit: bool) -> None:
        """Visual attack animation for boss moves."""
        if not getattr(self.settings, 'animations_enabled', True):
            return

        crit_tag = " [CRITICAL]" if is_crit else ""
        frames = [
            f"{BRIGHT_RED}<<<<<< [ WARNING: {self.boss.name.upper()} INCOMING{crit_tag} ] <<<<<<{RESET}",
            f"{BRIGHT_RED}█████████████ ☠ ☠ ☠ {move.name.upper()} ☠ ☠ ☠ █████████████{RESET}"
        ]
        for f in frames:
            self._draw_frame(status_msg=f, show_actions=False)
            time.sleep(0.06)


    def run_encounter(self) -> bool:
        Terminal.clear_screen()
        sound.status_alert()
        self._wait_for_advance("SECTOR BREACH: PRESS [ENTER] TO ENGAGE TARGET...")

        while self.boss.current_hp > 0 and self.player.current_hp > 0:
            self._execute_player_turn()
            if self.boss.current_hp <= 0:
                break
            self._execute_boss_turn()
            if self.player.current_hp <= 0:
                break

        if self.boss.current_hp <= 0:
            self._handle_boss_defeat()
            return True
        else:
            self._handle_player_defeat()
            return False

    def _execute_player_turn(self) -> None:
        diff = getattr(self.settings, 'difficulty', DifficultyMode.NORMAL)
        if self.player.has_status(StatusType.STUMBLE):
            self.current_dialogue = "CONCUSSIVE IMPACT! You stumble, forcing an emergency recovery sequence!"
            chosen_action = ActionType.RECOVERY
            target_word = self.loader.get_prompt_for_action(self.boss, chosen_action, difficulty=diff)
            self._draw_frame(
                status_msg=f"{BRIGHT_RED}[!] STUMBLED! PRESS [ENTER] FOR EMERGENCY RECOVERY...{RESET}",
                show_actions=False
            )
            Terminal.flush_input()
            while True:
                ch = Terminal.get_char(timeout=0.1)
                if ch in ('\n', ' '):
                    break
        else:
            chosen_action = self._select_action()
            target_word = self.loader.get_prompt_for_action(self.boss, chosen_action, difficulty=diff)

        displayed_prompt = target_word
        if self.player.has_status(StatusType.GLITCH):
            if diff == DifficultyMode.BABY or any(arrow in target_word for arrow in ("↑", "↓", "←", "→")):
                displayed_prompt = target_word
            else:
                displayed_prompt = self.loader.apply_glitch_mask(target_word)

        if self.boss.speed_limit_seconds is not None and diff != DifficultyMode.KING_HELL:
            base_time = self.boss.speed_limit_seconds
        elif diff == DifficultyMode.KING_HELL and self.boss.speed_limit_seconds is not None:
            # In King Hell mode, scale Swift Falcon's limit to paragraph length (tight ~65 WPM pace)
            base_time = max(8.0, (len(target_word) / 5.0) / (65.0 / 60.0))
        else:
            base_time = 3.0 + len(target_word) * 1.0

        time_limit = base_time * self.settings.timer_multiplier * diff.timer_multiplier
        if self.player.has_status(StatusType.CHILL):
            time_limit *= 0.7

        typed, elapsed = self._run_typing_loop(
            target_original=target_word,
            displayed_prompt=displayed_prompt,
            time_limit=time_limit,
            action=chosen_action
        )

        metrics = calculate_metrics(
            target_word,
            typed,
            elapsed,
            crit_threshold=diff.crit_wpm_threshold
        )
        self.player.total_words_typed += 1
        if metrics.net_wpm > self.player.highest_wpm:
            self.player.highest_wpm = metrics.net_wpm

        self._resolve_player_action(chosen_action, metrics, target_word)

    def _select_action(self) -> ActionType:
        self._draw_frame(show_actions=True)
        Terminal.flush_input()
        action_map = {
            '1': ActionType.JAB,
            '2': ActionType.HEAVY,
            '3': ActionType.PARRY,
            '4': ActionType.REST,
            Terminal.KEY_UP: ActionType.JAB,
            Terminal.KEY_RIGHT: ActionType.HEAVY,
            Terminal.KEY_LEFT: ActionType.PARRY,
            Terminal.KEY_DOWN: ActionType.REST,
            '↑': ActionType.JAB,
            '→': ActionType.HEAVY,
            '←': ActionType.PARRY,
            '↓': ActionType.REST,
            'H': ActionType.JAB,      # Windows console Up Arrow scancode fallback
            'M': ActionType.HEAVY,    # Windows console Right Arrow scancode fallback
            'K': ActionType.PARRY,    # Windows console Left Arrow scancode fallback
            'P': ActionType.REST,     # Windows console Down Arrow scancode fallback
            'w': ActionType.JAB,
            'W': ActionType.JAB,
            'd': ActionType.HEAVY,
            'D': ActionType.HEAVY,
            'a': ActionType.PARRY,
            'A': ActionType.PARRY,
            's': ActionType.REST,
            'S': ActionType.REST,
        }
        while True:
            ch = Terminal.get_char(timeout=0.1)
            if not ch:
                continue
            if ch in action_map:
                sound.menu_select()
                return action_map[ch]
            # Check normalized directional input (respecting control scheme)
            norm = Terminal.normalize_directional_input(ch, self.settings.control_scheme)
            if norm in action_map:
                sound.menu_select()
                return action_map[norm]

    def _run_typing_loop(
        self,
        target_original: str,
        displayed_prompt: str,
        time_limit: float,
        action: ActionType
    ) -> Tuple[str, float]:
        typed = ""
        start_time = time.perf_counter()
        is_arrow_mode = any(arrow in target_original for arrow in ("↑", "↓", "←", "→"))

        while True:
            now = time.perf_counter()
            elapsed = now - start_time
            remaining = max(0.0, time_limit - elapsed)

            if time_limit > 0:
                ratio = remaining / time_limit
            else:
                ratio = 0.0

            time_bar_len = 10
            filled = int(round(ratio * time_bar_len))
            if ratio > 0.4:
                bar_color = BRIGHT_GREEN
            elif ratio > 0.2:
                bar_color = BRIGHT_YELLOW
            else:
                bar_color = BRIGHT_RED

            t_bar = f"[{bar_color}{'█' * filled}{DIM}{'░' * (time_bar_len - filled)}{RESET}]"

            cur_mins = max(0.001, elapsed) / 60.0
            cur_wpm = (len(typed) / 5.0) / cur_mins

            telemetry_str = (
                f"TIME: {t_bar} {remaining:.1f}s | WPM: {cur_wpm:.1f} | LEN: {len(typed)}/{len(target_original)}"
            )

            status_help = "Enter arrow keys" if is_arrow_mode else "Enter prompt & press ENTER"
            self._draw_frame(
                prompt=displayed_prompt,
                typed=typed,
                target_original=target_original,
                telemetry_line=telemetry_str,
                status_msg=f"{BRIGHT_CYAN}[TYPING] {action.label}: {status_help}{RESET}",
                show_actions=False
            )

            if remaining <= 0:
                sound.fumble()
                break

            ch = Terminal.get_char(timeout=0.03)
            if ch is not None:
                if ch == '\n':
                    sound.menu_select()
                    break
                elif ch in ('\x08', '\b'):
                    if typed.endswith(" "):
                        typed = typed[:-2]
                    elif len(typed) > 0:
                        typed = typed[:-1]
                    sound.key_click()
                else:
                    dir_arrow = None
                    if is_arrow_mode:
                        dir_arrow = Terminal.normalize_directional_input(ch, self.settings.control_scheme)

                    if dir_arrow is not None:
                        typed += dir_arrow
                        # Auto-append space if next character in target is a space
                        if len(typed) < len(target_original) and target_original[len(typed)] == ' ':
                            typed += ' '

                        expected_idx = len(typed) - (2 if typed.endswith(' ') else 1)
                        if expected_idx < len(target_original) and typed[expected_idx] == target_original[expected_idx]:
                            sound.key_click()
                        else:
                            sound.key_error()

                        if typed == target_original:
                            time.sleep(0.05)
                            break
                    elif len(ch) == 1 and ch.isprintable():
                        expected_idx = len(typed)
                        # If typing a GLITCH masked character, accept letter case-insensitively
                        if (
                            expected_idx < len(target_original)
                            and expected_idx < len(displayed_prompt)
                            and displayed_prompt[expected_idx] in ("#", "@", "%", "*")
                        ):
                            if ch.lower() == target_original[expected_idx].lower():
                                typed += target_original[expected_idx]
                                sound.key_click()
                            else:
                                typed += ch
                                sound.key_error()
                        else:
                            typed += ch
                            if expected_idx < len(target_original) and typed[expected_idx] == target_original[expected_idx]:
                                sound.key_click()
                            else:
                                sound.key_error()

                        if typed == target_original:
                            time.sleep(0.05)
                            break

        total_elapsed = time.perf_counter() - start_time
        return typed, total_elapsed

    def _resolve_player_action(
        self,
        action: ActionType,
        metrics: TypingMetrics,
        target_original: str
    ) -> None:
        diff = getattr(self.settings, 'difficulty', DifficultyMode.NORMAL)
        threshold = max(0.50, action.accuracy_threshold + diff.accuracy_offset)
        is_success = metrics.accuracy >= threshold

        if not is_success:
            self.player.total_fumbles += 1
            sound.fumble()
            acc_pct = int(metrics.accuracy * 100)
            req_pct = int(threshold * 100)
            log = f"> FUMBLE! Accuracy fell to {acc_pct}% (Required: {req_pct}%). Your hands lost grip on the sequence!"
            self.current_dialogue = log
            self._wait_for_advance(f"{BRIGHT_RED}[FUMBLE DETECTED] PRESS [ENTER]...{RESET}")
            return

        if action == ActionType.JAB:
            dmg = round(metrics.net_wpm * 1.0 * metrics.crit_multiplier)
            self._animate_strike(action, metrics.is_crit)
            self._animate_hp_drain(self.boss, self.boss.current_hp, max(0, self.boss.current_hp - dmg))
            self.player.total_damage_dealt += dmg
            if metrics.is_crit:
                self.player.total_crits += 1
                sound.critical_hit()
                if self.settings.screen_shake:
                    flash_screen('\x1b[42m', 0.05)
                log = f"> CRITICAL STRIKE! 100% Accuracy delivered at {metrics.net_wpm:.1f} WPM! The strike echoes!"
            else:
                sound.jab_hit()
                log = f"> JAB STRIKES! Delivered {dmg} damage at {metrics.net_wpm:.1f} Net WPM."
            self.current_dialogue = log

        elif action == ActionType.HEAVY:
            dmg = round(metrics.net_wpm * 2.2 * metrics.crit_multiplier)
            self._animate_strike(action, metrics.is_crit)
            self._animate_hp_drain(self.boss, self.boss.current_hp, max(0, self.boss.current_hp - dmg))
            self.player.total_damage_dealt += dmg
            if metrics.is_crit:
                self.player.total_crits += 1
                sound.critical_hit()
                if self.settings.screen_shake:
                    flash_screen('\x1b[43m', 0.06)
                log = f"> CRITICAL STRIKE! 100% Accuracy delivered at {metrics.net_wpm:.1f} WPM! The strike echoes!"
            else:
                sound.heavy_hit()
                log = f"> HEAVY IMPACT! Dealt {dmg} devastating damage at {metrics.net_wpm:.1f} Net WPM."
            self.current_dialogue = log

        elif action == ActionType.PARRY:
            self._animate_strike(action, False)
            mitigation_pct = min(0.75, (metrics.net_wpm * 0.75) / 100.0)
            self.player.active_parry_mitigation = mitigation_pct
            sound.parry_defend()
            pct_int = int(round(mitigation_pct * 100))
            log = f"> PARRY LINKED! Incoming kinetic impact mitigated by {pct_int}%."
            self.current_dialogue = log

        elif action == ActionType.REST:
            self._animate_strike(action, False)
            heal = round(metrics.net_wpm * 0.6)
            prev_hp = self.player.current_hp
            target_hp = min(self.player.max_hp, self.player.current_hp + heal)
            actual_heal = target_hp - prev_hp
            self._animate_hp_drain(self.player, prev_hp, target_hp)
            sound.heal_rest()
            log = f"> REST PROTOCOL: Core recovered +{actual_heal} HP ({metrics.net_wpm:.1f} Net WPM)."
            self.current_dialogue = log

        elif action == ActionType.RECOVERY:
            self._animate_strike(action, False)
            sound.jab_hit()
            log = "> RECOVERED! Emergency sequence executed! Concussion cleared."
            if StatusType.STUMBLE in self.player.statuses:
                del self.player.statuses[StatusType.STUMBLE]
            self.current_dialogue = log

        if (
            self.boss.current_hp > 0
            and self.boss.current_hp <= self.boss.max_hp // 2
            and not self.boss.is_midfight_triggered
        ):
            self.boss.is_midfight_triggered = True
            mid_text = self.boss.dialogue.get("midfight")
            if mid_text:
                self.current_dialogue = f"{self.boss.name}: {mid_text}"

        self._wait_for_advance(f"{BRIGHT_GREEN}[ACTION RESOLVED] PRESS [ENTER] TO CONTINUE...{RESET}")

    def _execute_boss_turn(self) -> None:
        move = self.boss.select_move()
        base_dmg, is_crit = move.roll_damage()
        diff = getattr(self.settings, 'difficulty', DifficultyMode.NORMAL)
        base_dmg = max(1, int(round(base_dmg * diff.boss_damage_multiplier)))

        if self.player.active_parry_mitigation > 0:
            actual_dmg = max(1, round(base_dmg * (1.0 - self.player.active_parry_mitigation)))
            parry_used_pct = int(self.player.active_parry_mitigation * 100)
            self.player.active_parry_mitigation = 0.0
            parry_note = f" (Mitigated {parry_used_pct}%)"
        else:
            actual_dmg = base_dmg
            parry_note = ""

        self._animate_boss_attack(move, is_crit)
        self._animate_hp_drain(self.player, self.player.current_hp, max(0, self.player.current_hp - actual_dmg))
        self.player.total_damage_taken += actual_dmg

        if is_crit:
            sound.boss_crit()
            if self.settings.screen_shake:
                flash_screen('\x1b[41m', 0.08)
            dmg_log = f"> BOSS CRITICAL! {self.boss.name} used {move.name}! {actual_dmg} damage dealt!{parry_note}"
        else:
            sound.boss_attack()
            if self.settings.screen_shake:
                flash_screen('\x1b[41m', 0.04)
            dmg_log = f"> {self.boss.name} used {move.name}, dealing {actual_dmg} damage.{parry_note}"

        self.current_dialogue = dmg_log

        if move.status is not None:
            st = move.status
            if st == "RANDOM" or (isinstance(st, str) and st == "RANDOM"):
                st = random.choice([
                    StatusType.GLITCH,
                    StatusType.CHILL,
                    StatusType.BURN,
                    StatusType.STUMBLE
                ])
            if isinstance(st, str):
                st = StatusType[st]
            self.player.add_status(st)
            sound.status_alert()

            status_messages = {
                StatusType.BURN: "> ALERT: High heat signature! Taking residual burn damage each cycle.",
                StatusType.CHILL: "> WARNING: Cryo-lock engaged! Keystroke input window narrowed by 30%.",
                StatusType.GLITCH: "> CORRUPTION: Display buffer scrambled by glitch noise!",
                StatusType.STUMBLE: "> CONCUSSION: Heavy impact threw you off balance! Stumble inflicted!"
            }
            extra_msg = status_messages.get(st, f"> STATUS APPLIED: [{st.name}]!")
            self.current_dialogue += f" | {extra_msg}"

        self._wait_for_advance(f"{BRIGHT_RED}[HOSTILE STRIKE] PRESS [ENTER] TO ASSESS DAMAGE...{RESET}")

        tick_logs = self.player.tick_statuses()
        if tick_logs:
            self.current_dialogue = " | ".join(tick_logs)
            self._wait_for_advance(f"{YELLOW}[SYSTEM STATUS UPDATED] PRESS [ENTER]...{RESET}")

    def _handle_boss_defeat(self) -> None:
        self._animate_boss_defeat_dissolve()
        sound.victory_fanfare()
        defeat_msg = self.boss.dialogue.get("defeat", "Target anomaly disintegrated.")
        self.current_dialogue = f'{self.boss.name}: "{defeat_msg}"'
        self._wait_for_advance(f"{BRIGHT_GREEN}>>> TARGET PURGED! PRESS [ENTER] TO SECURE SECTOR...{RESET}")

    def _handle_player_defeat(self) -> None:
        sound.game_over_tune()
        self.current_dialogue = "> FATAL FAULT: Terminal signal lost. The Network Core remains corrupted."
        self._wait_for_advance(f"{BRIGHT_RED}>>> CONNECTION TERMINATED. PRESS [ENTER]...{RESET}")