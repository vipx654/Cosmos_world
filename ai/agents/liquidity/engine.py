"""
===============================================================================
COSMOS Liquidity Engine

Institutional Liquidity Orchestrator

Author: COSMOS Development Team
License: MIT
Version: 1.0.0
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
)

from ai.agents.liquidity.buyside_engine import BuySideEngine
from ai.agents.liquidity.sellside_engine import SellSideEngine
from ai.agents.liquidity.internal_engine import InternalLiquidityEngine
from ai.agents.liquidity.external_engine import ExternalLiquidityEngine
from ai.agents.liquidity.cluster_engine import ClusterEngine
from ai.agents.liquidity.quality_engine import QualityEngine
from ai.agents.liquidity.map_engine import LiquidityMapEngine
from ai.agents.liquidity.confidence_engine import ConfidenceEngine


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
    Institutional Liquidity AI

    Responsibilities

    • Detect Buy Side Liquidity

    • Detect Sell Side Liquidity

    • Detect Internal Liquidity

    • Detect External Liquidity

    • Build Liquidity Clusters

    • Calculate Quality

    • Build Liquidity Map

    • Produce Confidence

    • Publish Result
    """

    AGENT_NAME = "Liquidity"

    AGENT_VERSION = "1.0.0"

    AGENT_AUTHOR = "COSMOS"


    def __init__(self):

        logger.info(
            "Initializing Liquidity Engine..."
        )

        # ---------------------------------------------------------
        # Sub Engines
        # ---------------------------------------------------------

        self.buy_side_engine = BuySideEngine()

        self.sell_side_engine = SellSideEngine()

        self.internal_engine = InternalLiquidityEngine()

        self.external_engine = ExternalLiquidityEngine()

        self.cluster_engine = ClusterEngine()

        self.quality_engine = QualityEngine()

        self.map_engine = LiquidityMapEngine()

        self.confidence_engine = ConfidenceEngine()

        # ---------------------------------------------------------
        # Performance
        # ---------------------------------------------------------

        self.execution_statistics: dict[str, float] = {}

        logger.info(
            "Liquidity Engine Initialized."
        )


    # =============================================================
    # PERFORMANCE TIMER
    # =============================================================

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

                "%s failed",

                step_name,

            )

            raise exc

        elapsed = (

            time.perf_counter()

            -

            start

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
        # =============================================================
        # MAIN ANALYSIS
        # =============================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        logger.info(
            "Liquidity analysis started."
        )

        total_start = time.perf_counter()

        # ---------------------------------------------------------
        # Validation
        # ---------------------------------------------------------

        self._execute_step(

            "validator",

            LiquidityValidator.validate,

            context,

        )

        # ---------------------------------------------------------
        # Get Swings
        # ---------------------------------------------------------

        try:

            market_structure = context.memory[
                "market_structure"
            ]

            swings = market_structure["swings"]

        except KeyError as exc:

            raise RuntimeError(

                "Market Structure Agent must execute before Liquidity Agent."

            ) from exc

        # ---------------------------------------------------------
        # Individual Engines
        # ---------------------------------------------------------

        buy_side = self._execute_step(

            "buy_side",

            self.buy_side_engine.analyze,

            swings,

        )

        sell_side = self._execute_step(

            "sell_side",

            self.sell_side_engine.analyze,

            swings,

        )

        internal = self._execute_step(

            "internal",

            self.internal_engine.analyze,

            swings,

        )

        external = self._execute_step(

            "external",

            self.external_engine.analyze,

            swings,

        )

        # ---------------------------------------------------------
        # Merge Liquidity
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Quality Engine
        # ---------------------------------------------------------

        all_levels = self._execute_step(

            "quality",

            self.quality_engine.analyze,

            all_levels,

        )

        # ---------------------------------------------------------
        # Cluster Engine
        # ---------------------------------------------------------

        clusters = self._execute_step(

            "clusters",

            self.cluster_engine.analyze,

            all_levels,

        )
        # ---------------------------------------------------------
        # Liquidity Map
        # ---------------------------------------------------------

        liquidity_map = self._execute_step(

            "liquidity_map",

            self.map_engine.build,

            buy_side=buy_side,

            sell_side=sell_side,

            internal=internal,

            external=external,

            clusters=clusters,

        )

        # ---------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------

        confidence = self._execute_step(

            "confidence",

            self.confidence_engine.calculate,

            liquidity_map,

        )

        # ---------------------------------------------------------
        # Shared Memory
        # ---------------------------------------------------------

        context.memory["liquidity"] = {

            "buy_side": buy_side,

            "sell_side": sell_side,

            "internal": internal,

            "external": external,

            "clusters": clusters,

            "map": liquidity_map,

            "confidence": confidence,

            "statistics": self.execution_statistics.copy(),

        }

        # ---------------------------------------------------------
        # Future Event Bus
        # (Reserved for V2)
        # ---------------------------------------------------------

        if hasattr(context, "events"):

            try:

                context.events.append(

                    {

                        "agent": self.AGENT_NAME,

                        "event": "LIQUIDITY_UPDATED",

                        "confidence": confidence,

                    }

                )

            except Exception:

                pass

        # ---------------------------------------------------------
        # Total Execution Time
        # ---------------------------------------------------------

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

        logger.info(

            "Liquidity completed in %.3f ms",

            total_execution,

        )
        # ---------------------------------------------------------
        # Final Analysis
        # ---------------------------------------------------------

        analysis = LiquidityAnalysis(

            liquidity_map=liquidity_map,

            confidence=confidence,

            reasons=[

                f"Buy Side Levels : {len(buy_side)}",

                f"Sell Side Levels : {len(sell_side)}",

                f"Internal Levels : {len(internal)}",

                f"External Levels : {len(external)}",

                f"Liquidity Clusters : {len(clusters)}",

                f"Overall Confidence : {confidence:.2f}",

            ],

        )

        # ---------------------------------------------------------
        # Agent Result
        # ---------------------------------------------------------

        result = AgentResult(

            name=self.AGENT_NAME,

            success=True,

            confidence=confidence,

            analysis=analysis,

        )

        # ---------------------------------------------------------
        # Diagnostics
        # ---------------------------------------------------------

        if hasattr(result, "diagnostics"):

            result.diagnostics = {

                "agent": self.AGENT_NAME,

                "version": self.AGENT_VERSION,

                "execution_statistics":

                    self.execution_statistics.copy(),

            }

        # ---------------------------------------------------------
        # Store Result
        # ---------------------------------------------------------

        context.add_result(result)

        logger.info(

            "Liquidity Agent finished successfully."

        )

        return result