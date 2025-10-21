#!/usr/bin/env python3
"""
RageSmith · 愤怒熔炉 - Terminal forging rage relief game.

运行: python ragesmith.py
选项: 修改文件顶部 LANG = "zh" or "en" 切换语言。
降级策略: 自动检测声音与颜色支持，失败时静默降级。
"""
import curses
import time
import random
import textwrap
import os
import sys
import math
import locale
import json
from collections import deque, Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================
# Configuration & Localization
# ============================
LANG = "zh"  # change to "en" for English UI
locale.setlocale(locale.LC_ALL, "")

# Localization dictionaries
TEXT: Dict[str, Dict[str, str]] = {
    "zh": {
        "title": "RageSmith·愤怒熔炉",
        "press_any": "任意键开锻·怒火与诗",
        "phase_forge": "锻打阶段",
        "phase_cool": "冷却阶段",
        "combo": "连击",
        "anger": "怒火",
        "heat": "温度",
        "timer": "计时",
        "crit": "暴击",
        "apm": "APM",
        "tips_slow": "节拍提示: —— 拍 —— 拍 ——",
        "tips_fast": "降温! 换气!",
        "cool_msg": "跟着节奏呼吸: 吸4-停7-呼8",
        "cool_msg_alt": "方块呼吸: 上-停-下-停",
        "save_prompt": "按 S 保存战报 · 按 R 重开 · 按 Q 退出",
        "saved": "战报已写入",
        "save_fail": "保存失败",
        "farewell": "怒气收刀，江湖再见",
        "report_title": "怒气战报",
        "poem_title": "愤怒打油诗",
        "combo_stage_1": "炉火纯青",
        "combo_stage_2": "怒火燎原",
        "combo_stage_3": "熔岩奔涌",
        "heavy_ready": "重锤就绪",
        "heavy_wait": "重锤冷却",
        "breath_hint": "回车换气!",
        "block_hint": "方向键闪避",
        "gentle_quote": "把怒气打成诗，我至少赢了这90秒。",
        "gentle_quote_alt": "怒火揉成铁花，生活也得看我颜色。",
        "no_curses": "终端不支持 curses，尝试使用普通输出模式。",
        "relaunch": "Windows 用户请尝试: py ragesmith.py",
        "init_fail": "UI 初始化失败，降级为文本模式。",
    },
    "en": {
        "title": "RageSmith · Furnace of Fury",
        "press_any": "Smash any key to begin forging.",
        "phase_forge": "Forge Phase",
        "phase_cool": "Cooldown",
        "combo": "Combo",
        "anger": "Fury",
        "heat": "Heat",
        "timer": "Timer",
        "crit": "Crit",
        "apm": "APM",
        "tips_slow": "Beat cue: —— tap —— tap ——",
        "tips_fast": "Cool down! Breathe!",
        "cool_msg": "Follow 4-7-8 breathing",
        "cool_msg_alt": "Box breathing incoming",
        "save_prompt": "S to save · R to restart · Q to quit",
        "saved": "Run saved",
        "save_fail": "Save failed",
        "farewell": "Furnace sleeps. See you soon.",
        "report_title": "Rage Report",
        "poem_title": "Howl Chant",
        "combo_stage_1": "Ember Whisper",
        "combo_stage_2": "Wildfire Bloom",
        "combo_stage_3": "Lava Surge",
        "heavy_ready": "Heavy hammer ready",
        "heavy_wait": "Heavy hammer cooling",
        "breath_hint": "Press Enter to vent",
        "block_hint": "Arrow keys to sidestep",
        "gentle_quote": "Forged rage into verse; I owned these 90 seconds.",
        "gentle_quote_alt": "I bent lava into fireworks. Life must adapt.",
        "no_curses": "Terminal lacks curses, falling back to text mode.",
        "relaunch": "Windows tip: try `py ragesmith.py`",
        "init_fail": "Failed to init UI; using text fallback.",
    },
}

LANG_TEXT = TEXT.get(LANG, TEXT["en"])

# Banter pools (>=40 each)
BANter_ZH = [
    "这锤法，隔壁铁匠都怕。",
    "火星落你脸上了快吹吹。",
    "怒火值告警: 请保持狂暴。",
    "键盘要报警了。",
    "别停！停了就输给了气。",
    "你敲的不是键，是人生不公。",
    "节奏好感人，请继续。",
    "怒火熔浆正在翻滚。",
    "焦躁层积累，考虑换气。",
    "重锤冷却中，别急。",
    "你这波是复读机转世吧。",
    "怒气翻倍！掌控节奏！",
    "小心温度爆表。",
    "连击养成中，别断。",
    "你是火山喷发前夜。",
    "键帽快熔了。",
    "节奏略虚，来个重击？",
    "半拍迟疑，差点掉链子。",
    "呼吸像风箱一样狂。",
    "炉火：咆哮好评。",
    "焦躁层解锁，请回车换气。",
    "怒火坩埚饱和80%。",
    "想起来的那句吐槽，说出来。",
    "方向键给你挡住了怨气。",
    "击打偏慢，给个节拍：咚…咚…",
    "暴击！火花炸成烟花。",
    "你不是在敲键，是在敲命运。",
    "怒火的味道，有点烤焦。",
    "继续！这是对抗无能为力的方式。",
    "键盘喃喃: 今日也好忙。",
    "怒火被你刻成花纹。",
    "这段怒意值得收藏。",
    "暴击概率拉满，别停。",
    "快上空格重锤！",
    "你这节奏可以出碟了。",
    "怒火+1，平衡感-1。",
    "键程也有尊严，轻点？算了猛敲吧。",
    "火花飞溅，靶子害怕。",
    "别忘了你还有方向键。",
    "你的怒火正在给未来打草稿。",
    "这个世界欠你一句服气。",
    "记得保存这场战斗。",
    "APM已超越办公室平均。",
    "下个连击段位要到了。",
]

BANter_EN = [
    "Even anvils fear your tempo.",
    "Sparks on your face—wipe or wear?",
    "Fury alert: maintain berserk mode.",
    "Keyboard contacting HR soon.",
    "Don't stop; rage hates silence.",
    "You're striking injustice itself.",
    "Beat so clean it's legal rhythm.",
    "Molten river rising fast.",
    "Agitation stacks high, vent soon.",
    "Heavy hammer cooling, patience.",
    "Copy machine reincarnated in you.",
    "Fury doubled! Own the beat!",
    "Heat meter flirting with meltdown.",
    "Combo cocoon, don't drop.",
    "Volcano eve, that's you.",
    "Keycaps smell toasty.",
    "Tempo wobbly—swing harder?",
    "Half-beat hesitation almost fatal.",
    "Breath bellows roaring.",
    "Forge approves this roar.",
    "Agitation layer unlocked: vent!",
    "Cauldron at 80% magma.",
    "Voice that comeback!",
    "Arrow keys shielding your feelings.",
    "Too slow—here's your metronome: thud… thud…",
    "CRIT! Fireworks detonate.",
    "You're pounding destiny, not keys.",
    "Smells like burning frustration.",
    "Keep going—this is resistance training.",
    "Keyboard whisper: overworked again.",
    "You carved patterns into rage.",
    "This anger deserves a frame.",
    "Crit chance maxed—stay wild.",
    "Hit space! Heavy blow!",
    "This beat could drop an album.",
    "Fury +1, balance -1.",
    "Switch says: maybe lighter? Nah smash.",
    "Sparks everywhere; targets tremble.",
    "Don't forget arrow parry.",
    "Your rage drafts tomorrow's script.",
    "World owes you a respectful nod.",
    "Save this duel for the archives.",
    "APM above office average.",
    "New combo rank incoming.",
]

BANter = BANter_ZH if LANG == "zh" else BANter_EN

# =============================
# Audio Handling
# =============================
class AudioEngine:
    """Handles optional audio cues with graceful degradation."""

    def __init__(self) -> None:
        self.platform = sys.platform
        self.available = False
        self.use_winsound = False
        self.use_simpleaudio = False
        self._init_audio()

    def _init_audio(self) -> None:
        try:
            if self.platform.startswith("win"):
                import winsound  # type: ignore

                self._winsound = winsound
                self.use_winsound = True
                self.available = True
            else:
                import simpleaudio  # type: ignore

                self._simpleaudio = simpleaudio
                self.use_simpleaudio = True
                self.available = True
        except Exception:
            self.available = False

    def play_beep(self, freq: int = 600, duration_ms: int = 80) -> None:
        if not self.available:
            return
        try:
            if self.use_winsound:
                self._winsound.Beep(freq, duration_ms)  # type: ignore[attr-defined]
            elif self.use_simpleaudio:
                # create tone buffer
                sample_rate = 44100
                t = duration_ms / 1000.0
                num_samples = int(sample_rate * t)
                import numpy as np  # type: ignore

                arr = (np.sin(2 * np.pi * freq * np.arange(num_samples) / sample_rate) * 0.3)
                audio = (arr * (2 ** 15 - 1)).astype(np.int16)
                self._simpleaudio.play_buffer(audio, 1, 2, sample_rate)  # type: ignore[attr-defined]
        except Exception:
            self.available = False


# =============================
# Data Models
# =============================
@dataclass
class ComboStage:
    threshold: int
    name: str


@dataclass
class GameStats:
    total_hits: int = 0
    crits: int = 0
    max_combo: int = 0
    anger: float = 0.0
    heat: float = 0.0
    heavy_used: int = 0
    blocks: int = 0
    breaths: int = 0
    duration: float = 0.0
    key_history: List[str] = field(default_factory=list)

    def record_hit(self, key_repr: str) -> None:
        self.total_hits += 1
        if key_repr:
            self.key_history.append(key_repr)

    def register_combo(self, combo: int) -> None:
        if combo > self.max_combo:
            self.max_combo = combo


@dataclass
class GameState:
    stats: GameStats = field(default_factory=GameStats)
    combo: int = 0
    combo_timer: float = 0.0
    anger: float = 0.0
    heat: float = 0.0
    crits: int = 0
    heavy_cooldown: float = 0.0
    agitation: float = 0.0
    combo_stage: int = 0
    last_input_time: float = 0.0
    messages: deque = field(default_factory=lambda: deque(maxlen=5))

    def tick(self, dt: float) -> None:
        # combo decay after 1 second of inactivity
        if time.time() - self.last_input_time > 1.0 and self.combo > 0:
            decay = dt * 5  # lose combo gradually
            self.combo = max(0, self.combo - int(decay))
        if self.heavy_cooldown > 0:
            self.heavy_cooldown = max(0.0, self.heavy_cooldown - dt)
        # agitation leads to heat increase to penalize
        if self.agitation > 0:
            self.agitation = max(0.0, self.agitation - dt * 0.4)
        self.stats.anger = self.anger
        self.stats.heat = self.heat

    def register_input(self, base_heat: float, is_crit: bool, key_repr: str) -> None:
        now = time.time()
        self.last_input_time = now
        self.combo += 1
        self.combo_timer = now
        combo_mult = 1.0 + min(self.combo / 50.0, 1.5)
        heat_gain = base_heat * combo_mult
        crit_mult = 1.5 if is_crit else 1.0
        overheat_penalty = 0.5 if self.heat > 80 else 1.0
        anger_gain = heat_gain * crit_mult * overheat_penalty
        self.anger += anger_gain
        self.heat = min(100.0, self.heat + base_heat * 0.7)
        self.agitation = min(100.0, self.agitation + 1.0)
        self.stats.record_hit(key_repr)
        if is_crit:
            self.crits += 1
            self.stats.crits = self.crits
        self.stats.register_combo(self.combo)

    def heavy_blow(self) -> bool:
        if self.heavy_cooldown > 0:
            return False
        self.heavy_cooldown = 3.0
        return True

    def vent(self) -> None:
        self.heat = max(0.0, self.heat - 20.0)
        self.agitation = max(0.0, self.agitation - 15.0)
        self.stats.breaths += 1

    def block(self) -> None:
        self.agitation = max(0.0, self.agitation - 5.0)
        self.stats.blocks += 1


# =============================
# Utility Functions
# =============================

def format_time(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def clamp(n: float, low: float, high: float) -> float:
    return max(low, min(high, n))


# =============================
# Poem & Report Generator
# =============================
class PoemGenerator:
    """Generates a short post-run poem based on stats."""

    POEM_TEMPLATES_ZH = [
        "{combo}连击敲醒铁星尘，{anger}怒火写在掌心纹。",
        "重锤三秒雷声滚，{heat}度炉心仍不熄。",
        "一口焦躁吹成风，键帽化雪也从容。",
        "暴击如雷鸣，{apm}次起伏都是证词。",
        "怒海翻涌却成诗，{top_word}成了压轴字。",
    ]

    POEM_TEMPLATES_EN = [
        "{combo} combo woke the iron stars; {anger} fury etched your palms.",
        "Heavy blows on cooldown storms; {heat} heat yet forge still hums.",
        "Restless breath turned into gust; keycaps melt but you stay just.",
        "Crits like thunder; {apm} strokes testify.",
        "Rage became verse with {top_word} as final cry.",
    ]

    BORDER = [
        "╔" + "═" * 46 + "╗",
        "╚" + "═" * 46 + "╝",
    ]

    def __init__(self, lang: str = "zh") -> None:
        self.lang = lang

    def generate_poem(self, stats: GameStats, top_word: str) -> List[str]:
        templates = self.POEM_TEMPLATES_ZH if self.lang == "zh" else self.POEM_TEMPLATES_EN
        tpl = random.choice(templates)
        poem_text = tpl.format(
            combo=stats.max_combo,
            anger=int(stats.anger),
            heat=int(stats.heat),
            apm=int(self._compute_apm(stats)),
            top_word=top_word or ("怒" if self.lang == "zh" else "rage"),
        )
        lines = textwrap.wrap(poem_text, width=44)
        bordered = [self.BORDER[0]]
        for line in lines:
            bordered.append("║ " + line.ljust(44) + "║")
        bordered.append(self.BORDER[1])
        return bordered

    def build_report(self, stats: GameStats, top_words: List[str]) -> List[str]:
        apm = self._compute_apm(stats)
        words = ", ".join(top_words) if top_words else ("怒" if self.lang == "zh" else "rage")
        if self.lang == "zh":
            report_lines = [
                f"总按键: {stats.total_hits}",
                f"最高连击: {stats.max_combo}",
                f"平均APM: {apm:.1f}",
                f"暴击次数: {stats.crits}",
                f"最常用咒骂词根: {words}",
            ]
        else:
            report_lines = [
                f"Total hits: {stats.total_hits}",
                f"Max combo: {stats.max_combo}",
                f"Avg APM: {apm:.1f}",
                f"Crits: {stats.crits}",
                f"Top curse roots: {words}",
            ]
        return report_lines

    def _compute_apm(self, stats: GameStats) -> float:
        duration = max(stats.duration, 1.0)
        return stats.total_hits / (duration / 60.0)


# =============================
# View Rendering
# =============================
class ForgeView:
    """Responsible for drawing the forge scene using curses."""

    ANVIL_FRAMES = [
        [
            "      (\\",
            "       \\\\__",
            "  _    (____)",
            " / \\   /    \\\",
            "|   | | RAGE |",
            " \\_/  |_____|",
            "   \\  /    /",
            "    \\(_(__/",
        ],
        [
            "      (\\",
            "   *   \\\\__",
            " *_*   (____)",
            " / \\  */   \\\",
            "|   | | RAGE |",
            " \\_/  |_____|",
            " * \\ */   /",
            "    \\(_(__/",
        ],
        [
            "      (\\",
            "  *    \\\\__",
            " *_*   (____)",
            " / \\ */   \\\",
            "|   | | RAGE |",
            " \\_/  |_____|",
            " * \\ */   /",
            "  * \\(_(__/",
        ],
    ]

    def __init__(self, stdscr: "curses._CursesWindow", lang: str = "zh") -> None:
        self.stdscr = stdscr
        self.lang = lang
        self.height, self.width = stdscr.getmaxyx()
        self.spark_idx = 0
        self.color_enabled = False
        self._init_colors()
        self.banter = deque(maxlen=5)

    def _init_colors(self) -> None:
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_RED, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_CYAN, -1)
            curses.init_pair(4, curses.COLOR_MAGENTA, -1)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
            self.color_enabled = True

    def add_message(self, text: str) -> None:
        self.banter.appendleft(text[:self.width - 4])

    def draw_header(self, state: GameState, phase: str, remaining: float) -> None:
        header = f" {LANG_TEXT['title']} | {phase} | {LANG_TEXT['timer']}: {format_time(remaining)}"
        self._write(0, 0, header[: self.width - 1], curses.color_pair(3) if self.color_enabled else 0)

    def draw_stats(self, state: GameState) -> None:
        combo_line = f"{LANG_TEXT['combo']}: {state.combo}"
        anger_line = f"{LANG_TEXT['anger']}: {int(state.anger)}"
        heat_line = f"{LANG_TEXT['heat']}: {int(state.heat)}"
        crit_line = f"{LANG_TEXT['crit']}: {state.crits}"
        heavy_hint = LANG_TEXT['heavy_ready'] if state.heavy_cooldown <= 0 else f"{LANG_TEXT['heavy_wait']}: {state.heavy_cooldown:.1f}s"
        lines = [combo_line, anger_line, heat_line, crit_line, heavy_hint]
        for idx, line in enumerate(lines, start=1):
            attr = curses.A_BOLD if self.color_enabled else curses.A_DIM
            self._write(idx, 2, line, attr)
        if state.combo >= 60:
            self._flash_rank(LANG_TEXT['combo_stage_3'])
        elif state.combo >= 30:
            self._flash_rank(LANG_TEXT['combo_stage_2'])
        elif state.combo >= 10:
            self._flash_rank(LANG_TEXT['combo_stage_1'])

    def draw_anvil(self, intensity: float = 0.0) -> None:
        frame = self.ANVIL_FRAMES[self.spark_idx % len(self.ANVIL_FRAMES)]
        start_y = 7
        start_x = 2
        jitter = int(intensity * 2)
        for i, line in enumerate(frame):
            self._write(start_y + i + random.randint(0, jitter), start_x, line, curses.color_pair(2) if self.color_enabled else 0)
        self.spark_idx += 1

    def draw_messages(self) -> None:
        y = 2
        x = self.width // 2
        for msg in list(self.banter):
            if y < self.height - 2:
                self._write(y, x, msg)
                y += 1

    def draw_meter(self, label: str, value: float, max_value: float, row: int, color_idx: int = 1) -> None:
        bar_width = self.width // 4
        filled = int((value / max_value) * bar_width)
        bar = "█" * filled + "-" * (bar_width - filled)
        attr = curses.color_pair(color_idx) if self.color_enabled else curses.A_DIM
        self._write(row, 2, f"{label}: [{bar}] {int(value)}", attr)

    def draw_footer(self, tip: str) -> None:
        self._write(self.height - 2, 2, tip[: self.width - 4], curses.A_DIM)

    def draw_center_text(self, lines: List[str]) -> None:
        mid_y = self.height // 2 - len(lines) // 2
        mid_x = max(2, self.width // 2 - max(len(line) for line in lines) // 2)
        for idx, line in enumerate(lines):
            self._write(mid_y + idx, mid_x, line, curses.color_pair(4) if self.color_enabled else curses.A_BOLD)

    def _flash_rank(self, text: str) -> None:
        self._write(1, self.width // 2, text, curses.color_pair(5) if self.color_enabled else curses.A_REVERSE)

    def _write(self, y: int, x: int, text: str, attr: int = 0) -> None:
        if 0 <= y < self.height and 0 <= x < self.width:
            try:
                self.stdscr.addstr(y, x, text[: self.width - x - 1], attr)
            except curses.error:
                pass


# =============================
# Input Handler
# =============================
class InputHandler:
    """Processes key inputs and maps to game actions."""

    def __init__(self, view: ForgeView, audio: AudioEngine, state: GameState) -> None:
        self.view = view
        self.audio = audio
        self.state = state
        self.combo_stages = [
            ComboStage(10, LANG_TEXT['combo_stage_1']),
            ComboStage(30, LANG_TEXT['combo_stage_2']),
            ComboStage(60, LANG_TEXT['combo_stage_3']),
        ]

    def process_key(self, key: int) -> None:
        base_heat = random.uniform(2.0, 4.0)
        is_crit = False
        repr_key = chr(key) if 32 <= key <= 126 else ''
        if key in (curses.KEY_ENTER, 10, 13):
            self.state.vent()
            self.view.add_message(LANG_TEXT['breath_hint'])
            repr_key = "ENTER"
            return
        if key in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            self.state.block()
            self.view.add_message(LANG_TEXT['block_hint'])
            repr_key = "ARROW"
            return
        if key == ord(' '):
            if self.state.heavy_blow():
                base_heat = random.uniform(8.0, 12.0)
                repr_key = "HEAVY"
                is_crit = True
                self.audio.play_beep(440, 120)
            else:
                self.view.add_message(LANG_TEXT['heavy_wait'])
                return
        else:
            # chance for crit based on combo timing
            if time.time() - self.state.last_input_time < 0.25:
                is_crit = random.random() < 0.3
            else:
                is_crit = random.random() < 0.1
            if is_crit:
                self.audio.play_beep(880, 60)
        self.state.register_input(base_heat, is_crit, repr_key)
        if random.random() < 0.4:
            self.view.add_message(random.choice(BANter))


# =============================
# Breathing Animation
# =============================
class BreathingGuide:
    """Handles ASCII breathing prompts during cooldown."""

    def __init__(self, view: ForgeView, lang: str = "zh") -> None:
        self.view = view
        self.lang = lang

    def run(self, duration: float) -> None:
        start = time.time()
        phases = [("吸", 4), ("停", 7), ("呼", 8), ("停", 3)] if self.lang == "zh" else [
            ("Inhale", 4), ("Hold", 7), ("Exhale", 8), ("Hold", 3)
        ]
        box = ["+------+"]
        while time.time() - start < duration:
            elapsed = time.time() - start
            remain = duration - elapsed
            self.view.stdscr.erase()
            self.view.draw_header(GameState(), LANG_TEXT['phase_cool'], remain)
            phase_idx = int(elapsed) % len(phases)
            phase_name, phase_len = phases[phase_idx]
            frame = [
                "      []    ",
                "    [    ]  ",
                "    [    ]  ",
                "      []    ",
            ]
            scale = (elapsed % phase_len) / max(phase_len, 1)
            width = 4 + int(scale * 6)
            breath_box = ["+" + "-" * width + "+"]
            for _ in range(3):
                breath_box.append("|" + " " * width + "|")
            breath_box.append("+" + "-" * width + "+")
            info_lines = [LANG_TEXT['cool_msg'], LANG_TEXT['cool_msg_alt'], f"{phase_name} {phase_len - int(phase_len * scale)}"]
            self.view.draw_center_text(frame + box + breath_box + info_lines)
            self.view.draw_footer(LANG_TEXT['gentle_quote'])
            self.view.stdscr.refresh()
            time.sleep(0.2)
        self.view.add_message(LANG_TEXT['gentle_quote_alt'])


# =============================
# Game Controller
# =============================
class RageSmithGame:
    """Main game controller."""

    FORGE_DURATION = 90.0
    COOL_DURATION = 30.0

    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        self.audio = AudioEngine()
        self.state = GameState()
        self.view = ForgeView(stdscr, LANG)
        self.handler = InputHandler(self.view, self.audio, self.state)
        self.poet = PoemGenerator(LANG)
        self.breathing = BreathingGuide(self.view, LANG)
        self.key_counter = Counter()

    def start(self) -> None:
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)
        self._intro_screen()
        while True:
            self.state = GameState()
            self.handler.state = self.state
            self._forge_phase()
            self._cool_phase()
            poem, report = self._wrap_up()
            choice = self._post_round(poem, report)
            if choice == 'quit':
                break
            elif choice == 'save':
                self._save_run(poem, report)
            elif choice == 'restart':
                continue
        self._farewell()

    def _intro_screen(self) -> None:
        self.stdscr.erase()
        lines = [LANG_TEXT['title'], LANG_TEXT['press_any']]
        self.view.draw_center_text(lines)
        self.stdscr.refresh()
        self.stdscr.nodelay(False)
        self.stdscr.getch()
        self.stdscr.nodelay(True)

    def _forge_phase(self) -> None:
        start = time.time()
        last_tick = start
        banter_timer = 0.0
        while True:
            now = time.time()
            elapsed = now - start
            remaining = self.FORGE_DURATION - elapsed
            if remaining <= 0:
                break
            dt = now - last_tick
            last_tick = now
            key = self.stdscr.getch()
            if key != -1:
                self.handler.process_key(key)
                self._record_key(key)
            self.state.tick(dt)
            self._draw_forge(remaining)
            banter_timer += dt
            if banter_timer > 3.0:
                self.view.add_message(random.choice(BANter))
                banter_timer = 0.0
            time.sleep(0.01)
        self.state.stats.duration = self.FORGE_DURATION

    def _draw_forge(self, remaining: float) -> None:
        self.stdscr.erase()
        self.view.draw_header(self.state, LANG_TEXT['phase_forge'], remaining)
        self.view.draw_anvil(intensity=min(1.0, self.state.combo / 50.0))
        self.view.draw_stats(self.state)
        self.view.draw_meter(LANG_TEXT['anger'], self.state.anger % 200, 200, 13, 1)
        self.view.draw_meter(LANG_TEXT['heat'], self.state.heat, 100, 14, 2)
        pace = time.time() - self.state.last_input_time
        if pace > 1.2:
            tip = LANG_TEXT['tips_slow']
        elif pace < 0.2:
            tip = LANG_TEXT['tips_fast']
        else:
            tip = random.choice(BANter)
        self.view.draw_footer(tip)
        self.view.draw_messages()
        self.stdscr.refresh()

    def _cool_phase(self) -> None:
        self.stdscr.erase()
        self.breathing.run(self.COOL_DURATION)

    def _wrap_up(self) -> Tuple[List[str], List[str]]:
        freq = self._extract_common_words()
        top_words = [w for w, _ in freq[:3]]
        poem_lines = self.poet.generate_poem(self.state.stats, top_words[0] if top_words else '')
        report_lines = self.poet.build_report(self.state.stats, top_words)
        return poem_lines, report_lines

    def _post_round(self, poem: List[str], report: List[str]) -> str:
        selection = None
        while True:
            self.stdscr.erase()
            self.view.draw_header(self.state, LANG_TEXT['report_title'], 0)
            self.view.draw_center_text(report)
            offset = len(report) + 4
            for idx, line in enumerate(poem):
                self.view._write(offset + idx, self.view.width // 2 - 25, line)
            self.view.draw_footer(LANG_TEXT['save_prompt'])
            self.stdscr.refresh()
            ch = self.stdscr.getch()
            if ch in (ord('s'), ord('S')):
                selection = 'save'
                break
            elif ch in (ord('r'), ord('R')):
                selection = 'restart'
                break
            elif ch in (ord('q'), ord('Q')):
                selection = 'quit'
                break
        return selection or 'restart'

    def _save_run(self, poem: List[str], report: List[str]) -> None:
        folder = os.path.join(os.getcwd(), "ragesmith_runs")
        os.makedirs(folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f"run_{timestamp}.txt")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(LANG_TEXT['report_title'] + "\n")
                for line in report:
                    f.write(line + "\n")
                f.write("\n" + LANG_TEXT['poem_title'] + "\n")
                for line in poem:
                    f.write(line + "\n")
            self.view.add_message(f"{LANG_TEXT['saved']}: {path}")
        except Exception:
            self.view.add_message(LANG_TEXT['save_fail'])

    def _record_key(self, key: int) -> None:
        if key in (curses.KEY_ENTER, 10, 13):
            token = "ENTER"
        elif key == ord(' '):
            token = "HEAVY"
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            token = "ARROW"
        elif 32 <= key <= 126:
            token = chr(key)
        else:
            token = f"<{key}>"
        self.key_counter[token] += 1

    def _extract_common_words(self) -> List[Tuple[str, int]]:
        # simplistic: use tokens or characters
        counter = Counter()
        for token, count in self.key_counter.items():
            if token in ("ENTER", "HEAVY", "ARROW"):
                continue
            if len(token) == 1:
                counter[token] += count
            else:
                counter.update({token: count})
        if not counter:
            return []
        return counter.most_common(3)

    def _farewell(self) -> None:
        self.stdscr.erase()
        self.view.draw_center_text([LANG_TEXT['farewell']])
        self.stdscr.refresh()
        time.sleep(1.5)


# =============================
# Text Fallback (non-curses)
# =============================
def fallback_mode() -> None:
    print(LANG_TEXT['init_fail'])
    start = time.time()
    anger = 0.0
    combo = 0
    print(LANG_TEXT['press_any'])
    try:
        while time.time() - start < RageSmithGame.FORGE_DURATION:
            inp = input("🔥>")
            anger += len(inp) * random.uniform(1.0, 2.0)
            combo = max(combo, len(inp))
        print(LANG_TEXT['gentle_quote'])
    except KeyboardInterrupt:
        pass


# =============================
# Entrypoint with curses setup
# =============================

def main(stdscr: "curses._CursesWindow") -> None:
    game = RageSmithGame(stdscr)
    game.start()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error:
        print(LANG_TEXT['no_curses'])
        fallback_mode()
    except KeyboardInterrupt:
        pass

# =============================
# 快速故障排查 / Quick Troubleshooting
# - 若终端不支持 curses，程序会自动切换到简易文本模式。
# - Windows 建议使用 `py ragesmith.py` 启动以获得更好兼容性。
# - 声音模块不可用时自动静默，不影响游戏流程。
# - 若终端宽度过小，可放大窗口以获得完整 ASCII 动画。
# =============================

# 自测清单 Self-check
# - 启动后 2 秒内完成 UI 初始化。
# - 90 秒内任意键敲击均有数值增益。
# - 连击能在 1 秒无输入后逐步衰减。
# - 空格触发重锤并进入 3 秒冷却。
# - 冷却阶段显示呼吸动画且不再计分。
# - 结束后按 S 成功写入 .txt 战报。
# - 无外网依赖；声音模块不可用时不崩溃。
# - 代码行内含关键注释与 README 风格顶部说明。
