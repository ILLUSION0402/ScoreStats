from app.models import Ball,BattingScorecard,BowlingScorecard,Partnership,Inning
from sqlalchemy import func
from app.extensions import db
class StatisticsService:
    '''
    Calculate cricket statistics.
    
    Responsibilities:
    - Get batting/bowling scorecards
    - Calculate player career stats
    - Get partnerships
    - Calculate team totals
    '''
    @staticmethod
    def get_batting_scorecard(innings_id):
        scorecards=BattingScorecard.query.filter_by(innings_id=innings_id).order_by(BattingScorecard.batting_position).all()
        return [
            {
                'player_id':sc.player_id,
                'player_name':sc.player.name if sc.player else 'Unknown',
                'runs':sc.runs,
                'balls':sc.balls_faced,
                'fours':sc.fours,
                'sixes':sc.sixes,
                'strike_rate':sc.strike_rate,
                'dismissal':sc.dismissal_type if sc.is_out else 'not_out'
            } for sc in scorecards
        ]
    @staticmethod
    def get_bowling_scorecard(innings_id):
        scorecards=BowlingScorecard.query.filter_by(innings_id=innings_id).order_by(BowlingScorecard.wickets_taken.desc()).all()
        return [{
            'player_id':sc.player_id,
            'player_name':sc.player.name if sc.player else 'Unknown',
            'overs':sc.overs_bowled,
            'maidens':sc.maidens,
            'wickets':sc.wickets_taken,
            'economy':sc.economy_rate,
            'dots':sc.dots
        } for sc in scorecards]
    @staticmethod
    def get_partnerships(innings_id):
        partnerships=Partnership.query.filter_by(inning_id=innings_id).order_by(Partnership.wickets_fallen).all()
        return [p.to_dict() for p in partnerships]
    @staticmethod
    def get_player_career_stats(player_id):
        batting_balls=Ball.query.filter_by(batsman_id=player_id).all()
        bowling_balls=Ball.query.filter_by(bowler_id=player_id).all()
        # batting stats
        total_runs=sum(b.runs_scored for b in batting_balls)
        balls_faced=sum(1 for b in batting_balls if b.is_legal_delivery)
        dismissals=Ball.query.filter_by(dismissed_player_id=player_id).count()
        # bowling stats
        runs_conceded=sum(b.runs_scored + b.extra_runs for b in bowling_balls)
        wickets=sum(1 for b in bowling_balls if b.is_wicket and b.wicket_type not in ['run-out'])
        balls_bowled=sum(1 for b in bowling_balls if b.is_legal_delivery)
        return {
            'batting':{
                'runs':total_runs,
                'balls_faced':balls_faced,
                'dismissals':dismissals,
                'average': round(total_runs/dismissals,2) if dismissals>0 else total_runs,
                'strike_rate':round((total_runs/balls_faced)*100,2) if balls_faced>0 else 0,
                'fours':sum(1 for b in batting_balls if b.runs_scored==4),
                'sixes':sum(1 for b in batting_balls if b.runs_scored==6)
            },
            'bowling':{
                'wickets':wickets,
                'runs_conceded':runs_conceded,
                'overs':balls_bowled/6,
                'average':round(runs_conceded/wickets,2) if wickets>0 else 0,
                'economy':round((runs_conceded)/(balls_bowled/6),2) if balls_bowled>0 else 0,
                'strike_rate':round(balls_bowled/wickets,2) if wickets>0 else 0
            }
        }
