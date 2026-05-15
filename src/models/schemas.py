from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# --- teams ---


class Team(BaseModel):
    id: Optional[str] = None
    team_number: Optional[str] = None
    nickname: Optional[str] = None
    drivetrain_type: Optional[str] = None
    can_cross_bump: Optional[bool] = None
    can_use_trench: Optional[bool] = None
    shooter_type: Optional[str] = None
    shoots_on_move: Optional[bool] = None
    can_intake_from_outpost: Optional[bool] = None
    max_climb_level: Optional[int] = None
    pit_notes: Optional[str] = None
    created_at: Optional[datetime] = None


# --- responses ---


class MatchResponse(BaseModel):
    id: str
    date: Optional[date]
    scouter: Optional[str]
    event_key: str
    type_match: str  # 'qual', 'playoff', 'pre-scouting'
    match_number: int
    match_key: str
    alliance: str  # 'red' | 'blue'
    team_number: str
    starting_zone: Optional[str]

    # auto
    auto_fuels: int
    auto_feeds: int
    auto_climb: bool
    auto_climb_zone: Optional[str]  # 'L1'

    # teleop
    teleop_fuels: int
    teleop_feeds: int
    teleop_climb: bool
    teleop_climb_zone: Optional[str]  # 'L1' | 'L2' | 'L3'

    # outros
    played_defense: bool
    passed_trench: bool
    passed_bump: bool
    robot_failed: bool
    total_fouls: int
    comments: Optional[str]
    created_at: Optional[datetime]


# --- pre_processing view (agregada por time) ---


class TeamStats(BaseModel):
    teamNumber: Optional[str] = None
    playedMatchs: int = 0

    # auto
    autoFuelsAVGPoints: Optional[float] = None
    autoFeedAVG: Optional[float] = None
    autoL1AVG: Optional[float] = None
    autoL1AVGPoints: Optional[float] = None
    autoPoints: Optional[float] = None

    # teleop
    teleFuelsAVGPoints: Optional[float] = None
    teleFeedAVG: Optional[float] = None
    telePoints: Optional[float] = None

    # endgame
    endL1AVG: Optional[float] = None
    endL1AVGPoints: Optional[float] = None
    endL2AVG: Optional[float] = None
    endL2AVGPoints: Optional[float] = None
    endL3AVG: Optional[float] = None
    endL3AVGPoints: Optional[float] = None
    endClimbAVGPoints: Optional[float] = None
    endClimbAVGFail: Optional[float] = None
    endPoints: Optional[float] = None

    # misc
    defenseTotal: Optional[int] = None
    failedTotal: Optional[int] = None
    foulsAVG: Optional[float] = None
    trenchPassedAVG: Optional[float] = None
    bumpPassedAVG: Optional[float] = None
    totalPoints: Optional[float] = None
