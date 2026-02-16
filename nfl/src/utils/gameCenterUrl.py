def gamecenter_url(*, league_id: str, season: int, team_id: int, week: int) -> str:
    return (
        f"https://fantasy.nfl.com/league/{league_id}/history/{season}/teamgamecenter"
        f"?teamId={team_id}&week={week}"
    )