#!/usr/bin/env python3
"""
Gameplay Preview Generator for Terminal Typer: Battle Protocol.

Simulates an authentic, high-speed tactical battle turn against Sector 1: Slime Core,
capturing the real-time ANSI terminal output and rendering each frame into pixel-perfect
terminal graphics using Pillow and Consolas font. Synchronizes with the game's actual
8-bit audio effects (keystrokes, heavy strike, crit chime, HP drain ticks, victory).

Exports:
- assets/gameplay.gif (Optimized looping GIF for README preview)
- assets/gameplay.mp4 (High-definition H.264 video with synchronized 8-bit audio)
"""

import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from terminaltyper.core.models import Player, ActionType, Boss
from terminaltyper.data.loader import DataLoader
from terminaltyper.ui.renderer import BattleRenderer
from terminaltyper.ui.ansi import (
    RESET, BOLD, DIM,
    BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_CYAN,
    BRIGHT_MAGENTA, BRIGHT_WHITE, YELLOW, CYAN
)

# Cyberpunk Terminal Color Palette
COLOR_MAP = {
    30: (110, 118, 129),   # Black / Dark Gray
    31: (248, 81, 73),     # Red
    32: (63, 185, 80),     # Green
    33: (210, 153, 34),    # Yellow
    34: (88, 166, 255),    # Blue
    35: (188, 140, 255),   # Magenta
    36: (56, 139, 253),    # Cyan
    37: (230, 237, 243),   # White
    90: (110, 118, 129),   # Bright Black
    91: (255, 123, 114),   # Bright Red
    92: (86, 211, 100),    # Bright Green
    93: (242, 204, 96),    # Bright Yellow
    94: (121, 192, 255),   # Bright Blue
    95: (210, 168, 255),   # Bright Magenta
    96: (121, 192, 255),   # Bright Cyan
    97: (255, 255, 255),   # Bright White
}

ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;]*[a-zA-Z])")


class FrameRenderer:
    """Renders 80-column ANSI terminal text into styled PNG images."""

    def __init__(self):
        font_path = "C:/Windows/Fonts/consola.ttf"
        font_bold_path = "C:/Windows/Fonts/consolab.ttf"
        if not os.path.exists(font_path):
            font_path = "consola.ttf"
            font_bold_path = "consolab.ttf"

        self.font = ImageFont.truetype(font_path, 18)
        self.font_bold = ImageFont.truetype(font_bold_path, 18)
        self.title_font = ImageFont.truetype(font_path, 13)

        self.char_w = 10
        self.char_h = 24
        self.pad_x = 28
        self.pad_top = 52
        self.pad_bot = 24
        self.img_w = self.pad_x * 2 + 80 * self.char_w  # 856 px
        self.img_h = self.pad_top + self.pad_bot + 20 * self.char_h  # 556 px

    def render_frame(self, frame_str: str) -> Image.Image:
        lines = frame_str.split("\n")
        # Ensure exact 20 lines (0 to 19)
        if len(lines) > 20:
            lines = lines[:20]
        elif len(lines) < 20:
            lines += ["|" + " " * 78 + "|"] * (20 - len(lines))

        img = Image.new("RGB", (self.img_w, self.img_h), (13, 17, 23))
        draw = ImageDraw.Draw(img)

        # Title bar background
        draw.rectangle([(0, 0), (self.img_w, 38)], fill=(22, 27, 34))
        draw.line([(0, 38), (self.img_w, 38)], fill=(48, 54, 61), width=1)

        # Window control buttons (macOS style)
        draw.ellipse([(16, 14), (26, 24)], fill=(255, 95, 86))
        draw.ellipse([(34, 14), (44, 24)], fill=(255, 189, 46))
        draw.ellipse([(52, 14), (62, 24)], fill=(39, 201, 63))

        # Centered Window Title
        title_text = "TERMINAL TYPER: BATTLE PROTOCOL — [80x24 ANSI VIEWPORT]"
        bbox = self.title_font.getbbox(title_text)
        title_w = bbox[2] - bbox[0]
        draw.text(((self.img_w - title_w) // 2, 12), title_text, font=self.title_font, fill=(139, 148, 158))

        # Render terminal lines
        for row_idx, line in enumerate(lines):
            y = self.pad_top + row_idx * self.char_h
            col_idx = 0
            fg = (230, 237, 243)
            bold = False
            dim = False

            parts = ANSI_SPLIT.split(line)
            for part in parts:
                if not part:
                    continue
                if part.startswith("\x1b[") and part.endswith("m"):
                    codes = part[2:-1].split(";")
                    for c in codes:
                        c_num = int(c) if c else 0
                        if c_num == 0:
                            fg = (230, 237, 243)
                            bold = False
                            dim = False
                        elif c_num == 1:
                            bold = True
                        elif c_num == 2:
                            dim = True
                        elif c_num in COLOR_MAP:
                            fg = COLOR_MAP[c_num]
                else:
                    curr_fg = fg
                    if dim:
                        curr_fg = (curr_fg[0] * 6 // 10, curr_fg[1] * 6 // 10, curr_fg[2] * 6 // 10)
                    use_font = self.font_bold if bold else self.font
                    for ch in part:
                        x = self.pad_x + col_idx * self.char_w
                        draw.text((x, y), ch, font=use_font, fill=curr_fg)
                        col_idx += 1

        return img


def generate_gameplay_frames_and_audio_cues() -> Tuple[List[Tuple[str, int]], List[Tuple[float, str, float]]]:
    """
    Generates:
    1. Sequence of (frame_ansi_str, repeat_count) at 12 FPS.
    2. List of (timestamp_sec, wav_filename, volume) audio cues.
    """
    loader = DataLoader()
    boss = loader.get_all_bosses()[0]  # Slime Core (HP: 120)
    player = Player(name="OPERATOR", level=1, max_hp=100, current_hp=100)
    renderer = BattleRenderer(width=80)

    frames: List[Tuple[str, int]] = []
    audio_cues: List[Tuple[float, str, float]] = []
    current_time_sec = 0.0
    fps = 12.0

    def add_frame(
        dialogue: str,
        prompt: str = None,
        typed: str = "",
        target_orig: str = None,
        telemetry: str = None,
        status_msg: str = None,
        show_actions: bool = True,
        repeat: int = 1,
        sfx: str = None,
        sfx_vol: float = 0.8
    ):
        nonlocal current_time_sec
        s = renderer.render_full_screen(
            boss=boss,
            player=player,
            dialogue=dialogue,
            prompt=prompt,
            typed=typed,
            target_original=target_orig,
            telemetry_line=telemetry,
            status_msg=status_msg,
            show_actions=show_actions,
            baby_mode=False
        )
        if sfx:
            audio_cues.append((current_time_sec, sfx, sfx_vol))

        frames.append((s, repeat))
        current_time_sec += repeat / fps

    # --- SCENE 1: ENCOUNTER START (1.2s = 14 frames) ---
    add_frame(
        dialogue="A volatile Slime Core bubbles up from the data pool!",
        status_msg=None,
        show_actions=True,
        repeat=14
    )

    # --- SCENE 2: ACTION SELECTED: HEAVY ATTACK (0.8s = 10 frames) ---
    target_prompt = "OVERCLOCK THE KINETIC COILS"
    add_frame(
        dialogue=f"{CYAN}COMMAND LOCKED:{RESET} Executing [2] HEAVY strike protocol!",
        prompt=target_prompt,
        typed="",
        target_orig=target_prompt,
        status_msg="TYPE WITH MAXIMUM VELOCITY & ACCURACY!",
        show_actions=False,
        repeat=10,
        sfx="select.wav",
        sfx_vol=0.9
    )

    # --- SCENE 3: REAL-TIME TYPING TELEMETRY (~2.5s = ~30 frames) ---
    typed_accum = ""
    wpm_values = [
        68.4, 74.2, 79.8, 83.5, 87.1, 90.4, 92.8, 95.1, 97.4, 99.0,
        100.5, 101.2, 102.0, 102.8, 103.4, 103.9, 104.2, 104.5, 104.8, 105.0,
        105.2, 105.4, 105.4, 105.4, 105.4, 105.4, 105.4
    ]

    for idx, ch in enumerate(target_prompt):
        typed_accum += ch
        wpm = wpm_values[min(idx, len(wpm_values) - 1)]
        is_crit = (wpm >= 90.0 and idx > 15)
        crit_str = f" {BRIGHT_YELLOW}[CRITICAL HIT!]{RESET}" if is_crit else ""
        telem = f"{wpm:.1f} GROSS WPM | ACC: 100.0% | NET: {wpm:.1f} WPM{crit_str}"

        rep = 2 if ch == " " else 1
        add_frame(
            dialogue="Synchronizing keystrokes with kinetic capacitors...",
            prompt=target_prompt,
            typed=typed_accum,
            target_orig=target_prompt,
            telemetry=telem,
            show_actions=False,
            repeat=rep,
            sfx="click.wav",
            sfx_vol=0.6
        )

    # Hold completed typing (0.4s = 5 frames)
    add_frame(
        dialogue="Keystroke sequence complete! DISCHARGING OVERLOAD!",
        prompt=target_prompt,
        typed=target_prompt,
        target_orig=target_prompt,
        telemetry=f"105.4 GROSS WPM | ACC: 100.0% | NET: 105.4 WPM {BRIGHT_YELLOW}[CRITICAL HIT!]{RESET}",
        show_actions=False,
        repeat=5
    )

    # --- SCENE 4: KINETIC ATTACK DETONATION (0.8s) ---
    add_frame(
        dialogue=f"{BRIGHT_YELLOW}CRITICAL BURST TRIGGERED! Resonance multiplier x1.5 active!{RESET}",
        telemetry=f"105.4 GROSS WPM | ACC: 100.0% | NET: 105.4 WPM {BRIGHT_YELLOW}[CRITICAL HIT!]{RESET}",
        status_msg=f"{BRIGHT_YELLOW}(((( RESONANCE OVERLOAD: CYBERNETIC COIL CHARGING )))){RESET}",
        show_actions=False,
        repeat=4,
        sfx="heavy.wav",
        sfx_vol=0.9
    )
    add_frame(
        dialogue=f"{BRIGHT_RED}CRITICAL HIT! Heavy seismic blast strikes Slime Core for 248 DMG!{RESET}",
        telemetry=f"105.4 GROSS WPM | ACC: 100.0% | NET: 105.4 WPM {BRIGHT_YELLOW}[CRITICAL HIT!]{RESET}",
        status_msg=f"{BRIGHT_RED}▓▓▓▓▓▓▓▓▓▓▓▓▓ ⚡ ⚡ ⚡ SEISMIC CRUSH ⚡ ⚡ ⚡ ▓▓▓▓▓▓▓▓▓▓▓▓▓{RESET}",
        show_actions=False,
        repeat=5,
        sfx="crit.wav",
        sfx_vol=1.0
    )

    # --- SCENE 5: DYNAMIC HP DRAIN (0.8s = 10 frames) ---
    drain_hps = [100, 75, 50, 25, 0]
    for hp in drain_hps:
        boss.current_hp = hp
        add_frame(
            dialogue="Slime Core structural integrity collapsing under kinetic impact!",
            telemetry=f"105.4 GROSS WPM | ACC: 100.0% | NET: 105.4 WPM {BRIGHT_YELLOW}[CRITICAL HIT!]{RESET}",
            status_msg=f"{BRIGHT_RED}>>> SLIME CORE HP DEPLETED <<< {RESET}",
            show_actions=False,
            repeat=2,
            sfx="tick.wav",
            sfx_vol=0.7
        )

    # --- SCENE 6: MATRIX DISSOLVE (0.8s = 8 frames) ---
    dissolve_stages = [
        ["   .----.   ", "  /  ..  \\  ", " (  o  o  ) ", "  \\  ░░  /  ", "  _.'  ░ '._", " (___░░░░___)"],
        ["   .░░░░.   ", "  /  ..  \\  ", " (  ░  ░  ) ", "  \\  ░░  /  ", "  _.░  ░ ░._", " (___░░░░___)"],
        ["   .░  ░.   ", "  /      \\  ", " (  ░     ) ", "  \\      /  ", "  _.░    ░._", " (___    ___)"],
        ["            ", "            ", "     ░      ", "            ", "            ", "            "]
    ]
    for stage in dissolve_stages:
        boss.ascii_art = stage
        add_frame(
            dialogue=f"{YELLOW}The Slime Core bursts into inert memory leaks!{RESET}",
            status_msg=f"{BRIGHT_WHITE}[TARGET ELIMINATED: MEMORY BUFFER RESTORED]{RESET}",
            show_actions=False,
            repeat=2
        )

    # --- SCENE 7: SECTOR CLEARED & VICTORY BANNER (1.8s = 22 frames) ---
    boss.ascii_art = [""] * 6
    add_frame(
        dialogue=f"{BRIGHT_GREEN}SECTOR 1 CLEARED! ACCESS GRANTED TO SECTOR 2 [FIREWALL].{RESET}",
        status_msg=f"{BRIGHT_YELLOW}VICTORY! EXP GAINED: +50 | TELEMETRY RANK: S+ | PRESS [ENTER]{RESET}",
        show_actions=False,
        repeat=22,
        sfx="victory.wav",
        sfx_vol=1.0
    )

    return frames, audio_cues


def synthesize_audio_track(
    audio_cues: List[Tuple[float, str, float]],
    total_duration_sec: float,
    output_wav_path: str
):
    """Mixes WAV sound effects into a single synchronized master audio track."""
    sfx_dir = os.path.join(PROJECT_ROOT, "terminaltyper", "assets", "sfx")
    sample_rate = 44100
    total_samples = int((total_duration_sec + 0.5) * sample_rate)
    master_buffer = [0] * total_samples

    for start_sec, filename, volume in audio_cues:
        wav_path = os.path.join(sfx_dir, filename)
        if not os.path.exists(wav_path):
            continue
        try:
            with wave.open(wav_path, "rb") as w:
                n_frames = w.getnframes()
                data = w.readframes(n_frames)
                samples = struct.unpack(f"<{len(data)//2}h", data)
                start_sample = int(start_sec * sample_rate)
                for i, samp in enumerate(samples):
                    target_idx = start_sample + i
                    if target_idx < total_samples:
                        mixed = int(master_buffer[target_idx] + samp * volume)
                        master_buffer[target_idx] = max(-32768, min(32767, mixed))
        except Exception:
            pass

    with wave.open(output_wav_path, "wb") as out_w:
        out_w.setnchannels(1)
        out_w.setsampwidth(2)
        out_w.setframerate(sample_rate)
        raw_bytes = struct.pack(f"<{len(master_buffer)}h", *master_buffer)
        out_w.writeframes(raw_bytes)


def build_media_assets():
    """Generates preview frames and encodes them into GIF and MP4."""
    print("⚡ Generating gameplay preview frames and audio cues from BattleRenderer...")
    frames_data, audio_cues = generate_gameplay_frames_and_audio_cues()
    fps = 12.0
    total_frames = sum(repeat for _, repeat in frames_data)
    total_duration_sec = total_frames / fps
    print(f"✓ Generated {len(frames_data)} keyframes ({total_frames} total frames, {total_duration_sec:.1f}s at 12 FPS)")

    renderer = FrameRenderer()
    assets_dir = os.path.join(PROJECT_ROOT, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    gif_output = os.path.join(assets_dir, "gameplay.gif")
    mp4_output = os.path.join(assets_dir, "gameplay.mp4")

    temp_dir = tempfile.mkdtemp(prefix="terminaltyper_preview_")
    try:
        frame_idx = 0
        cached_images: List[Image.Image] = []
        durations: List[int] = []

        print("⚡ Rendering styled terminal frames with Pillow...")
        for keyframe_idx, (ansi_str, repeat) in enumerate(frames_data):
            img = renderer.render_frame(ansi_str)
            for _ in range(repeat):
                frame_file = os.path.join(temp_dir, f"frame_{frame_idx:04d}.png")
                img.save(frame_file)
                frame_idx += 1
            cached_images.append(img)
            durations.append(int(repeat * (1000 / fps)))

        print(f"✓ Saved {frame_idx} PNG frames to temporary storage.")

        # Synthesize audio
        temp_audio = os.path.join(temp_dir, "soundtrack.wav")
        print("⚡ Synthesizing synchronized 8-bit audio track...")
        synthesize_audio_track(audio_cues, total_duration_sec, temp_audio)
        print(f"✓ Generated audio track: {temp_audio}")

        # Locate ffmpeg
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            winget_path = r"C:\Users\ACER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
            if os.path.exists(winget_path):
                ffmpeg_bin = winget_path

        if ffmpeg_bin:
            print(f"⚡ Encoding high-quality GIF with FFmpeg ({ffmpeg_bin})...")
            gif_cmd = [
                ffmpeg_bin, "-y",
                "-framerate", "12",
                "-i", os.path.join(temp_dir, "frame_%04d.png"),
                "-vf", "split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
                gif_output
            ]
            subprocess.run(gif_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            gif_size = os.path.getsize(gif_output) / (1024 * 1024)
            print(f"✓ Generated GIF: {gif_output} ({gif_size:.2f} MB)")

            print("⚡ Encoding high-definition MP4 with synchronized 8-bit audio...")
            mp4_cmd = [
                ffmpeg_bin, "-y",
                "-framerate", "12",
                "-i", os.path.join(temp_dir, "frame_%04d.png"),
                "-i", temp_audio,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-movflags", "+faststart",
                mp4_output
            ]
            subprocess.run(mp4_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            mp4_size = os.path.getsize(mp4_output) / (1024 * 1024)
            print(f"✓ Generated MP4: {mp4_output} ({mp4_size:.2f} MB)")
        else:
            print("⚠ FFmpeg not found, falling back to PIL GIF export...")
            cached_images[0].save(
                gif_output,
                save_all=True,
                append_images=cached_images[1:],
                duration=durations,
                loop=0,
                optimize=True
            )
            gif_size = os.path.getsize(gif_output) / (1024 * 1024)
            print(f"✓ Generated fallback GIF: {gif_output} ({gif_size:.2f} MB)")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n🎉 Gameplay preview assets generated successfully!")
    print(f"  - GIF: {gif_output}")
    if os.path.exists(mp4_output):
        print(f"  - MP4: {mp4_output}")


if __name__ == "__main__":
    build_media_assets()
