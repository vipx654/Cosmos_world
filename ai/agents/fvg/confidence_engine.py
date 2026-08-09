"""
===============================================================================
COSMOS Fair Value Gap Confidence Engine

Produces the final confidence score for each Fair Value Gap.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.models import (
    FairValueGap,
    FVGStatus,
    InversionStatus,
)


class ConfidenceEngine:
    """
    Calculates final FVG confidence.

    V1 combines:

    - Probability
    - Strength
    - Confirmation evidence
    - Mitigation state
    - Inversion state
    - Validity

    The score is normalized to 0-100.
    """

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FairValueGap]:

        if not fvgs:
            return []

        for fvg in fvgs:

            # -------------------------------------------------------------
            # Base components
            # -------------------------------------------------------------

            probability = max(
                0.0,
                min(
                    100.0,
                    float(fvg.probability),
                ),
            )

            strength = max(
                0.0,
                min(
                    100.0,
                    float(fvg.strength),
                ),
            )

            # -------------------------------------------------------------
            # Weighted base score
            # -------------------------------------------------------------

            confidence = (
                probability * 0.45
                +
                strength * 0.35
                +
                float(fvg.confidence) * 0.20
            )

            # -------------------------------------------------------------
            # Validity
            # -------------------------------------------------------------

            if not fvg.valid:

                confidence -= 30.0

                fvg.evidence.append(
                    "FVG Invalid"
                )

            # -------------------------------------------------------------
            # Freshness
            # -------------------------------------------------------------

            if fvg.status == FVGStatus.FRESH:

                confidence += 8.0

            elif fvg.status == FVGStatus.PARTIAL:

                confidence += 3.0

            elif fvg.status == FVGStatus.TESTED:

                confidence -= 3.0

            elif fvg.status == FVGStatus.FILLED:

                confidence -= 25.0

            elif fvg.status == FVGStatus.INVALID:

                confidence -= 35.0

            # -------------------------------------------------------------
            # Inversion
            # -------------------------------------------------------------

            if (
                fvg.inversion_status
                == InversionStatus.CONFIRMED
            ):

                confidence -= 8.0

                fvg.evidence.append(
                    "FVG Inverted"
                )

            # -------------------------------------------------------------
            # Evidence quality
            # -------------------------------------------------------------

            evidence_count = len(
                fvg.evidence
            )

            if evidence_count >= 6:

                confidence += 8.0

            elif evidence_count >= 4:

                confidence += 5.0

            elif evidence_count >= 2:

                confidence += 2.0

            # -------------------------------------------------------------
            # Normalize
            # -------------------------------------------------------------

            confidence = max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            )

            fvg.confidence = round(
                confidence,
                2,
            )

            # -------------------------------------------------------------
            # Confidence labels
            # -------------------------------------------------------------

            if fvg.confidence >= 85.0:

                label = "Very High FVG Confidence"

            elif fvg.confidence >= 70.0:

                label = "High FVG Confidence"

            elif fvg.confidence >= 55.0:

                label = "Moderate FVG Confidence"

            else:

                label = "Low FVG Confidence"

            if label not in fvg.evidence:

                fvg.evidence.append(
                    label
                )

        return fvgs