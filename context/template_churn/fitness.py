"""Earth GA fitness contract: FitnessCalculationResult only. Projects define FitnessClass and call pipeline.get_fitness_score."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class FitnessCalculationResult(BaseModel):
    """Required return type for Earth GA calculate_fitness. score=optimization objective; scalars/rows for diagnostics."""

    score: float
    scalars: Optional[Dict[str, Any]] = None
    rows: Union[Dict[str, List[Union[str, float, int]]], None] = None
