"""Domain types. The bottom layer: no imports from app.*"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Holding:
    id: int
    portfolio_id: int
    symbol: str
    units: int


@dataclass(frozen=True)
class Portfolio:
    id: int
    owner: str
    name: str
