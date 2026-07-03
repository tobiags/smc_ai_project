"""SQLite persistence layer — backtest runs, quarter results, trades, settings.

SQLAlchemy 2.0 declarative models. The database lives at data/smc.db by
default; tests inject their own path via init_db(path).
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from smc_ai.config import get_settings


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(UTC)


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20))
    kind: Mapped[str] = mapped_column(String(20), default="quarterly")  # quarterly | full
    min_rr: Mapped[float] = mapped_column(Float, default=2.5)
    scan_step: Mapped[int] = mapped_column(Integer, default=120)
    sim_horizon: Mapped[int] = mapped_column(Integer, default=500)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|running|done|failed
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    quarters: Mapped[list["QuarterResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    trades: Mapped[list["Trade"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )

    def to_dict(self, with_children: bool = False) -> dict:
        d = {
            "id": self.id,
            "symbol": self.symbol,
            "kind": self.kind,
            "min_rr": self.min_rr,
            "scan_step": self.scan_step,
            "sim_horizon": self.sim_horizon,
            "status": self.status,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
        if with_children:
            d["quarters"] = [q.to_dict() for q in self.quarters]
            d["trades"] = [t.to_dict() for t in self.trades]
        return d


class QuarterResult(Base):
    __tablename__ = "quarter_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("backtest_runs.id"))
    label: Mapped[str] = mapped_column(String(10))  # e.g. 2026Q1
    start: Mapped[str] = mapped_column(String(40))
    end: Mapped[str] = mapped_column(String(40))
    kpis: Mapped[dict] = mapped_column(JSON, default=dict)
    equity_curve: Mapped[list] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    run: Mapped[BacktestRun] = relationship(back_populates="quarters")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "label": self.label,
            "start": self.start,
            "end": self.end,
            "kpis": self.kpis,
            "equity_curve": self.equity_curve,
            "error": self.error,
        }


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("backtest_runs.id"))
    quarter_label: Mapped[str | None] = mapped_column(String(10), nullable=True)
    symbol: Mapped[str] = mapped_column(String(20))
    timestamp: Mapped[str] = mapped_column(String(40))
    direction: Mapped[str] = mapped_column(String(10))
    entry: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    rr: Mapped[float] = mapped_column(Float)
    pnl: Mapped[float] = mapped_column(Float)
    pnl_r: Mapped[float] = mapped_column(Float)
    outcome: Mapped[str] = mapped_column(String(10))  # tp | sl | open
    status: Mapped[str] = mapped_column(String(10))   # closed | open

    run: Mapped[BacktestRun] = relationship(back_populates="trades")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "quarter_label": self.quarter_label,
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "direction": self.direction,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "rr": self.rr,
            "pnl": self.pnl,
            "pnl_r": self.pnl_r,
            "outcome": self.outcome,
            "status": self.status,
        }


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


# ── Engine / session management ─────────────────────────────────────────────

_engine = None
_SessionLocal: sessionmaker | None = None


def default_db_path() -> Path:
    return get_settings().data_dir / "smc.db"


def init_db(db_path: Path | None = None):
    """Create engine + tables. Call once at app startup (or per test)."""
    global _engine, _SessionLocal
    path = Path(db_path) if db_path else default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: sessions are used from the backtest worker thread
    _engine = create_engine(
        f"sqlite:///{path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_session() -> Session:
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()
