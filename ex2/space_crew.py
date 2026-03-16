from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(min_length=18, max_length=80)
    specialization: str = Field(min_length=3, max_digits=30)
    years_experience: int = Field(min_length=0, max_length=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_items=1, max_items=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def check_safety_rules(self) -> "SpaceMission":
        """Custom validation for mission safety and crew requirements"""

        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        if not any(c.rank in
                   (Rank.commander, Rank.captain) for c in self.crew):
            raise ValueError("Mission must have at least one Commander "
                             "or Captain")

        if self.duration_days > 365:
            experienced_count = sum(1 for c in self.crew if 
                                    c.years_experience >= 5)
            if experienced_count < len(self.crew) / 2:
                raise ValueError(
                    "Long missions require at least 50% experienced crew"
                    "(5+ yrs)"
                )

        if not all(c.is_active for c in self.crew):
            raise ValueError("All crew members must be active")

        return self
