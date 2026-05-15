from mcp.server.fastmcp import FastMCP
from db.client import get_client
from utils.supabase import refresh_pre_processing
from models.schemas import Team, TeamStats


def register(mcp: FastMCP):

    @mcp.tool()
    def get_team_summary(team_number: str) -> dict:
        """
        Returns complete data for a specific team.
        Includes pit scouting info (drivetrain, shooter type, climb level)
        and aggregated match stats (avg points, climb rates, defense, failures).
        Use this when the user asks about a specific team's performance or capabilities.
        """
        db = get_client()

        pit = db.table("teams").select("*").eq("team_number", team_number).execute()
        team_data = pit.data[0] if pit.data else None

        refresh_pre_processing()
        stats = (
            db.table("pre_processing")
            .select("*")
            .eq("teamNumber", team_number)
            .execute()
        )
        stats_data = stats.data[0] if stats.data else None

        if not team_data and not stats_data:
            return {"error": f"Team {team_number} not found"}

        return {
            "pit": Team.model_validate(team_data).model_dump() if team_data else None,
            "stats": TeamStats.model_validate(stats_data).model_dump() if stats_data else None,
        }
