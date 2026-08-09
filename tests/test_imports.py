def test_core_imports():
    import ai
    import ai.models
    import ai.context
    import ai.brain
    import ai.memory
    import ai.decision_engine
    import ai.orchestrator


def test_agent_imports():
    from ai.agents.trend.engine import TrendEngine
    from ai.agents.smc.engine import SMCEngine
    from ai.agents.sweep.engine import SweepEngine
    from ai.agents.order_block.engine import OrderBlockEngine
    from ai.agents.market_structure.engine import MarketStructureEngine
    from ai.agents.liquidity.engine import LiquidityEngine
    from ai.agents.fvg.engine import FVGEngine
    from ai.agents.volume.engine import VolumeEngine
    from ai.agents.trap.engine import TrapEngine
    from ai.agents.strategy.engine import StrategyEngine
    from ai.agents.session.engine import SessionEngine
    from ai.agents.risk.engine import RiskEngine
    from ai.agents.execution.engine import ExecutionEngine
    from ai.agents.future_prediction.engine import FuturePredictionEngine