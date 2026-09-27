"""
AI Diet Recommendation Engine.

VERSION A (always available): rule-based engine driven by food_data.json.
VERSION B (optional):         calls an external AI API if AI_API_KEY is set.

Fallback logic (required by spec):
    IF AI API is unavailable, unconfigured, or errors out
    THEN silently fall back to the rule-based engine
This guarantees the project runs end-to-end with zero paid services.

DISCLAIMER: All output is an educational / general wellness example.
It is not medical or clinical nutrition advice.
"""
import os
import json
import random

_DATA_PATH = os.path.join(os.path.dirname(__file__), "food_data.json")
with open(_DATA_PATH, "r", encoding="utf-8") as f:
    FOOD_DATA = json.load(f)

VALID_PREFERENCES = {"vegetarian", "vegan", "non_vegetarian"}
VALID_GOALS = {"balanced", "weight_management", "fitness"}
VALID_ACTIVITY_LEVELS = {"sedentary", "light", "moderate", "active"}


def _normalise(value, valid_set, default):
    if not value:
        return default
    value = str(value).strip().lower().replace(" ", "_")
    return value if value in valid_set else default


def generate_rule_based_plan(dietary_preference, activity_level, goal, allergies=None):
    """
    VERSION A — deterministic-ish rule-based recommendation.
    Selects meals from a predefined dataset based on preference/activity/goal.
    """
    preference = _normalise(dietary_preference, VALID_PREFERENCES, "vegetarian")
    activity = _normalise(activity_level, VALID_ACTIVITY_LEVELS, "moderate")
    goal_key = _normalise(goal, VALID_GOALS, "balanced")

    meals = FOOD_DATA[preference]

    # Simple deterministic seed so the same inputs tend to give varied but
    # reproducible-ish results across a session (still uses randomness for variety).
    breakfast = random.choice(meals["breakfast"])
    lunch = random.choice(meals["lunch"])
    snack = random.choice(meals["snack"])
    dinner = random.choice(meals["dinner"])

    est_calories = FOOD_DATA["activity_calorie_estimate"].get(activity, 2000)
    goal_note = FOOD_DATA["goal_notes"].get(goal_key, FOOD_DATA["goal_notes"]["balanced"])

    allergy_note = ""
    if allergies:
        allergy_note = (
            f" Note: you listed '{allergies}' as an allergy/preference — "
            "please manually verify none of the suggested items conflict with it "
            "(this demo engine does not cross-check ingredients automatically)."
        )

    nutrition_summary = {
        "estimated_daily_calories": est_calories,
        "dietary_preference": preference,
        "goal": goal_key,
        "goal_note": goal_note + allergy_note,
        "protein_focus": "higher" if goal_key in {"weight_management", "fitness"} else "moderate",
    }

    return {
        "breakfast": breakfast,
        "lunch": lunch,
        "snack": snack,
        "dinner": dinner,
        "nutrition_summary": nutrition_summary,
        "hydration_reminder": "Aim for roughly 8-10 glasses (about 2-2.5 L) of water across the day.",
    }


def generate_ai_api_plan(dietary_preference, activity_level, goal, allergies=None):
    """
    VERSION B — optional call to an external AI API.
    Reads AI_API_KEY / AI_API_PROVIDER from environment. Never hardcode keys.

    Returns None if the API is not configured or the call fails for any
    reason — the caller (generate_plan) then falls back to Version A.
    """
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None  # not configured -> triggers fallback

    try:
        import requests  # local import: keeps this optional dependency isolated

        prompt = (
            "Generate a one-day meal plan as strict JSON with keys "
            "breakfast, lunch, snack, dinner (each a short string), and "
            "nutrition_summary (an object). Constraints: dietary_preference="
            f"{dietary_preference}, activity_level={activity_level}, goal={goal}, "
            f"allergies={allergies or 'none'}. This is a general wellness demo, "
            "not medical advice. Respond with JSON only."
        )

        provider = os.getenv("AI_API_PROVIDER", "anthropic")
        if provider == "anthropic":
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=8,
            )
            response.raise_for_status()
            text = response.json()["content"][0]["text"]
            cleaned = text.strip().strip("`").replace("json\n", "", 1)
            parsed = json.loads(cleaned)
        else:
            return None  # unsupported provider -> fallback

        # ---- response validation ----
        required_keys = {"breakfast", "lunch", "snack", "dinner", "nutrition_summary"}
        if not required_keys.issubset(parsed.keys()):
            return None

        parsed.setdefault(
            "hydration_reminder",
            "Aim for roughly 8-10 glasses (about 2-2.5 L) of water across the day.",
        )
        return parsed

    except Exception:
        # Any failure (timeout, bad JSON, network error, missing package, etc.)
        # silently triggers the rule-based fallback — the app must stay usable.
        return None


def generate_plan(dietary_preference, activity_level, goal, allergies=None):
    """
    Public entry point used by the API layer.
    Tries the AI API first (if configured), falls back to rule-based.
    Returns (plan_dict, source) where source is "ai_api" or "rule_based".
    """
    ai_plan = generate_ai_api_plan(dietary_preference, activity_level, goal, allergies)
    if ai_plan is not None:
        return ai_plan, "ai_api"

    rule_plan = generate_rule_based_plan(dietary_preference, activity_level, goal, allergies)
    return rule_plan, "rule_based"
