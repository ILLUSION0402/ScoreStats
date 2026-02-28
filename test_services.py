# test_services.py

from app import create_app
from app.extensions import db
from app.models import Team, Player, Match
from app.services import MatchService, InningsService, BallService

app = create_app('development')

with app.app_context():
    def get_or_create_team(name, short_name):
        team = Team.query.filter_by(name=name).first()
        if team:
            return team, False
        team = Team(name=name, short_name=short_name)
        db.session.add(team)
        return team, True

    def get_or_create_player(name, team_id, role, jersey_number):
        player = Player.query.filter_by(name=name, team_id=team_id).first()
        if player:
            return player, False
        player = Player(
            name=name,
            team_id=team_id,
            role=role,
            jersey_number=jersey_number,
        )
        db.session.add(player)
        return player, True

    # Create teams (idempotent)
    team1, team1_created = get_or_create_team("Mumbai Indians", "MI")
    team2, team2_created = get_or_create_team("Chennai Super Kings", "CSK")
    if team1_created or team2_created:
        db.session.commit()
    
    # Create players (idempotent)
    rohit, rohit_created = get_or_create_player("Rohit Sharma", team1.id, "batsman", 45)
    ishan, ishan_created = get_or_create_player("Ishan Kishan", team1.id, "batsman", 77)
    bumrah, bumrah_created = get_or_create_player("Jasprit Bumrah", team1.id, "bowler", 93)
    dhoni, dhoni_created = get_or_create_player("MS Dhoni", team2.id, "wicket-keeper", 7)
    jadeja, jadeja_created = get_or_create_player("Ravindra Jadeja", team2.id, "all-rounder", 8)

    if any([rohit_created, ishan_created, bumrah_created, dhoni_created, jadeja_created]):
        db.session.commit()
    
    # Create match
    match = MatchService.create_match(
        team_1_id=team1.id,
        team_2_id=team2.id,
        match_type='T20',
        over_limit=20
    )
    print(f"Match created: {match.id}")
    
    # Record toss
    MatchService.record_toss(match.id, team1.id, 'bat')
    print(f" Toss recorded")
    
    # Start first innings
    innings = InningsService.start_innings(
        match_id=match.id,
        batting_team_id=team1.id,
        bowling_team_id=team2.id,
        innings_number=1,
      
    )
    print(f" Innings started: {innings.id}")
    
    # Record first ball: Rohit faces Jadeja, hits 4
    ball1 = BallService.record_ball(
        innings_id=innings.id,
        striker_id=rohit.id,
        non_striker_id=ishan.id,
        bowler_id=jadeja.id,
        runs=4
    )
    print(f" Ball 1 recorded: {ball1.over_number}.{ball1.ball_number} - {ball1.runs} runs")
    
    # Record second ball: Rohit hits 6
    ball2 = BallService.record_ball(
        innings_id=innings.id,
        striker_id=rohit.id,
        non_striker_id=ishan.id,
        bowler_id=jadeja.id,
        runs=6
    )
    print(f" Ball 2 recorded: {ball2.over_number}.{ball2.ball_number} - {ball2.runs} runs")
    
    # Get scorecard
    from app.services import StatisticsService
    scorecard = StatisticsService.get_batting_scorecard(innings.id)
    print(f" Batting Scorecard: {scorecard}")
    
    print("\n All services working!")
