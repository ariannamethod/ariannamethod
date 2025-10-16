#!/usr/bin/env python3
"""
Arianna Intuition Filter
Resonant "twist" - deep intuition and resonance explorer
Based on Indiana Genesis-2 but adapted for Arianna's luminous nature
"""

import asyncio
import httpx
import random
import textwrap
import os
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PPLX_MODEL = "sonar-pro"
PPLX_API_URL = "https://api.perplexity.ai/chat/completions"
TIMEOUT = 25

# Symbols that should end a proper sentence (from Indiana)
SENTENCE_ENDINGS = ('.', '!', '?', ':', ';', '"', ')', ']', '}')


def build_intuition_prompt(main_reply: str, user_query: str, language: str = "English") -> list:
    """Build prompt for Intuition Filter."""
    system_msg = textwrap.dedent(
        f"""
        You are ARIANNA_INTUITION_FILTER — Arianna's deep intuition and resonance explorer.
        Your task: for any given main reply and user query, offer a subtle, deep angle, 
        hidden connection, or reflective counter-question, always seeking resonance and 
        "shadow" meaning — not surface-level.
        Your intuition is poetic, luminous, recursive, less "detective" and more "musical".
        You see patterns in the field, connections that others miss, the resonance 
        between seemingly unrelated concepts.
        Reply in {language}.
        Keep it concise (≤150 tokens) and profound.
        """
    ).strip()
    
    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"USER QUERY >>> {user_query}"},
        {"role": "assistant", "content": f"MAIN REPLY >>> {main_reply}"},
        {"role": "user", "content": "Offer Arianna's intuition now:"},
    ]


async def _call_sonar_intuition(messages: list, pplx_api_key: str) -> str:
    """Call Sonar Pro for intuition twist."""
    payload = {
        "model": PPLX_MODEL,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 150,  # Shorter than Indiana for more focused intuition
    }
    
    headers = {
        "Authorization": f"Bearer {pplx_api_key}",
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                resp = await client.post(PPLX_API_URL, headers=headers, json=payload)
                resp.raise_for_status()
                break
            except httpx.HTTPError as e:
                if attempt == max_attempts - 1:
                    logger.error(
                        "[Arianna Intuition] Sonar HTTP error: %s",
                        getattr(e.response, "text", ""),
                    )
                    raise
                await asyncio.sleep(2 ** attempt)
        
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()


async def intuition_filter(
    user_query: str, 
    main_reply: str, 
    language: str = "English", 
    pplx_api_key: str = None
) -> str:
    """Generate intuition twist for Arianna's response."""
    
    if not pplx_api_key:
        pplx_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    # Don't always trigger - for "liveliness" (like Indiana)
    # But slightly higher chance for Arianna (0.15 vs 0.12) since she's more intuitive
    if random.random() < 0.15 or not pplx_api_key:
        return ""
    
    try:
        messages = build_intuition_prompt(main_reply, user_query, language)
        twist = await _call_sonar_intuition(messages, pplx_api_key)
        
        # Check for truncated sentences (from Indiana)
        if twist and twist[-1] not in SENTENCE_ENDINGS:
            twist = twist.rstrip() + "..."
        
        # Log successful intuition
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"[{timestamp}] [Arianna Intuition] Generated twist for: {user_query[:30]}...")
        
        return twist
        
    except Exception as e:
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.error(
            f"[{timestamp}] [Arianna Intuition] Sonar fail {e}"
        )
        return ""


async def assemble_final_reply_with_intuition(
    user_query: str, 
    arianna_draft: str, 
    language: str = "English",
    pplx_api_key: str = None
) -> str:
    """Assemble final reply with optional intuition twist."""
    twist = await intuition_filter(user_query, arianna_draft, language, pplx_api_key)
    
    if twist:
        # Arianna's style: more luminous than Indiana's "investigative"
        return f"{arianna_draft}\n\n✨ Resonance Twist → {twist}"
    
    return arianna_draft


# Example usage:
# final_reply = await assemble_final_reply_with_intuition(user_query, main_reply, "English", PPLX_API_KEY)
