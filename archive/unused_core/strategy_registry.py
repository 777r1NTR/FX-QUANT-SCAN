# core/strategy_registry.py

# === Global strategy registry ===
STRATEGY_REGISTRY = {}

def register_strategy(func):
    """
    Decorator to register a strategy function with a global strategy registry.
    Each strategy must accept a DataFrame and return a list of trade dicts.
    """
    STRATEGY_REGISTRY[func.__name__] = func
    return func
