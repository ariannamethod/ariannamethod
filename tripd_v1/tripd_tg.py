# -*- coding: utf-8 -*-
"""Telegram interface for the TRIPD model."""

from __future__ import annotations

from pathlib import Path
import argparse
import os
import logging
import html
from typing import List, Optional, Tuple

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    BotCommand,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

try:  # pragma: no cover - support package and script execution
    from .tripd import TripDModel, start_verb_stream, build_letter
except ImportError:  # pragma: no cover - fallback for running as scripts
    from tripd import TripDModel, start_verb_stream, build_letter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rendering configuration
TRIPD_RENDER = os.environ.get("TRIPD_RENDER", "markdown").lower()

def _render_script(script: str) -> Tuple[str, Optional[str]]:
    """Render TRIPD script according to TRIPD_RENDER setting."""
    if TRIPD_RENDER == "html":
        escaped_script = html.escape(script)
        return f"<pre><code>{escaped_script}</code></pre>", "HTML"
    else:
        # Markdown: use code fence, escape backticks to avoid fence breakage
        safe_script = script.replace("```", "'''").replace("`", "'")
        return f"```TRIPD\n{safe_script}\n```", "Markdown"

def _render_letter(letter_text: str) -> Tuple[str, Optional[str]]:
    """Render TRIPD letter with minimal processing to preserve formatting and special characters."""
    if TRIPD_RENDER == "html":
        # HTML mode: escape entities but DO NOT wrap with <pre><code>
        return html.escape(letter_text), "HTML"
    else:
        # Markdown mode: send as plain text (no parse_mode) to preserve typography
        return letter_text, None

# ---------------------------------------------------------------------------
# Model and dictionary setup
_model = TripDModel()
_sections: List[str] = sorted(_model.sections)

# Preload README and split into logical sections
_README = Path(__file__).resolve().parent / "README.md"
_text = _README.read_text(encoding="utf-8")

# Split by major sections for better parsing
sections = _text.split("## ")
_readme_parts: List[str] = []
current_part = ""
chars_per_part = 3500  # Telegram message limit consideration

for i, section in enumerate(sections):
    if i == 0:  # First part before any ##
        current_part = section
    else:
        section_text = "## " + section
        if len(current_part + section_text) > chars_per_part and current_part:
            _readme_parts.append(current_part.strip())
            current_part = section_text
        else:
            current_part += "\n\n" + section_text
if current_part:
    _readme_parts.append(current_part.strip())

while len(_readme_parts) < 3:
    if _readme_parts:
        longest_idx = max(range(len(_readme_parts)), key=lambda i: len(_readme_parts[i]))
        longest = _readme_parts[longest_idx]
        mid = len(longest) // 2
        _readme_parts[longest_idx] = longest[:mid]
        _readme_parts.insert(longest_idx + 1, longest[mid:])
    else:
        _readme_parts = [
            _text[: len(_text) // 3],
            _text[len(_text) // 3 : 2 * len(_text) // 3],
            _text[2 * len(_text) // 3 :],
        ]

# Load policy files if present
_ACCEPTABLE_USE = Path(__file__).resolve().parent / "ACCEPTABLE_USE.md"
_TRADEMARK_POLICY = Path(__file__).resolve().parent / "TRADEMARK_POLICY.md"
_policy_parts: List[str] = []
_policy_parts.append(_ACCEPTABLE_USE.read_text(encoding="utf-8") if _ACCEPTABLE_USE.exists() else "")
_policy_parts.append(_TRADEMARK_POLICY.read_text(encoding="utf-8") if _TRADEMARK_POLICY.exists() else "")

# ---------------------------------------------------------------------------
# Menu helpers

def _menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(name, callback_data=f"section:{name}")]
               for name in _sections]
    buttons.append([InlineKeyboardButton("TRIPD Documentation", callback_data="theory:0")])
    buttons.append([InlineKeyboardButton("TRIPD Policy", callback_data="policy:0")])
    return InlineKeyboardMarkup(buttons)


async def _show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "True Recursive Intelligent Python Dialect"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            message, reply_markup=_menu_keyboard()
        )
    else:
        assert update.message
        await update.message.reply_text(
            message, reply_markup=_menu_keyboard()
        )
    logger.info("Menu displayed")


# ---------------------------------------------------------------------------
# Section handling
async def _send_section(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    assert query
    await query.answer()
    section = query.data.split(":", 1)[1]
    logger.info("Section requested: %s", section)
    script = _model.generate_from_section(section)

    nav_buttons = [
        InlineKeyboardButton("⬅️ Menu", callback_data="menu"),
        InlineKeyboardButton("↻ Regenerate", callback_data=f"section:{section}")
    ]
    keyboard = InlineKeyboardMarkup([nav_buttons])

    rendered_script, parse_mode = _render_script(script)
    await query.message.reply_text(
        rendered_script,
        parse_mode=parse_mode,
        reply_markup=keyboard
    )


# ---------------------------------------------------------------------------
# Theory navigation
async def _send_theory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    assert query
    await query.answer()
    index = int(query.data.split(":", 1)[1])
    logger.info("Theory section %d requested", index)

    if index >= len(_readme_parts):
        index = 0

    text = _readme_parts[index]
    max_index = len(_readme_parts) - 1

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"theory:{index - 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"theory:{max_index}"))

    nav_buttons.append(InlineKeyboardButton("📚", callback_data="menu"))

    if index < max_index:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"theory:{index + 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data="theory:0"))

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup([nav_buttons])
    )


# ---------------------------------------------------------------------------
# Policy navigation
async def _send_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    assert query
    await query.answer()
    index = int(query.data.split(":", 1)[1])
    logger.info("Policy section %d requested", index)

    if index >= len(_policy_parts):
        index = 0

    text = _policy_parts[index]
    max_index = len(_policy_parts) - 1

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"policy:{index - 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"policy:{max_index}"))

    nav_buttons.append(InlineKeyboardButton("📚", callback_data="menu"))

    if index < max_index:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"policy:{index + 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data="policy:0"))

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup([nav_buttons])
    )


# ---------------------------------------------------------------------------
# Letter flow (via /letters command)
async def _letter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message
    await update.message.reply_text("What's your AI's name? (optional)")
    context.user_data["letter_wait_name"] = True


# ---------------------------------------------------------------------------
# Message handling delegated to the TRIPD model
async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message
    text = update.message.text or ""
    logger.info("Received message: %s", text)

    if context.user_data.get("letter_wait_name"):
        name = text.strip() if text.strip() else None
        context.user_data["letter_wait_name"] = False
        context.user_data["letter_name"] = name
        letter_text = build_letter(ai_name=name)
        rendered_letter, parse_mode = _render_letter(letter_text)
        await update.message.reply_text(rendered_letter, parse_mode=parse_mode)
        return

    script, metrics_text = _model.generate_response(text)
    rendered_script, parse_mode = _render_script(script)
    await update.message.reply_text(
        rendered_script, parse_mode=parse_mode
    )
    await update.message.reply_text(metrics_text)


# ---------------------------------------------------------------------------
async def _post_init(app: Application) -> None:
    await app.bot.set_my_commands([
        BotCommand("tripd", "Meet TRIPD 👉"),
        BotCommand("letters", "GET A LETTER 👉"),
    ])

def main() -> None:
    parser = argparse.ArgumentParser(description="Run TRIPD Telegram bot")
    parser.add_argument(
        "--verb-stream",
        metavar="ADDR",
        help="Enable live verb streaming via TCP port or UNIX socket path",
    )
    parser.add_argument(
        "--token",
        help=(
            "Telegram bot token. Overrides TELEGRAM_TOKEN environment "
            "variable if provided."
        ),
    )
    args = parser.parse_args()

    if args.verb_stream:
        addr = args.verb_stream
        if addr.isdigit():
            start_verb_stream(_model, port=int(addr))
        else:
            start_verb_stream(_model, unix_socket=addr)

    token = args.token or os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError(
            "Telegram token required via --token or TELEGRAM_TOKEN environment variable"
        )
    application = (
        Application.builder()
        .token(token)
        .post_init(_post_init)
        .build()
    )

    application.add_handler(CommandHandler("tripd", _show_menu))
    application.add_handler(CommandHandler("start", _show_menu))
    application.add_handler(CommandHandler("letters", _letter_command))
    application.add_handler(CommandHandler("letter", _letter_command))
    application.add_handler(CallbackQueryHandler(_show_menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(_send_section, pattern="^section:"))
    application.add_handler(CallbackQueryHandler(_send_theory, pattern="^theory:"))
    application.add_handler(CallbackQueryHandler(_send_policy, pattern="^policy:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_message))

    logger.info("Starting Telegram polling")
    application.run_polling()


__all__ = ["main"]


if __name__ == "__main__":
    main()
