from datetime import datetime
from app.extensions import db
class Ball(db.Model):
    """
    Docstring for Ball
    """
    __tablename__='ball'
    id=db.Column(db.Integer,primary_key=True)
    inning_id=db.Column(db.Integer,db.ForeignKey('inning.id'),nullable=False,comment="Inning ID")
    over_number=db.Column(db.Integer,nullable=False,comment="Over Number") 
    ball_number=db.Column(db.Integer,nullable=False,comment="Ball Number within the over (1-6)")
    batsman_id=db.Column(db.Integer,db.ForeignKey('player.id'),nullable=False,comment="Batsman on strike")
    non_striker_id=db.Column(db.Integer,db.ForeignKey('player.id'),nullable=False,comment="Non-striker Batsman")
    bowler_id=db.Column(db.Integer,db.ForeignKey('player.id'),nullable=False,comment="Bowler delivering the ball")
    runs_scored=db.Column(db.Integer,default=0,nullable=False,comment="Runs scored on this ball")
    is_wicket=db.Column(db.Boolean,default=False,nullable=False,comment="Whether a wicket fell on this ball")
    wicket_type=db.Column(db.String(50),comment="Type of Wicket (bowled, caught, run out, etc.)")
    extra_type=db.Column(db.String(50),comment="Type of Extra (wide, no ball, bye, leg bye)")
    extra_runs=db.Column(db.Integer,default=0,nullable=False,comment="Extra runs awarded on this ball")
    dismissed_player_id=db.Column(db.Integer,db.ForeignKey('player.id'),comment="Player ID of the dismissed batsman (if applicable)")
    fielder_id=db.Column(db.Integer,db.ForeignKey('player.id'),comment="Fielder involved in the dismissal (if applicable)")
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False,comment="Record Creation Timestamp")
    is_legal_delivery=db.Column(db.Boolean,default=True,nullable=False,comment="Whether the delivery is legal (not a wide or no ball)")
    __table_args__=(db.Index('idx_ball_inning_over_ball', 'inning_id','over_number','ball_number'),db.Index('idx_ball_batsman', 'batsman_id'),db.Index('idx_ball_bowler', 'bowler_id'))
    def __repr__(self):
        return f"<Ball Inning:{self.inning_id} Over:{self.over_number}.{self.ball_number} Runs:{self.runs_scored} Wicket:{self.is_wicket}>"
    def to_dict(self):
        """Convert Ball object to dictionary"""
        return {
            'id':self.id,
            'inning_id':self.inning_id,
            'over_number':self.over_number,
            'ball_number':self.ball_number,
            'batsman_id':self.batsman_id,
            'non_striker_id':self.non_striker_id,
            'bowler_id':self.bowler_id,
            'runs_scored':self.runs_scored,
            'is_wicket':self.is_wicket,
            'wicket_type':self.wicket_type,
            'extra_type':self.extra_type,
            'extra_runs':self.extra_runs,
            'dismissed_player_id':self.dismissed_player_id,
            'fielder_id':self.fielder_id,
            'is_legal_delivery':self.is_legal_delivery,
            'created_at':self.created_at.isoformat()
        }
    @property
    def total_runs(self):
        # Calculate total runs from runs scored and extras
        return self.runs_scored+self.extra_runs
    # Compatibility aliases for older codepaths
    @property
    def runs(self):
        return self.runs_scored
    @property
    def extras(self):
        return self.extra_runs
    @property
    def striker_id(self):
        return self.batsman_id
    @property
    def innings_id(self):
        return self.inning_id
    @property
    def over(self):
        return self.over_number
    @property
    def balls(self):
        return self.ball_number
    @property
    def over_display(self):
        return f"{self.over_number+1}.{self.ball_number}"
