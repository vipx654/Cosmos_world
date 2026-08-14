"""
===============================================================================
COSMOS Sweep Map Engine

Builds the institutional sweep map.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from collections.abc import Sequence

from ai.agents.sweep.models import (
    SweepMap,
    SweepObject,
)


class SweepMapEngine:
    """
    Builds the final immutable-style snapshot of Sweep Agent results.

    Responsibilities
    ----------------
    - Normalize sweep collections.
    - Preserve sweep object identity.
    - Build the complete sweep collection.
    - Prevent duplicate references in ``all_sweeps``.
    - Keep the output deterministic.

    Notes
    -----
    ``fake_sweeps`` and ``confirmed`` are classification views of the same
    detected sweep objects. They are therefore not merged into ``all_sweeps``.
    """

    @staticmethod
    def _normalize(
        sweeps: Sequence[SweepObject] | None,
    ) -> list[SweepObject]:
        """
        Normalize an optional sweep collection.

        The engine intentionally does not clone SweepObject instances because
        downstream stages progressively enrich the same objects.
        """

        if sweeps is None:
            return []

        return list(sweeps)

    @staticmethod
    def _build_all_sweeps(
        buy_side: Sequence[SweepObject],
        sell_side: Sequence[SweepObject],
    ) -> list[SweepObject]:
        """
        Build a deterministic collection of unique detected sweeps.

        Object identity is used rather than dataclass equality because two
        separate sweeps may legitimately have identical field values.
        """

        all_sweeps: list[SweepObject] = []
        seen: set[int] = set()

        for sweep in (*buy_side, *sell_side):
            identity = id(sweep)

            if identity in seen:
                continue

            seen.add(identity)
            all_sweeps.append(sweep)

        return all_sweeps

    def build(
        self,
        buy_side: Sequence[SweepObject] | None,
        sell_side: Sequence[SweepObject] | None,
        fake_sweeps: Sequence[SweepObject] | None,
        confirmed: Sequence[SweepObject] | None,
    ) -> SweepMap:
        """
        Build the final SweepMap.

        ``fake_sweeps`` and ``confirmed`` remain classification views and are
        not added separately to ``all_sweeps``.
        """

        normalized_buy_side = self._normalize(
            buy_side
        )

        normalized_sell_side = self._normalize(
            sell_side
        )

        normalized_fake_sweeps = self._normalize(
            fake_sweeps
        )

        normalized_confirmed = self._normalize(
            confirmed
        )

        all_sweeps = self._build_all_sweeps(
            normalized_buy_side,
            normalized_sell_side,
        )

        return SweepMap(
            buy_side=normalized_buy_side,
            sell_side=normalized_sell_side,
            fake_sweeps=normalized_fake_sweeps,
            confirmed=normalized_confirmed,
            all_sweeps=all_sweeps,
        )