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
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_length=1, max_length=12)
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


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 40)

    # Valid mission
    try:
        valid_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date="2024-06-01T09:00:00",
            duration_days=900,
            budget_millions=2500.0,
            crew=[
                CrewMember(
                    member_id="CM001",
                    name="Sarah Connor",
                    rank="commander",
                    age=40,
                    specialization="Mission Command",
                    years_experience=12
                ),
                CrewMember(
                    member_id="CM002",
                    name="John Smith",
                    rank="lieutenant",
                    age=35,
                    specialization="Navigation",
                    years_experience=7
                ),
                CrewMember(
                    member_id="CM003",
                    name="Alice Johnson",
                    rank="officer",
                    age=30,
                    specialization="Engineering",
                    years_experience=4
                ),
            ]
        )
        print("Valid mission created:")
        print(f"Mission: {valid_mission.mission_name}")
        print(f"ID: {valid_mission.mission_id}")
        print(f"Destination: {valid_mission.destination}")
        print(f"Duration: {valid_mission.duration_days} days")
        print(f"Budget: ${valid_mission.budget_millions}M")
        print(f"Crew size: {len(valid_mission.crew)}")
        print("Crew members:")
        for member in valid_mission.crew:
            print(f"- {member.name} ({member.rank}) - {member.specialization}")

    except ValidationError as e:
        print(e)

    print()
    print("=" * 40)

    # Invalid mission (no Commander or Captain)
    try:
        SpaceMission(
            mission_id="M2024_LUNA",
            mission_name="Moon Research Mission",
            destination="Moon",
            launch_date="2024-07-01T09:00:00",
            duration_days=200,
            budget_millions=1500.0,
            crew=[
                CrewMember(
                    member_id="CM004",
                    name="Bob Lee",
                    rank="lieutenant",
                    age=32,
                    specialization="Science Officer",
                    years_experience=6
                )
            ]
        )
    except ValidationError as e:
        print("Expected validation error:")
        print(e.errors()[0]['msg'])


if __name__ == "__main__":
    main()
