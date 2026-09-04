#!/usr/bin/env python3
"""
Claude Code status line.
Shows: model, context usage, session cost, duration, today/30d overall costs.

Setup — add to ~/.claude/settings.json:
  {
    "statusLine": {
      "type": "command",
      "command": "uv run ~/.claude/claude-statusline-tracker.py"
    }
  }

Refactored for Extreme Performance:
- Implements Stale-While-Revalidate background caching (O(1) prompt rendering)
- Fast-path string filtering avoids unnecessary JSON parsing
- Time-based file pruning via os.stat ignores logs older than 30 days
- String-slicing timestamp extraction replaces heavy datetime parsing
- Memoized regex pattern matching
- Lazy imports to optimize Python startup duration

Today and 30d costs are overall totals across all projects.
"""

import json
import logging
import logging.handlers
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# ── Logging Setup ──────────────────────────────────────────────────────────
LOG_DIR = Path.home() / ".claude" / "logs"
LOG_FILE = LOG_DIR / "statusline.log"


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("claude_statusline")
    logger.setLevel(logging.ERROR)

    # Rotating handler: 1MB per file, keep 3 backups
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


setup_logging()

logger = logging.getLogger("claude_statusline")

# ── Early Exit for Background Worker ───────────────────────────────────────
# Subprocess flag to recalculate cache silently without blocking the UI
BACKGROUND_UPDATE = "--update-cache" in sys.argv

CACHE_MAX_AGE = 3600  # 1 hour
CACHE_FILE = Path.home() / ".claude" / "cost_cache.json"

# ── Pricing (per 1M tokens) ───────────────────────────────────────────────
# Source: Anthropic API pricing (https://www.anthropic.com/pricing)
# For Bedrock pricing in us-west-2, verify at: https://aws.amazon.com/bedrock/pricing/
# Note: Bedrock pricing typically aligns with API pricing but may vary by region
# fmt: off
PRICING = {
    "claude-fable-5-1":     {"input": 10.00, "output": 50.00, "cache_read": 1.00,  "cache_write": 12.50},
    "claude-fable-5":       {"input": 10.00, "output": 50.00, "cache_read": 1.00,  "cache_write": 12.50},
    "claude-opus-5":        {"input": 5.00,  "output": 25.00, "cache_read": 0.50,  "cache_write": 6.25},
    "claude-sonnet-5":      {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
    "claude-opus-4-8":      {"input": 5.00,  "output": 25.00, "cache_read": 0.50,  "cache_write": 6.25},
    "claude-opus-4-7":      {"input": 5.00,  "output": 25.00, "cache_read": 0.50,  "cache_write": 6.25},
    "claude-opus-4-6":      {"input": 5.00,  "output": 25.00, "cache_read": 0.50,  "cache_write": 6.25},
    "claude-sonnet-4-6":    {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
    "claude-opus-4-5":      {"input": 5.00,  "output": 25.00, "cache_read": 0.50,  "cache_write": 6.25},
    "claude-sonnet-4-5":    {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
    "claude-haiku-4-5":     {"input": 1.00,  "output": 5.00,  "cache_read": 0.10,  "cache_write": 1.25},
    "claude-opus-4-1":      {"input": 15.00, "output": 75.00, "cache_read": 1.50,  "cache_write": 18.75},
    "claude-opus-4":        {"input": 15.00, "output": 75.00, "cache_read": 1.50,  "cache_write": 18.75},
    "claude-sonnet-4":      {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
    "claude-3-7-sonnet":    {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
    "claude-3-5-sonnet":    {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
    "claude-3-5-haiku":     {"input": 0.25,  "output": 1.25,  "cache_read": 0.025, "cache_write": 0.30},
    "claude-3-haiku":       {"input": 0.25,  "output": 1.25,  "cache_read": 0.025, "cache_write": 0.30},
    "claude-opus-3":        {"input": 15.00, "output": 75.00, "cache_read": 1.50,  "cache_write": 18.75},
}
# fmt: on
DEFAULT_PRICING = {
    "input": 3.00,
    "output": 15.00,
    "cache_read": 0.30,
    "cache_write": 3.75,
}

# fmt: off
_MODEL_PATTERNS = [
    (r"fable.?5.?1",                 "claude-fable-5-1"),
    (r"fable.?5",                    "claude-fable-5"),
    (r"opus.?5",                     "claude-opus-5"),
    (r"sonnet.?5",                   "claude-sonnet-5"),
    (r"opus.?4.?8",                  "claude-opus-4-8"),
    (r"opus.?4.?7",                  "claude-opus-4-7"),
    (r"opus.?4.?6",                  "claude-opus-4-6"),
    (r"sonnet.?4.?6",                "claude-sonnet-4-6"),
    (r"opus.?4.?5",                  "claude-opus-4-5"),
    (r"sonnet.?4.?5",                "claude-sonnet-4-5"),
    (r"haiku.?4.?5",                 "claude-haiku-4-5"),
    (r"opus.?4.?1",                  "claude-opus-4-1"),
    (r"opus.?4(?![.\d])",            "claude-opus-4"),
    (r"sonnet.?4(?![.\d])",          "claude-sonnet-4"),
    (r"opus.?3",                     "claude-opus-3"),
    (r"3.?7.?sonnet|sonnet.?3.?7",   "claude-3-7-sonnet"),
    (r"3.?5.?sonnet|sonnet.?3.?5",   "claude-3-5-sonnet"),
    (r"3.?5.?haiku|haiku.?3.?5",     "claude-3-5-haiku"),
    (r"haiku",                       "claude-3-haiku"),
]
# fmt: on

_MODEL_PATTERNS_COMPILED = [
    (re.compile(p, re.IGNORECASE), k) for p, k in _MODEL_PATTERNS
]
_MODEL_KEY_CACHE = {}


# ── Helpers ────────────────────────────────────────────────────────────────


def _get_model_key(name: str) -> str | None:
    """Map model display name to pricing key, highly memoized."""
    if not name or name.startswith("<"):
        return None
    if name in _MODEL_KEY_CACHE:
        return _MODEL_KEY_CACHE[name]
    for pattern, key in _MODEL_PATTERNS_COMPILED:
        if pattern.search(name):
            _MODEL_KEY_CACHE[name] = key
            return key
    _MODEL_KEY_CACHE[name] = "unknown"
    return "unknown"


def _calc_cost(model_key: str, inp: int, out: int, cr: int, cw: int) -> float:
    p = PRICING.get(model_key, DEFAULT_PRICING)
    return (
        (inp * p["input"])
        + (out * p["output"])
        + (cr * p["cache_read"])
        + (cw * p["cache_write"])
    ) / 1_000_000


def _fmt_duration(ms: int) -> str:
    total_sec = ms // 1000
    d, rem = divmod(total_sec, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if d > 0:
        return f"{d}d {h}h {m:02d}m"
    if h > 0:
        return f"{h}h {m:02d}m"
    if m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def _get_cache_write_tokens(u: dict[str, Any]) -> int:
    """Extract cache write tokens from usage dictionary."""

    total_cw = u.get("cache_creation_input_tokens", 0)
    cache_creation = u.get("cache_creation", {})

    if isinstance(cache_creation, dict):
        cw_5m = cache_creation.get("ephemeral_5m_input_tokens", 0)
        cw_1h = cache_creation.get("ephemeral_1h_input_tokens", 0)

        if cw_5m or cw_1h:
            total_cw = cw_5m + cw_1h

    return total_cw


# ── Cost calculation with caching ──────────────────────────────────────────


def _compute_costs() -> dict[str, float]:
    """Compute costs traversing local files with heavy optimization."""
    # Lazy import datetime to avoid startup overhead on cache hits
    from datetime import datetime, timedelta, timezone

    claude_dir = Path.home() / ".claude" / "projects"
    if not claude_dir.exists():
        return {"total_30d": 0.0, "today": 0.0}

    now = datetime.now(timezone.utc)
    cutoff_date_str = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    today_date_str = now.strftime("%Y-%m-%d")

    # OS level prune threshold
    cutoff_ts = time.time() - (30 * 86400)

    total = 0.0
    today_cost = 0.0

    for root, _, files in os.walk(str(claude_dir)):
        for file in files:
            if not file.endswith(".jsonl"):
                continue

            filepath = os.path.join(root, file)
            try:
                # OPTIMIZATION: Discard old files instantly without opening them
                if os.stat(filepath).st_mtime < cutoff_ts:
                    continue

                seen: dict[str, dict[str, Any]] = {}
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        # OPTIMIZATION: High-speed pre-filter dodges JSON loads overhead
                        if '"assistant"' not in line:
                            continue

                        try:
                            data = json.loads(line)
                            if data.get("type") != "assistant":
                                continue

                            msg = data.get("message", {})
                            u = msg.get("usage")
                            ts = data.get("timestamp")
                            if not u or not ts:
                                continue

                            # OPTIMIZATION: Zero-allocation date parsing
                            date_str = ts[:10]
                            if date_str < cutoff_date_str:
                                continue

                            mk = _get_model_key(msg.get("model", ""))
                            if not mk or mk == "unknown":
                                continue

                            message_id = msg.get("id", data.get("uuid", ""))
                            seen[message_id] = {
                                "date": date_str,
                                "mk": mk,
                                "inp": u.get("input_tokens", 0),
                                "out": u.get("output_tokens", 0),
                                "cr": u.get("cache_read_input_tokens", 0),
                                "cw": _get_cache_write_tokens(u),
                            }
                        except (
                            json.JSONDecodeError,
                            ValueError,
                            AttributeError,
                            TypeError,
                        ) as e:
                            logger.debug(f"Skipping line due to error: {e}")
                            continue
            except OSError as e:
                logger.error(f"Error accessing file {filepath}: {e}")
                continue
            except Exception:
                logger.exception("Unexpected error during file processing")
                continue

        for e in seen.values():
            c = _calc_cost(e["mk"], e["inp"], e["out"], e["cr"], e["cw"])
            total += c
            if e["date"] == today_date_str:
                today_cost += c

    return {"total_30d": round(total, 2), "today": round(today_cost, 2)}


def update_cache_file() -> None:
    costs = _compute_costs()
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(costs, f)
    except OSError as e:
        logger.error(f"Failed to update cost cache file: {e}")


# Early exit trap for the detached background worker
if BACKGROUND_UPDATE:
    update_cache_file()
    sys.exit(0)


def get_cached_costs() -> dict[str, float]:
    """Returns cost data. Uses Stale-While-Revalidate pattern."""
    try:
        if CACHE_FILE.exists():
            age = time.time() - os.path.getmtime(CACHE_FILE)
            if age < CACHE_MAX_AGE:
                with open(CACHE_FILE, encoding="utf-8") as f:
                    return json.load(f)
            else:
                # OPTIMIZATION: Cache is stale. We immediately return the stale content
                # to render the prompt fast, while rebuilding in a detached process.
                import subprocess

                # Cross-platform detached background process
                kwargs: dict[str, Any] = (
                    {"creationflags": 0x00000008}
                    if os.name == "nt"
                    else {"start_new_session": True}
                )
                subprocess.Popen(
                    [sys.executable, os.path.abspath(__file__), "--update-cache"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    **kwargs,
                )

                with open(CACHE_FILE, encoding="utf-8") as f:
                    return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Error reading cached costs: {e}")

    # Blocking fail-safe if cache completely missing
    update_cache_file()
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Fail-safe cache read failed: {e}")
        return {"total_30d": 0.0, "today": 0.0}


# ── UI Execution ───────────────────────────────────────────────────────────

claude_ctx = {}
try:
    raw = sys.stdin.read()
    if raw.strip():
        claude_ctx = json.loads(raw)
except (json.JSONDecodeError, OSError) as e:
    logger.debug(f"Failed to parse input context: {e}")


model = ""
ctx_pct = ctx_rem = 0
cost_usd = 0.0
dur_ms = 0

try:
    model = claude_ctx.get("model", {}).get("display_name", "")
    cw = claude_ctx.get("context_window", {})
    ctx_pct = cw.get("used_percentage", 0)
    ctx_rem = cw.get("remaining_percentage", 0)
    c = claude_ctx.get("cost", {})
    cost_usd = c.get("total_cost_usd", 0.0)
    dur_ms = c.get("total_duration_ms", 0)
except (AttributeError, TypeError) as e:
    logger.debug(f"Error parsing context values: {e}")


costs = get_cached_costs()

ORANGE = "\033[38;2;222;115;86m"
BOLD = "\033[1m"
LABEL = "\033[38;2;170;170;170m"
DIM = "\033[38;2;110;110;110m"
RED = "\033[31m"
RESET = "\033[0m"

SEP = f"  {DIM}·{RESET}  "

cost_30d = costs.get("total_30d", 0)
if cost_30d >= 300:
    cost_30d_str = f"{RED}${cost_30d:.2f}{RESET}"
elif cost_30d >= 150:
    cost_30d_str = f"{ORANGE}${cost_30d:.2f}{RESET}"
else:
    cost_30d_str = f"${cost_30d:.2f}"

if model:
    ctx_filled = round(ctx_pct / 10)
    ctx_bar = "█" * ctx_filled + "░" * (10 - ctx_filled)
    ctx_color = RED if ctx_pct >= 80 else ORANGE
    duration_str = _fmt_duration(dur_ms)

    print(
        f"{ORANGE}{BOLD}✦ {model}{RESET}"
        f"{SEP}{LABEL}context{RESET} {ctx_color}{ctx_pct}%{RESET} {DIM}[{RESET}{ctx_bar}{DIM}]{RESET}"
        f"{SEP}{LABEL}session{RESET} ${cost_usd:.2f} {DIM}{duration_str}{RESET}"
        f"{SEP}{LABEL}today{RESET} ${costs.get('today', 0):.2f}"
        f"{SEP}{LABEL}30 days{RESET} {cost_30d_str}"
    )
else:
    print(
        f"{ORANGE}{BOLD}✦ Claude{RESET}"
        f"{SEP}{LABEL}today{RESET} ${costs.get('today', 0):.2f}"
        f"{SEP}{LABEL}30 days{RESET} {cost_30d_str}"
    )
