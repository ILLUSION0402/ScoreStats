from app.extensions import db 
from app.models import Ball,Inning,BattingScorecard,BowlingScorecard,Partnership
from sqlalchemy.exc import SQLAlchemyError
class BallService:
    '''
    Docstring for BallService
    handles all the ball recordings logic with cricket rules 
    Responsibilities:
    -Record a ball with validation 
    -auto-increment over/ball numbers
    -Rotate strikers on odd runs
    -Swap strikers at over completion
    -Updateall aggregation tables 
    -handle extras (wide,no-ball)
    '''
    @staticmethod
    def record_ball(innings_id,striker_id,non_striker_id,bowler_id,runs=0,extras=0,extra_type=None,is_wicket=False,wicket_type=None,dismissed_player_id=None,fielder_id=None,**kwargs):
        """      
        record a single ball 
        """
        try:
            if runs < 0 or runs > 7:
                raise ValueError("Runs must be between 0 and 7")
            if extras < 0:
                raise ValueError("Extras must be 0 or more")
            innings=Inning.query.get(innings_id)
            if not innings:
                raise ValueError(f"Inning {innings_id} not found")
            if innings.is_completed:
                raise ValueError("cannot record ball in completed innings")
            last_ball=Ball.query.filter_by(inning_id=innings_id)\
                .order_by(Ball.id.desc())\
                .first()
            is_legal_delivery = extra_type not in ['wide','no-ball']
            if not last_ball:
                over_number=0
                ball_number=1
            else:
                over_number=last_ball.over_number
                ball_number=last_ball.ball_number
                current_striker=last_ball.batsman_id
                current_non_striker=last_ball.non_striker_id
                if last_ball.is_legal_delivery:
                    if ball_number==6:
                        over_number+=1
                        ball_number=1
                        current_striker,current_non_striker=current_non_striker,current_striker
                    else:
                        ball_number+=1
            if dismissed_player_id is None:
                dismissed_player_id = kwargs.pop("dismissed_palyer_id", None)
            ball=Ball(
                inning_id=innings_id,
                over_number=over_number,
                ball_number=ball_number,
                batsman_id=striker_id,
                non_striker_id=non_striker_id,
                bowler_id=bowler_id,
                runs_scored=runs,
                extra_runs=extras,
                extra_type=extra_type,
                is_wicket=is_wicket,
                wicket_type=wicket_type,
                dismissed_player_id=dismissed_player_id,
                fielder_id=fielder_id,
                is_legal_delivery=is_legal_delivery,
            )
            db.session.add(ball)
            BallService._update_batting_scorecard(ball)
            BallService._update_bowling_scorecard(ball)
            BallService._update_partnership(ball)
            BallService._update_innings(ball)
            if is_wicket:
                BallService._handle_wicket(ball)
            db.session.commit()
            return ball
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"DataBase error:{str(e)}")
    @staticmethod
    def _update_batting_scorecard(ball):
        scorecard=BattingScorecard.query.filter_by(innings_id=ball.inning_id,player_id=ball.batsman_id).first()
        if not scorecard:
            existing_batsmen=BattingScorecard.query.filter_by(innings_id=ball.inning_id).count()
            scorecard=BattingScorecard(innings_id=ball.inning_id,player_id=ball.batsman_id,batting_position=existing_batsmen+1)
            db.session.add(scorecard)
        scorecard.update_stats(ball)
    @staticmethod
    def _update_bowling_scorecard(ball):
        scorecard = BowlingScorecard.query.filter_by(innings_id=ball.inning_id,player_id=ball.bowler_id).first()
        if not scorecard:
            scorecard = BowlingScorecard(innings_id=ball.inning_id,player_id=ball.bowler_id)
            db.session.add(scorecard)
        
        scorecard.update_stats(ball)
    @staticmethod
    def _update_partnership(ball):
        partnership=Partnership.query.filter_by(inning_id=ball.inning_id,is_active=True).first()
        if not partnership:
            wickets_fallen=Partnership.query.filter_by(inning_id=ball.inning_id).count()
            partnership=Partnership(
                inning_id=ball.inning_id,
                batsman1_id=ball.batsman_id,
                batsman2_id=ball.non_striker_id,
                wickets_fallen=wickets_fallen,
                runs_scored=0,
                balls_faced=0,
                is_active=True,
            )
            db.session.add(partnership)
        # Defensive defaults for nullable legacy rows
        partnership.runs_scored = partnership.runs_scored or 0
        partnership.balls_faced = partnership.balls_faced or 0
        partnership.wickets_fallen = partnership.wickets_fallen or 0
        partnership.runs_scored+=(ball.runs_scored+ball.extra_runs)
        if ball.is_legal_delivery:
            partnership.balls_faced+=1
        if ball.is_wicket:
            partnership.is_active=False
    
    @staticmethod
    def _update_innings(ball):
        innings=Inning.query.get(ball.inning_id)
        innings.total_runs+=(ball.runs_scored+ball.extra_runs)
        innings.extras+=ball.extra_runs
        if ball.is_wicket:
            innings.total_wickets+=1
        if ball.is_legal_delivery:
            total_balls=Ball.query.filter_by(inning_id=ball.inning_id,is_legal_delivery=True).count()
            innings.total_overs=total_balls//6 +(total_balls%6)/10
        match=innings.match
        if innings.total_wickets>=10:
            innings.is_completed=True
        elif match.over_limit is not None and innings.total_overs>=match.over_limit:
            innings.is_completed=True
        elif innings.target is not None and innings.total_runs>=innings.target:
            innings.is_completed=True
    @staticmethod
    def _handle_wicket(ball):
        """Handle wicket-specific logic"""
        # Partnership already ended in _update_partnership
        # Next batsman will come in - handled by frontend/next ball
        pass
    @staticmethod
    def get_current_batsmen(innings_id):
        last_ball=Ball.query.filter_by(inning_id=innings_id).order_by(Ball.id.desc()).first()
        if not last_ball:
            return None,None
        return last_ball.batsman_id,last_ball.non_striker_id
    @staticmethod
    def get_over_summary(innings_id,over_number):
        balls=Ball.query.filter_by(inning_id=innings_id,over_number=over_number).order_by(Ball.ball_number).all()
        return {
            'over_number':over_number+1,
            'balls':[ball.to_dict() for ball in balls],
            'total_runs':sum(ball.runs_scored+ball.extra_runs for ball in balls),
            'is_complete':len(balls)==6 or any(ball.is_wicket for ball in balls),
            'wickets':sum(1 for ball in balls if ball.is_wicket)
        }
    
