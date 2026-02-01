"""Utility functions for the AI Workforce backend."""

# Prices per 1M tokens (USD)
MODEL_PRICING = {
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}
DEFAULT_MODEL = "gpt-4.1"


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = DEFAULT_MODEL
) -> dict:
    """Estimate USD cost for token usage.

    Returns:
        {"model": str, "total_estimated_usd_cost": float | None}
    """
    try:
        pricing = MODEL_PRICING.get(model, MODEL_PRICING[DEFAULT_MODEL])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return {
            "model": model if model in MODEL_PRICING else DEFAULT_MODEL,
            "total_estimated_usd_cost": round(input_cost + output_cost, 6),
        }
    except Exception:
        return {
            "model": model,
            "total_estimated_usd_cost": None,
        }
