"""
Game Engine and Campaign Progression Manager.
Handles campaign loop, sector level-ups, narrative transitions,
and victory/defeat sequence resolution.
"""

import sys
import time
from terminaltyper.core.terminal import Terminal
from terminaltyper.core.models import Player, Boss, GameSettings, StatusType
from terminaltyper.core.sound import sound
from terminaltyper.data.loader import DataLoader
from terminaltyper.game.battle import BattleSession
from terminaltyper.ui.animations import show_hex8_transmission, typewriter, animate_sector_warp
from terminaltyper.ui.renderer import make_box_row
from terminaltyper.ui.ansi import (
    RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_MAGENTA, BRIGHT_WHITE, visible_len
)

SECTOR_BASELINE_HP = {
    1: 100,
    2: 120,
    3: 130,
    4: 140,
    5: 150,
    6: 160,
    7: 180
}

SECTOR_PLAYER_LEVEL = {
    1: 1,
    2: 4,
    3: 7,
    4: 10,
    5: 14,
    6: 17,
    7: 20
}


class GameEngine:
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.loader = DataLoader()

    def run_campaign(self) -> None:
        show_hex8_transmission(text_speed=self.settings.text_speed_delay)

        player = Player(
            name="COURIER",
            level=SECTOR_PLAYER_LEVEL[1],
            max_hp=SECTOR_BASELINE_HP[1],
            current_hp=SECTOR_BASELINE_HP[1]
        )

        bosses = self.loader.get_all_bosses()
        total_sectors = len(bosses)

        for sector_idx, boss in enumerate(bosses, 1):
            player.level = SECTOR_PLAYER_LEVEL.get(sector_idx, player.level + 2)
            player.max_hp = SECTOR_BASELINE_HP.get(sector_idx, player.max_hp + 15)
            player.current_hp = player.max_hp
            player.statuses.clear()
            player.active_parry_mitigation = 0.0

            animate_sector_warp(sector_idx, total_sectors, enabled=self.settings.animations_enabled)
            self._show_sector_briefing(sector_idx, total_sectors, boss, player)

            battle = BattleSession(
                boss=boss,
                player=player,
                data_loader=self.loader,
                settings=self.settings
            )

            cleared = battle.run_encounter()
            if not cleared:
                self._show_game_over(sector_idx, boss, player)
                return

            if sector_idx < total_sectors:
                self._show_sector_cleared(sector_idx, boss, player)

        self._show_campaign_victory(player)

    def _show_sector_briefing(
        self,
        sector_num: int,
        total_sectors: int,
        boss: Boss,
        player: Player
    ) -> None:
        Terminal.clear_screen()
        border = "+------------------------------------------------------------------------------+"
        print(f"{CYAN}{border}{RESET}")
        print(f"{CYAN}{make_box_row(f' {BRIGHT_MAGENTA}[HEX-8 SECTOR BRIEFING: {sector_num}/{total_sectors}]{RESET}', 78)}{RESET}")
        print(f"{CYAN}{make_box_row('', 78)}{RESET}")
        print(f"{CYAN}{make_box_row(f' \"Courier, targeting Sector {sector_num} signature: [{boss.name.upper()}].\"', 78)}{RESET}")
        print(f"{CYAN}{make_box_row(f' Anomaly Threat Class   : Lv. {boss.level}', 78)}{RESET}")
        print(f"{CYAN}{make_box_row(f'{DIM} Operational Theme      : {boss.theme}{RESET}', 78)}{RESET}")
        print(f"{CYAN}{make_box_row('', 78)}{RESET}")
        print(f"{CYAN}{make_box_row(f'{BRIGHT_GREEN} COURIER INTEGRITY       : Lv. {player.level} | HP: {player.current_hp}/{player.max_hp} [BUFFER 100%]{RESET}', 78)}{RESET}")
        print(f"{CYAN}{border}{RESET}\n")

        sys.stdout.write(f"{BRIGHT_YELLOW}PRESS [ENTER] TO INFILTRATE SECTOR {sector_num}...{RESET}")
        sys.stdout.flush()

        Terminal.flush_input()
        Terminal.wait_for_enter()
        sound.menu_select()

    def _show_sector_cleared(
        self,
        sector_num: int,
        boss: Boss,
        player: Player
    ) -> None:
        Terminal.clear_screen()
        border = "+------------------------------------------------------------------------------+"
        print(f"{BRIGHT_GREEN}{border}{RESET}")
        print(f"{BRIGHT_GREEN}{make_box_row(f' [SECTOR {sector_num} PURGED: SUCCESS]', 78)}{RESET}")
        print(f"{BRIGHT_GREEN}{make_box_row('', 78)}{RESET}")
        print(f"{BRIGHT_GREEN}{make_box_row(f' Subroutine [{boss.name.upper()}] has been eradicated from root memory.', 78)}{RESET}")
        print(f"{BRIGHT_GREEN}{make_box_row('', 78)}{RESET}")
        print(f"{BRIGHT_GREEN}{make_box_row(f'{BRIGHT_YELLOW} [LEVEL UP] Courier calibrated to Lv. {SECTOR_PLAYER_LEVEL.get(sector_num + 1, player.level + 2)}!{RESET}', 78)}{RESET}")
        print(f"{BRIGHT_GREEN}{make_box_row(f'{BRIGHT_CYAN} [CORE REPAIRS] Frame restored to {SECTOR_BASELINE_HP.get(sector_num + 1, player.max_hp + 15)} HP.{RESET}', 78)}{RESET}")
        print(f"{BRIGHT_GREEN}{border}{RESET}\n")

        sys.stdout.write(f"{BRIGHT_YELLOW}PRESS [ENTER] TO ADVANCE TO SECTOR {sector_num + 1}...{RESET}")
        sys.stdout.flush()

        Terminal.flush_input()
        Terminal.wait_for_enter()
        sound.menu_select()

    def _show_game_over(
        self,
        sector_num: int,
        boss: Boss,
        player: Player
    ) -> None:
        Terminal.clear_screen()
        print(f"{BRIGHT_RED}+------------------------------------------------------------------------------+{RESET}")
        print(f"{BRIGHT_RED}| > FATAL FAULT: Terminal signal lost. The Network Core remains corrupted.    |{RESET}")
        print(f"{BRIGHT_RED}+------------------------------------------------------------------------------+{RESET}\n")

        print(f" {BRIGHT_WHITE}MISSION FAILURE REPORT:{RESET}")
        print(f"   Sector Reached      : Sector {sector_num} ({boss.name})")
        print(f"   Total Damage Dealt  : {player.total_damage_dealt:.0f}")
        print(f"   Total Damage Taken  : {player.total_damage_taken:.0f}")
        print(f"   Critical Strikes    : {player.total_crits}")
        print(f"   Action Fumbles      : {player.total_fumbles}")
        print(f"   Prompts Typed       : {player.total_words_typed}")
        print(f"   Peak Impact Velocity: {player.highest_wpm:.1f} WPM\n")

        print(f"{DIM}Press [ENTER] to return to Main Menu...{RESET}")
        Terminal.flush_input()
        Terminal.wait_for_enter()
        sound.menu_select()

    def _show_campaign_victory(self, player: Player) -> None:
        Terminal.clear_screen()
        sound.victory_fanfare()
        banner = """
   ========================================================================
   ____  ____   ___ _____ ___   ____ ___  _       ____ ___  __  __ ____  _     
  |  _ \\|  _ \\ / _ \\_   _/ _ \\ / ___/ _ \\| |     / ___/ _ \\|  \\/  |  _ \\| |    
  | |_) | |_) | | | || || | | | |  | | | | |    | |  | | | | |\\/| | |_) | |    
  |  __/|  _ <| |_| || || |_| | |__| |_| | |___ | |__| |_| | |  | |  __/| |___ 
  |_|   |_| \\_\\\\___/ |_| \\___/ \\____\\___/|_____(_)____\\___/|_|  |_|_|   |_____|
   ========================================================================
        """
        print(f"{BRIGHT_GREEN}{banner}{RESET}")
        print(f" {BRIGHT_CYAN}> PROTOCOL COMPLETE: All seven root sectors purged. Courier status: MASTER OPERATOR.{RESET}\n")

        print(f" {BRIGHT_YELLOW}[FINAL CAMPAIGN TELEMETRY]{RESET}")
        print("   Anomalies Neutralized : 7 / 7 (100% Core Integrity Restored)")
        print(f"   Courier Level Achieved: Lv. {player.level}")
        print(f"   Total Damage Delivered: {player.total_damage_dealt:.0f}")
        print(f"   Damage Sustained      : {player.total_damage_taken:.0f}")
        print(f"   Critical Strikes      : {player.total_crits}")
        print(f"   Action Fumbles        : {player.total_fumbles}")
        print(f"   Total Sequences Typed : {player.total_words_typed}")
        print(f"   Peak Speed Velocity   : {player.highest_wpm:.1f} WPM\n")

        print(f"{BRIGHT_WHITE} The Network Core hums in flawless synchronization.")
        print(f" You have rewritten reality with the speed of your fingers.{RESET}\n")

        print(f"{DIM}Press [ENTER] to return to Main Menu...{RESET}")
        Terminal.flush_input()
        Terminal.wait_for_enter()
        sound.menu_select()