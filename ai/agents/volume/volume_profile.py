"""
===============================================================================
COSMOS Volume Profile Engine

Builds a volume-at-price profile from OHLCV candles.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    DEFAULT_LOOKBACK,
    DEFAULT_PROFILE_ROWS,
    DEFAULT_VALUE_AREA_PERCENT,
    HVN_THRESHOLD,
    LVN_THRESHOLD,
)

from ai.agents.volume.models import (
    ProfileLevelType,
    VolumeProfile,
    VolumeProfileLevel,
)

from ai.agents.volume.utils import (
    candle_direction,
    candle_range,
    candle_volume,
    normalize_score,
)


class VolumeProfileEngine:
    """
    Builds a simplified volume-at-price profile.

    The engine distributes each candle's volume across the candle's price
    range. It then identifies:

        - POC
        - VAH
        - VAL
        - HVN
        - LVN

    This is a structural map. It does not produce an automatic trade entry.
    """

    def analyze(
        self,
        candles,
        lookback: int = DEFAULT_LOOKBACK,
        rows: int = DEFAULT_PROFILE_ROWS,
        value_area_percent: float = (
            DEFAULT_VALUE_AREA_PERCENT
        ),
    ) -> VolumeProfile:

        if not candles:

            return VolumeProfile()

        # =====================================================================
        # PARAMETERS
        # =====================================================================

        lookback = max(
            1,
            int(lookback),
        )

        rows = max(
            2,
            int(rows),
        )

        value_area_percent = max(
            1.0,
            min(
                100.0,
                float(
                    value_area_percent
                ),
            ),
        )

        # =====================================================================
        # RECENT CANDLES
        # =====================================================================

        recent = list(
            candles[-lookback:]
        )

        if not recent:

            return VolumeProfile()

        # =====================================================================
        # PRICE RANGE
        # =====================================================================

        highs = [
            float(
                getattr(
                    candle,
                    "high",
                    0.0,
                )
            )
            for candle in recent
        ]

        lows = [
            float(
                getattr(
                    candle,
                    "low",
                    0.0,
                )
            )
            for candle in recent
        ]

        profile_high = max(
            highs
        )

        profile_low = min(
            lows
        )

        price_range = (
            profile_high
            -
            profile_low
        )

        if price_range <= 0.0:

            return VolumeProfile()

        # =====================================================================
        # PRICE ROWS
        # =====================================================================

        row_size = (
            price_range
            /
            rows
        )

        row_volume = [
            0.0
            for _ in range(rows)
        ]

        # =====================================================================
        # DISTRIBUTE CANDLE VOLUME
        # =====================================================================

        for candle in recent:

            high = float(
                getattr(
                    candle,
                    "high",
                    0.0,
                )
            )

            low = float(
                getattr(
                    candle,
                    "low",
                    0.0,
                )
            )

            volume = candle_volume(
                candle
            )

            candle_span = (
                high - low
            )

            if candle_span <= 0.0:

                midpoint = (
                    high + low
                ) / 2.0

                row_index = int(
                    (
                        midpoint
                        -
                        profile_low
                    )
                    /
                    row_size
                )

                row_index = max(
                    0,
                    min(
                        rows - 1,
                        row_index,
                    ),
                )

                row_volume[
                    row_index
                ] += volume

                continue

            # -------------------------------------------------------------
            # Distribute volume proportionally across touched rows.
            # -------------------------------------------------------------

            first_row = int(
                (
                    low
                    -
                    profile_low
                )
                /
                row_size
            )

            last_row = int(
                (
                    high
                    -
                    profile_low
                )
                /
                row_size
            )

            first_row = max(
                0,
                min(
                    rows - 1,
                    first_row,
                ),
            )

            last_row = max(
                0,
                min(
                    rows - 1,
                    last_row,
                ),
            )

            touched_rows = (
                last_row
                -
                first_row
                +
                1
            )

            if touched_rows <= 0:

                continue

            distributed_volume = (
                volume
                /
                touched_rows
            )

            for row_index in range(
                first_row,
                last_row + 1,
            ):

                row_volume[
                    row_index
                ] += distributed_volume

        # =====================================================================
        # TOTAL VOLUME
        # =====================================================================

        total_volume = sum(
            row_volume
        )

        if total_volume <= 0.0:

            return VolumeProfile()

        max_volume = max(
            row_volume
        )

        average_row_volume = (
            total_volume
            /
            rows
        )

        # =====================================================================
        # POC
        # =====================================================================

        poc_index = max(
            range(rows),
            key=lambda index:
                row_volume[index],
        )

        poc_price = (
            profile_low
            +
            (
                poc_index
                +
                0.5
            )
            *
            row_size
        )

        # =====================================================================
        # VALUE AREA
        # =====================================================================

        target_volume = (
            total_volume
            *
            (
                value_area_percent
                /
                100.0
            )
        )

        accumulated_volume = (
            row_volume[poc_index]
        )

        lower_index = (
            poc_index
        )

        upper_index = (
            poc_index
        )

        # Expand from POC using the larger adjacent-volume row first.
        while (
            accumulated_volume
            <
            target_volume
        ):

            next_lower = (
                lower_index - 1
            )

            next_upper = (
                upper_index + 1
            )

            lower_volume = (
                row_volume[next_lower]
                if next_lower >= 0
                else -1.0
            )

            upper_volume = (
                row_volume[next_upper]
                if next_upper < rows
                else -1.0
            )

            if (
                lower_volume < 0.0
                and
                upper_volume < 0.0
            ):

                break

            if (
                upper_volume
                >
                lower_volume
            ):

                upper_index = (
                    next_upper
                )

                accumulated_volume += (
                    upper_volume
                )

            elif (
                lower_volume
                >
                upper_volume
            ):

                lower_index = (
                    next_lower
                )

                accumulated_volume += (
                    lower_volume
                )

            else:

                # Tie: prefer the side closer to the POC.
                if next_upper < rows:

                    upper_index = (
                        next_upper
                    )

                    accumulated_volume += (
                        upper_volume
                    )

                elif next_lower >= 0:

                    lower_index = (
                        next_lower
                    )

                    accumulated_volume += (
                        lower_volume
                    )

                else:

                    break

        value_area_low = (
            profile_low
            +
            lower_index
            *
            row_size
        )

        value_area_high = (
            profile_low
            +
            (
                upper_index
                +
                1
            )
            *
            row_size
        )

        # =====================================================================
        # PROFILE LEVELS
        # =====================================================================

        levels: list[
            VolumeProfileLevel
        ] = []

        for index, volume in enumerate(
            row_volume
        ):

            row_low = (
                profile_low
                +
                index
                *
                row_size
            )

            row_high = (
                row_low
                +
                row_size
            )

            price = (
                row_low
                +
                row_high
            ) / 2.0

            percentage = (
                volume
                /
                total_volume
            ) * 100.0

            strength = (
                volume
                /
                max_volume
            ) * 100.0

            # -------------------------------------------------------------
            # Level classification
            # -------------------------------------------------------------

            if index == poc_index:

                level_type = (
                    ProfileLevelType.POC
                )

            elif (
                volume
                >=
                average_row_volume
                *
                HVN_THRESHOLD
            ):

                level_type = (
                    ProfileLevelType.HVN
                )

            elif (
                volume
                <=
                average_row_volume
                *
                LVN_THRESHOLD
            ):

                level_type = (
                    ProfileLevelType.LVN
                )

            elif index == upper_index:

                level_type = (
                    ProfileLevelType.VALUE_HIGH
                )

            elif index == lower_index:

                level_type = (
                    ProfileLevelType.VALUE_LOW
                )

            else:

                # Ordinary profile row.
                #
                # We don't force every row into a special classification.
                continue

            evidence: list[str] = []

            if level_type == ProfileLevelType.POC:

                evidence.append(
                    "Point of Control"
                )

            elif level_type == ProfileLevelType.HVN:

                evidence.append(
                    "High Volume Node"
                )

            elif level_type == ProfileLevelType.LVN:

                evidence.append(
                    "Low Volume Node"
                )

            elif (
                level_type
                == ProfileLevelType.VALUE_HIGH
            ):

                evidence.append(
                    "Value Area High"
                )

            elif (
                level_type
                == ProfileLevelType.VALUE_LOW
            ):

                evidence.append(
                    "Value Area Low"
                )

            levels.append(
                VolumeProfileLevel(

                    price=round(
                        price,
                        8,
                    ),

                    volume=round(
                        volume,
                        8,
                    ),

                    level_type=level_type,

                    strength=round(
                        normalize_score(
                            strength
                        ),
                        2,
                    ),

                    percentage_of_total=round(
                        percentage,
                        4,
                    ),

                    evidence=evidence,
                )
            )

        # =====================================================================
        # HVN / LVN COLLECTIONS
        # =====================================================================

        high_volume_nodes = [
            level
            for level in levels
            if level.level_type
            == ProfileLevelType.HVN
        ]

        low_volume_nodes = [
            level
            for level in levels
            if level.level_type
            == ProfileLevelType.LVN
        ]

        # =====================================================================
        # PROFILE CONFIDENCE
        # =====================================================================

        # A concentrated profile has a stronger POC reference.
        poc_concentration = (
            row_volume[poc_index]
            /
            total_volume
        )

        confidence = normalize_score(
            poc_concentration
            *
            100.0
        )

        return VolumeProfile(

            levels=levels,

            poc=round(
                poc_price,
                8,
            ),

            value_area_high=round(
                value_area_high,
                8,
            ),

            value_area_low=round(
                value_area_low,
                8,
            ),

            high_volume_nodes=(
                high_volume_nodes
            ),

            low_volume_nodes=(
                low_volume_nodes
            ),

            total_volume=round(
                total_volume,
                8,
            ),

            confidence=round(
                confidence,
                2,
            ),
        )