from mcp.server.fastmcp import FastMCP
from typing import Optional
from db.client import get_client
from utils.supabase import refresh_pre_processing
from models.schemas import Team, TeamStats, MatchResponse


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
            "stats": (
                TeamStats.model_validate(stats_data).model_dump()
                if stats_data
                else None
            ),
        }

    @mcp.tool()
    def compare_teams(team_numbers: list[str]) -> dict:
        """
        Compares multiple teams side by side. Returns pit scouting and aggregated match stats for each team. Use when the user wants to evaluate or rank a set of teams.
        """
        db = get_client()
        refresh_pre_processing()

        result = {}
        for team_number in team_numbers:
            pit = db.table("teams").select("*").eq("team_number", team_number).execute()
            team_data = pit.data[0] if pit.data else None

            stats = (
                db.table("pre_processing")
                .select("*")
                .eq("teamNumber", team_number)
                .execute()
            )
            stats_data = stats.data[0] if stats.data else None

            if not team_data and not stats_data:
                result[team_number] = {"error": f"Team {team_number} not found"}
            else:
                result[team_number] = {
                    "pit": (
                        Team.model_validate(team_data).model_dump()
                        if team_data
                        else None
                    ),
                    "stats": (
                        TeamStats.model_validate(stats_data).model_dump()
                        if stats_data
                        else None
                    ),
                }

        return result

    @mcp.tool()
    def get_match_data(
        match_numbers: Optional[list[int]] = None,
        team_numbers: Optional[list[str]] = None,
    ) -> dict | list:
        """
        Returns raw match data from the responses table. Can filter by match number(s), team number(s), or both combined. Use when the user asks how a team performed in a specific match, or wants to compare multiple teams across one or more matches.
        """
        if not match_numbers and not team_numbers:
            return {"error": "Provide at least one of match_numbers or team_numbers"}

        db = get_client()
        query = db.table("responses").select("*")

        if match_numbers:
            query = query.in_("match_number", match_numbers)
        if team_numbers:
            query = query.in_("team_number", team_numbers)

        rows = query.execute()

        if not rows.data:
            return {"error": "No matches found for the given filters"}

        return [MatchResponse.model_validate(row).model_dump() for row in rows.data]

    @mcp.tool()
    def rank_teams_by_metric(metric: str, top_n: Optional[int] = None) -> dict | list:
        """
        Ranks all teams by a specific stat from the pre_processing view. Use when the user wants to know which teams are best at a given metric, e.g. totalPoints, endClimbAVGPoints, autoPoints. Returns teams sorted descending by the metric value.
        """
        if metric not in TeamStats.model_fields.keys():
            return {"error": f"Invalid metric: {metric}"}

        refresh_pre_processing()
        db = get_client()
        rows = db.table("pre_processing").select("*").execute()

        ranked = []
        for row in rows.data:
            stats = TeamStats.model_validate(row)
            value = getattr(stats, metric)
            if value is not None:
                ranked.append((stats, value))

        if not ranked:
            return {"error": f"No data found for metric {metric}"}

        ranked.sort(key=lambda x: x[1], reverse=True)

        if top_n is not None:
            ranked = ranked[:top_n]

        return [
            {"team_number": stats.teamNumber, "value": value, "rank": i + 1}
            for i, (stats, value) in enumerate(ranked)
        ]

    @mcp.tool()
    def suggest_alliance_picks(
        captain_team: str,
        weights: dict[str, float],
        excluded_teams: Optional[list[str]] = None,
        top_n: int = 10,
    ) -> dict | list:
        """
        Suggests the best alliance picks for a given captain team based on weighted metrics. Weights are a dict mapping TeamStats field names to their importance (e.g. {'endClimbAVGPoints': 0.5, 'autoPoints': 0.3}). Excludes captain and any already-picked teams.
        """
        for metric in weights:
            if metric not in TeamStats.model_fields.keys():
                return {"error": f"Invalid metric: {metric}"}

        excluded = {captain_team, *(excluded_teams or [])}

        refresh_pre_processing()
        db = get_client()
        rows = db.table("pre_processing").select("*").execute()

        scored = []
        for row in rows.data:
            stats = TeamStats.model_validate(row)
            if stats.teamNumber in excluded:
                continue
            score = sum(
                getattr(stats, metric) * weight
                for metric, weight in weights.items()
                if getattr(stats, metric) is not None
            )
            scored.append((stats, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            {"rank": i + 1, "team_number": stats.teamNumber, "score": score, "stats": stats.model_dump()}
            for i, (stats, score) in enumerate(scored[:top_n])
        ]
