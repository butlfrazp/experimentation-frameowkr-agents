import math
from collections.abc import Iterable
from typing import Any


class EquivalentEvaluator:
    """Evaluator that scores loose equivalence between response & ground truth.

    Returns a dictionary with:
      score: float in [0,1]
      exact: bool (strict equality after normalization)
      response_normalized / ground_truth_normalized: canonical forms
      notes: explanation of comparison path
    """

    def __init__(self):  # pragma: no cover - trivial
        pass

    # --------------- public API ---------------
    def __call__(
        self,
        *,
        response: Any,
        ground_truth: Any,
        **kwargs,
    ) -> dict[str, Any]:
        r_norm, r_type = self._normalize(response)
        g_norm, g_type = self._normalize(ground_truth)

        # Exact normalized equality
        if r_norm == g_norm:
            return {
                "score": 1.0,
                "exact": True,
                "response_normalized": r_norm,
                "ground_truth_normalized": g_norm,
                "notes": f"Normalized values equal (type {r_type}).",
            }

        # Numeric closeness (floats / ints)
        if self._is_number(r_norm) and self._is_number(g_norm):
            return self._score_numeric(r_norm, g_norm)

        # Iterable (set-like) overlap scoring for unordered collections
        if self._is_iterable_non_string(r_norm) and self._is_iterable_non_string(g_norm):
            return self._score_iterables(r_norm, g_norm)

        # Fallback string comparison (case & whitespace insensitive)
        r_str = self._as_simple_string(r_norm)
        g_str = self._as_simple_string(g_norm)
        if r_str == g_str:
            return {
                "score": 1.0,
                "exact": True,
                "response_normalized": r_str,
                "ground_truth_normalized": g_str,
                "notes": "String forms match after normalization.",
            }

        # Partial token overlap (very lightweight)
        r_tokens = set(filter(None, r_str.split()))
        g_tokens = set(filter(None, g_str.split()))
        if r_tokens and g_tokens:
            inter = len(r_tokens & g_tokens)
            union = len(r_tokens | g_tokens)
            token_score = inter / union if union else 0.0
        else:
            token_score = 0.0
        return {
            "score": round(token_score, 4),
            "exact": False,
            "response_normalized": r_norm,
            "ground_truth_normalized": g_norm,
            "notes": "Fallback token overlap scoring.",
        }

    # --------------- helpers ---------------
    def _normalize(self, val: Any):
        """Produce a canonical comparable form.

            - Dicts -> sorted list of (key, normalized_value)
            - Sets -> sorted list of normalized elements
            - Lists/Tuples -> list of normalized elements
            - Strings -> stripped lowercased
        - Numbers -> float (int retention for equality path not required)
            - Other -> unchanged
        """
        if isinstance(val, dict):
            items = sorted((k, self._normalize(v)[0]) for k, v in val.items())
            return items, "dict"
        if isinstance(val, set):
            elems = sorted(self._normalize(v)[0] for v in val)
            return elems, "set"
        if isinstance(val, (list, tuple)):
            elems = [self._normalize(v)[0] for v in val]
            return elems, "list"
        if isinstance(val, str):
            return val.strip().lower(), "str"
        if self._is_number(val):
            try:
                return float(val), "number"
            except Exception:
                return val, "number"  # fallback
        return val, type(val).__name__

    def _is_number(self, v: Any) -> bool:
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def _is_iterable_non_string(self, v: Any) -> bool:
        return isinstance(v, (list, tuple, set))

    def _score_numeric(self, r: float, g: float) -> dict[str, Any]:
        if any(math.isnan(x) for x in [r, g]):  # pragma: no cover
            return {
                "score": 0.0,
                "exact": False,
                "response_normalized": r,
                "ground_truth_normalized": g,
                "notes": "NaN encountered; score 0.",
            }
        if g == 0:
            # Absolute diff scoring when ground truth is zero
            diff = abs(r - g)
            score = 1.0 if diff == 0 else max(0.0, 1 - min(diff, 1))
        else:
            rel_err = abs(r - g) / abs(g)
            score = max(0.0, 1 - rel_err)
        return {
            "score": round(score, 4),
            "exact": r == g,
            "response_normalized": r,
            "ground_truth_normalized": g,
            "notes": "Numeric relative/absolute error scoring.",
        }

    def _score_iterables(self, r_iter: Iterable[Any], g_iter: Iterable[Any]):
        r_set = set(r_iter)
        g_set = set(g_iter)
        if not r_set and not g_set:
            return {
                "score": 1.0,
                "exact": True,
                "response_normalized": list(r_set),
                "ground_truth_normalized": list(g_set),
                "notes": "Both empty iterables.",
            }
        inter = len(r_set & g_set)
        union = len(r_set | g_set)
        score = inter / union if union else 0.0
        return {
            "score": round(score, 4),
            "exact": score == 1.0,
            "response_normalized": list(r_set),
            "ground_truth_normalized": list(g_set),
            "notes": "Jaccard similarity over iterable elements.",
        }

    def _as_simple_string(self, v: Any) -> str:
        if isinstance(v, str):
            return v
        return str(v).strip().lower()
