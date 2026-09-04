from pathlib import Path


# =========================================================
# PROJECT SETTINGS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR = PROJECT_ROOT / "reports"

SOURCE_BRIEFING = (
    REPORTS_DIR
    / "management_briefing.txt"
)

OUTPUT_FILE = (
    REPORTS_DIR
    / "verified_ai_prompt.txt"
)


# =========================================================
# VERIFY SOURCE BRIEFING
# =========================================================

if not SOURCE_BRIEFING.exists():

    raise FileNotFoundError(
        "management_briefing.txt was not found. "
        "Run generate_briefing.py first."
    )


verified_briefing = SOURCE_BRIEFING.read_text(
    encoding="utf-8"
)


# =========================================================
# AI INSTRUCTIONS
# =========================================================

ai_instructions = """
You are an executive reporting assistant.

Rewrite the verified management briefing below into concise,
professional, management-ready language.

STRICT RULES

1. Use only facts contained in the verified briefing.
2. Do not calculate new KPI values.
3. Do not change any number, percentage, team name,
   ticket count, or factual statement.
4. Do not invent causes that are not supported by the data.
5. Clearly separate observed facts from recommendations.
6. Keep recommendations directly tied to the evidence.
7. If the data does not establish why something happened,
   do not claim a cause.
8. Keep the output concise and suitable for management review.

Use this structure:

EXECUTIVE SUMMARY

KEY FINDINGS

PRIORITY RISKS

RECOMMENDED ACTIONS

DATA RELIABILITY NOTE
""".strip()


# =========================================================
# BUILD GROUNDED AI PROMPT
# =========================================================

prompt = f"""
{ai_instructions}


============================================================
VERIFIED SOURCE DATA
============================================================

{verified_briefing}


============================================================
END OF VERIFIED SOURCE DATA
============================================================

Rewrite the briefing according to the rules above.
Do not introduce facts that are not present in the verified source.
""".strip()


# =========================================================
# SAVE PROMPT
# =========================================================

OUTPUT_FILE.write_text(
    prompt,
    encoding="utf-8"
)


print()
print(
    "Verified AI prompt created successfully."
)

print(
    f"Saved to: {OUTPUT_FILE}"
)

print()
print(
    "You can paste this prompt into ChatGPT "
    "or another AI assistant for an optional "
    "human-reviewed executive rewrite."
)