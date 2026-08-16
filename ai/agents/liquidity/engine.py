"""
===============================================================================
COSMOS Liquidity Engine

Institutional Liquidity Intelligence Orchestrator

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, Any

from ai.context import MarketContext
from ai.models import AgentResult

from ai.agents.liquidity.validator import LiquidityValidator

from ai.agents.liquidity.models import (
    LiquidityAnalysis,
    LiquidityObject,
    LiquidityType,
)

from ai.agents.liquidity.buyside_engine import BuySideEngine
from ai.agents.liquidity.sellside_engine import SellSideEngine
from ai.agents.liquidity.internal_engine import InternalLiquidityEngine
from ai.agents.liquidity.external_engine import ExternalLiquidityEngine
from ai.agents.liquidity.cluster_engine import ClusterEngine
from ai.agents.liquidity.quality_engine import QualityEngine
from ai.agents.liquidity.map_engine import LiquidityMapEngine
from ai.agents.liquidity.confidence_engine import ConfidenceEngine

from ai.agents.liquidity.utils import (
    average_quality,
    strongest_liquidity,
    weakest_liquidity,
)


# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# PIPELINE STEP
# =============================================================================


@dataclass(slots=True)
class PipelineStep:

    name: str

    runner: Callable[..., Any]


# =============================================================================
# ENGINE
# =============================================================================


class LiquidityEngine:

    """
    Institutional Liquidity AI.

    Responsibilities:

        • Validate analysis dependencies
        • Detect Buy Side Liquidity
        • Detect Sell Side Liquidity
        • Detect Internal Liquidity
        • Detect External Liquidity
        • Calculate liquidity quality
        • Build liquidity clusters
        • Build complete liquidity map
        • Calculate institutional confidence
        • Calculate directional liquidity balance
        • Identify strongest / weakest liquidity
        • Publish shared intelligence
        • Publish chart-ready annotations when supported
        • Maintain execution diagnostics
        • Maintain backward-compatible result contracts

    The engine is intentionally modular so future intelligence modules
    can be inserted without replacing the existing pipeline.
    """

    AGENT_NAME = "liquidity"

    AGENT_VERSION = "1.0.0"

    AGENT_AUTHOR = "COSMOS"

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(self):

        logger.info(
            "Initializing COSMOS Liquidity Engine..."
        )

        # ---------------------------------------------------------------------
        # Sub Engines
        # ---------------------------------------------------------------------

        self.buy_side_engine = BuySideEngine()

        self.sell_side_engine = SellSideEngine()

        self.internal_engine = InternalLiquidityEngine()

        self.external_engine = ExternalLiquidityEngine()

        self.cluster_engine = ClusterEngine()

        self.quality_engine = QualityEngine()

        self.map_engine = LiquidityMapEngine()

        self.confidence_engine = ConfidenceEngine()

        # ---------------------------------------------------------------------
        # Performance
        # ---------------------------------------------------------------------

        self.execution_statistics: dict[str, float] = {}

        self.execution_count = 0

        self.last_execution_ms = 0.0

        # ---------------------------------------------------------------------
        # Runtime Diagnostics
        # ---------------------------------------------------------------------

        self.last_error: str | None = None

        self.last_success = False

        # ---------------------------------------------------------------------
        # Pipeline
        # ---------------------------------------------------------------------

        self.pipeline = [

            PipelineStep(
                name="validator",
                runner=LiquidityValidator.validate,
            ),

            PipelineStep(
                name="buy_side",
                runner=self.buy_side_engine.analyze,
            ),

            PipelineStep(
                name="sell_side",
                runner=self.sell_side_engine.analyze,
            ),

            PipelineStep(
                name="internal",
                runner=self.internal_engine.analyze,
            ),

            PipelineStep(
                name="external",
                runner=self.external_engine.analyze,
            ),

            PipelineStep(
                name="quality",
                runner=self.quality_engine.analyze,
            ),

            PipelineStep(
                name="clusters",
                runner=self.cluster_engine.analyze,
            ),

            PipelineStep(
                name="liquidity_map",
                runner=self.map_engine.build,
            ),

            PipelineStep(
                name="confidence",
                runner=self.confidence_engine.calculate,
            ),
        ]

        logger.info(
            "COSMOS Liquidity Engine initialized."
        )

    # =========================================================================
    # PERFORMANCE TIMER
    # =========================================================================

    def _execute_step(
        self,
        step_name: str,
        function: Callable,
        *args,
        **kwargs,
    ):

        start = time.perf_counter()

        try:

            result = function(
                *args,
                **kwargs,
            )

        except Exception as exc:

            logger.exception(
                "Liquidity pipeline step '%s' failed.",
                step_name,
            )

            self.last_error = (
                f"{step_name}: {exc}"
            )

            raise

        elapsed = (

            time.perf_counter()

            - start

        ) * 1000

        self.execution_statistics[
            step_name
        ] = round(
            elapsed,
            3,
        )

        logger.debug(
            "%s completed in %.3f ms",
            step_name,
            elapsed,
        )

        return result

    # =========================================================================
    # SWING EXTRACTION
    # =========================================================================

    @staticmethod
    def _extract_swings(
        context: MarketContext,
    ) -> list:

        try:

            market_structure = context.memory[
                "market_structure"
            ]

        except KeyError as exc:

            raise RuntimeError(

                "Market Structure Agent must execute "
                "before Liquidity Agent."

            ) from exc

        if not isinstance(
            market_structure,
            dict,
        ):

            raise RuntimeError(
                "Invalid market structure memory."
            )

        swings = market_structure.get(
            "swings",
            [],
        )

        if swings is None:

            return []

        if not isinstance(
            swings,
            list,
        ):

            raise RuntimeError(
                "Market structure swings must be a list."
            )

        return swings

    # =========================================================================
    # LEVEL VALIDATION
    # =========================================================================

    @staticmethod
    def _clean_levels(
        levels: list[LiquidityObject],
    ) -> list[LiquidityObject]:

        if not levels:

            return []

        cleaned: list[
            LiquidityObject
        ] = []

        seen: set[
            tuple
        ] = set()

        for level in levels:

            if level is None:

                continue

            try:

                price = float(
                    level.price
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if price != price:

                continue

            if price in (
                float("inf"),
                float("-inf"),
            ):

                continue

            level.price = round(
                price,
                10,
            )

            key = (

                level.liquidity_type,

                level.price,

                level.source,
            )

            if key in seen:

                continue

            seen.add(
                key
            )

            cleaned.append(
                level
            )

        return cleaned

    # =========================================================================
    # LIQUIDITY STATISTICS
    # =========================================================================

    @staticmethod
    def _calculate_statistics(
        levels: list[LiquidityObject],
    ) -> dict[str, Any]:

        if not levels:

            return {

                "total_levels": 0,

                "average_quality": 0.0,

                "average_strength": 0.0,

                "average_confidence": 0.0,

                "average_touches": 0.0,

                "max_quality": 0.0,

                "min_quality": 0.0,
            }

        qualities = [
            level.quality
            for level in levels
        ]

        strengths = [
            level.strength
            for level in levels
        ]

        confidences = [
            level.confidence
            for level in levels
        ]

        touches = [
            level.touches
            for level in levels
        ]

        return {

            "total_levels": len(
                levels
            ),

            "average_quality": average_quality(
                levels
            ),

            "average_strength": round(
                sum(strengths)
                / len(strengths),
                2,
            ),

            "average_confidence": round(
                sum(confidences)
                / len(confidences),
                2,
            ),

            "average_touches": round(
                sum(touches)
                / len(touches),
                2,
            ),

            "max_quality": round(
                max(qualities),
                2,
            ),

            "min_quality": round(
                min(qualities),
                2,
            ),
        }

    # =========================================================================
    # LIQUIDITY BALANCE
    # =========================================================================

    @staticmethod
    def _calculate_balance(
        buy_side: list[LiquidityObject],
        sell_side: list[LiquidityObject],
    ) -> dict[str, Any]:

        buy_strength = sum(

            level.strength

            for level in buy_side

        )

        sell_strength = sum(

            level.strength

            for level in sell_side

        )

        total_strength = (

            buy_strength

            +

            sell_strength

        )

        if total_strength <= 0:

            return {

                "buy_strength": 0.0,

                "sell_strength": 0.0,

                "buy_ratio": 0.0,

                "sell_ratio": 0.0,

                "dominance": "NEUTRAL",

            }

        buy_ratio = (

            buy_strength

            /

            total_strength

        )

        sell_ratio = (

            sell_strength

            /

            total_strength

        )

        if buy_ratio >= 0.60:

            dominance = "BUY_SIDE_DOMINANT"

        elif sell_ratio >= 0.60:

            dominance = "SELL_SIDE_DOMINANT"

        else:

            dominance = "BALANCED"

        return {

            "buy_strength": round(
                buy_strength,
                2,
            ),

            "sell_strength": round(
                sell_strength,
                2,
            ),

            "buy_ratio": round(
                buy_ratio,
                4,
            ),

            "sell_ratio": round(
                sell_ratio,
                4,
            ),

            "dominance": dominance,
        }

    # =========================================================================
    # LIQUIDITY EXTREMES
    # =========================================================================

    @staticmethod
    def _calculate_extremes(
        levels: list[LiquidityObject],
    ) -> dict[str, Any]:

        strongest = strongest_liquidity(
            levels
        )

        weakest = weakest_liquidity(
            levels
        )

        highest_price = None

        lowest_price = None

        if levels:

            highest_price = max(

                level.price

                for level in levels

            )

            lowest_price = min(

                level.price

                for level in levels

            )

        return {

            "strongest": strongest,

            "weakest": weakest,

            "highest_price": highest_price,

            "lowest_price": lowest_price,
        }

    # =========================================================================
    # LIQUIDITY COUNTS
    # =========================================================================

    @staticmethod
    def _calculate_counts(
        buy_side: list[LiquidityObject],
        sell_side: list[LiquidityObject],
        internal: list[LiquidityObject],
        external: list[LiquidityObject],
        clusters: list,
    ) -> dict[str, int]:

        return {

            "buy_side": len(
                buy_side
            ),

            "sell_side": len(
                sell_side
            ),

            "internal": len(
                internal
            ),

            "external": len(
                external
            ),

            "clusters": len(
                clusters
            ),

            "total": (

                len(buy_side)

                +

                len(sell_side)

                +

                len(internal)

                +

                len(external)

            ),
        }

    # =========================================================================
    # REASONS
    # =========================================================================

    @staticmethod
    def _build_reasons(
        counts: dict[str, int],
        confidence: float,
        statistics: dict[str, Any],
        balance: dict[str, Any],
    ) -> list[str]:

        return [

            (
                f"Buy Side Levels : "
                f"{counts['buy_side']}"
            ),

            (
                f"Sell Side Levels : "
                f"{counts['sell_side']}"
            ),

            (
                f"Internal Levels : "
                f"{counts['internal']}"
            ),

            (
                f"External Levels : "
                f"{counts['external']}"
            ),

            (
                f"Liquidity Clusters : "
                f"{counts['clusters']}"
            ),

            (
                f"Total Liquidity Levels : "
                f"{counts['total']}"
            ),

            (
                f"Average Quality : "
                f"{statistics['average_quality']:.2f}"
            ),

            (
                f"Average Strength : "
                f"{statistics['average_strength']:.2f}"
            ),

            (
                f"Average Confidence : "
                f"{statistics['average_confidence']:.2f}"
            ),

            (
                f"Liquidity Dominance : "
                f"{balance['dominance']}"
            ),

            (
                f"Overall Confidence : "
                f"{confidence:.2f}"
            ),
        ]

    # =========================================================================
    # MEMORY PUBLICATION
    # =========================================================================

    def _publish_memory(
        self,
        context: MarketContext,
        buy_side: list[LiquidityObject],
        sell_side: list[LiquidityObject],
        internal: list[LiquidityObject],
        external: list[LiquidityObject],
        clusters: list,
        liquidity_map,
        confidence: float,
        statistics: dict[str, Any],
        balance: dict[str, Any],
        extremes: dict[str, Any],
    ) -> None:

        context.memory[
            "liquidity"
        ] = {

            # ---------------------------------------------------------
            # Core Liquidity
            # ---------------------------------------------------------

            "buy_side": buy_side,

            "sell_side": sell_side,

            "internal": internal,

            "external": external,

            "clusters": clusters,

            "map": liquidity_map,

            "confidence": confidence,

            # ---------------------------------------------------------
            # Advanced Intelligence
            # ---------------------------------------------------------

            "statistics": statistics,

            "balance": balance,

            "strongest": extremes[
                "strongest"
            ],

            "weakest": extremes[
                "weakest"
            ],

            "highest_price": extremes[
                "highest_price"
            ],

            "lowest_price": extremes[
                "lowest_price"
            ],

            # ---------------------------------------------------------
            # Engine Diagnostics
            # ---------------------------------------------------------

            "execution": {

                "agent": self.AGENT_NAME,

                "version": self.AGENT_VERSION,

                "execution_count": (
                    self.execution_count
                ),

                "statistics": (
                    self.execution_statistics.copy()
                ),
            },
        }

    # =========================================================================
    # EVENT PUBLICATION
    # =========================================================================

    @staticmethod
    def _publish_event(
        context: MarketContext,
        confidence: float,
        counts: dict[str, int],
    ) -> None:

        if not hasattr(
            context,
            "events",
        ):

            return

        try:

            context.events.append(

                {

                    "agent": "liquidity",

                    "event": "LIQUIDITY_UPDATED",

                    "confidence": confidence,

                    "levels": counts[
                        "total"
                    ],

                    "clusters": counts[
                        "clusters"
                    ],
                }

            )

        except Exception:

            logger.debug(
                "Unable to publish liquidity event.",
                exc_info=True,
            )

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        logger.info(
            "Liquidity analysis started."
        )

        total_start = time.perf_counter()

        self.execution_count += 1

        self.last_error = None

        self.last_success = False

        # ---------------------------------------------------------------------
        # Reset Per-Run Statistics
        # ---------------------------------------------------------------------

        self.execution_statistics = {}

        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        self._execute_step(

            "validator",

            LiquidityValidator.validate,

            context,

        )

        # ---------------------------------------------------------------------
        # Market Structure
        # ---------------------------------------------------------------------

        swings = self._extract_swings(
            context
        )

        logger.debug(
            "Liquidity analysis received %d swings.",
            len(swings),
        )

        # ---------------------------------------------------------------------
        # Buy Side Liquidity
        # ---------------------------------------------------------------------

        buy_side = self._execute_step(

            "buy_side",

            self.buy_side_engine.analyze,

            swings,

        )

        # ---------------------------------------------------------------------
        # Sell Side Liquidity
        # ---------------------------------------------------------------------

        sell_side = self._execute_step(

            "sell_side",

            self.sell_side_engine.analyze,

            swings,

        )

        # ---------------------------------------------------------------------
        # Internal Liquidity
        # ---------------------------------------------------------------------

        internal = self._execute_step(

            "internal",

            self.internal_engine.analyze,

            swings,

        )

        # ---------------------------------------------------------------------
        # External Liquidity
        # ---------------------------------------------------------------------

        external = self._execute_step(

            "external",

            self.external_engine.analyze,

            swings,

        )

        # ---------------------------------------------------------------------
        # Clean Individual Results
        # ---------------------------------------------------------------------

        buy_side = self._clean_levels(
            buy_side
        )

        sell_side = self._clean_levels(
            sell_side
        )

        internal = self._clean_levels(
            internal
        )

        external = self._clean_levels(
            external
        )

        # ---------------------------------------------------------------------
        # Merge Liquidity
        # ---------------------------------------------------------------------

        all_levels = (

            buy_side

            +

            sell_side

            +

            internal

            +

            external

        )

        logger.debug(
            "Total liquidity levels: %d",
            len(all_levels),
        )

        # ---------------------------------------------------------------------
        # Quality Engine
        # ---------------------------------------------------------------------

        all_levels = self._execute_step(

            "quality",

            self.quality_engine.analyze,

            all_levels,

        )

        # ---------------------------------------------------------------------
        # Rebuild Clean Groups
        # ---------------------------------------------------------------------

        buy_side = [

            level

            for level in all_levels

            if level.liquidity_type
            == LiquidityType.BUY_SIDE

        ]

        sell_side = [

            level

            for level in all_levels

            if level.liquidity_type
            == LiquidityType.SELL_SIDE

        ]

        internal = [

            level

            for level in all_levels

            if level.liquidity_type
            == LiquidityType.INTERNAL

        ]

        external = [

            level

            for level in all_levels

            if level.liquidity_type
            == LiquidityType.EXTERNAL

        ]

        # ---------------------------------------------------------------------
        # Cluster Engine
        # ---------------------------------------------------------------------

        clusters = self._execute_step(

            "clusters",

            self.cluster_engine.analyze,

            all_levels,

        )

        # ---------------------------------------------------------------------
        # Liquidity Map
        # ---------------------------------------------------------------------

        liquidity_map = self._execute_step(

            "liquidity_map",

            self.map_engine.build,

            buy_side=buy_side,

            sell_side=sell_side,

            internal=internal,

            external=external,

            clusters=clusters,

        )

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        confidence = self._execute_step(

            "confidence",

            self.confidence_engine.calculate,

            liquidity_map,

        )

        # ---------------------------------------------------------------------
        # Advanced Statistics
        # ---------------------------------------------------------------------

        statistics = (
            self._calculate_statistics(
                all_levels
            )
        )

        # ---------------------------------------------------------------------
        # Directional Balance
        # ---------------------------------------------------------------------

        balance = (
            self._calculate_balance(

                buy_side,

                sell_side,

            )
        )

        # ---------------------------------------------------------------------
        # Strongest / Weakest
        # ---------------------------------------------------------------------

        extremes = (
            self._calculate_extremes(
                all_levels
            )
        )

        # ---------------------------------------------------------------------
        # Counts
        # ---------------------------------------------------------------------

        counts = (
            self._calculate_counts(

                buy_side,

                sell_side,

                internal,

                external,

                clusters,

            )
        )

        # ---------------------------------------------------------------------
        # Total Execution Time
        # ---------------------------------------------------------------------

        total_execution = round(

            (

                time.perf_counter()

                -

                total_start

            )

            * 1000,

            3,

        )

        self.execution_statistics[
            "total"
        ] = total_execution

        self.last_execution_ms = (
            total_execution
        )

        # ---------------------------------------------------------------------
        # Reasons
        # ---------------------------------------------------------------------

        reasons = (
            self._build_reasons(

                counts,

                confidence,

                statistics,

                balance,

            )
        )

        # ---------------------------------------------------------------------
        # Final Analysis
        # ---------------------------------------------------------------------

        analysis = LiquidityAnalysis(

            liquidity_map=liquidity_map,

            confidence=confidence,

            reasons=reasons,

        )

        # ---------------------------------------------------------------------
        # Shared Memory
        # ---------------------------------------------------------------------

        self._publish_memory(

            context,

            buy_side,

            sell_side,

            internal,

            external,

            clusters,

            liquidity_map,

            confidence,

            statistics,

            balance,

            extremes,

        )

        # ---------------------------------------------------------------------
        # Event Bus
        # ---------------------------------------------------------------------

        self._publish_event(

            context,

            confidence,

            counts,

        )

        # ---------------------------------------------------------------------
        # Agent Result
        # ---------------------------------------------------------------------

        result = AgentResult(

            name=self.AGENT_NAME,

            success=True,

            confidence=confidence,

            analysis=analysis,

            execution_time_ms=(
                total_execution
            ),

        )

        # ---------------------------------------------------------------------
        # Optional Diagnostics
        # ---------------------------------------------------------------------

        if hasattr(
            result,
            "diagnostics",
        ):

            result.diagnostics = {

                "agent": self.AGENT_NAME,

                "version": self.AGENT_VERSION,

                "execution_statistics":
                    self.execution_statistics.copy(),

                "counts": counts,

                "statistics": statistics,

                "balance": balance,

            }

        # ---------------------------------------------------------------------
        # Store Result
        # ---------------------------------------------------------------------

        context.add_result(
            result
        )

        self.last_success = True

        logger.info(

            "Liquidity Agent finished successfully "
            "in %.3f ms | confidence=%.2f | levels=%d",

            total_execution,

            confidence,

            counts["total"],

        )

        return result