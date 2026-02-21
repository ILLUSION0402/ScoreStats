from datetime import datetime
from app.extensions import db
class Inning(db.Model):
    """
    Represent one innings in a Match.
    Tracks which team is batting and bowling, runs scored, wickets fallen, and overs bowled.
    """
    __tablename__='inning'
    id=db.Column(db.Integer,primary_key=True)
    match_id=db.Column(db.Integer,db.ForeignKey('match.id'),nullable=False,comment="Match ID")
    batting_team_id=db.Column(db.Integer,db.ForeignKey('team.id'),nullable=False,comment="Batting Team ID")
    bowling_team_id=db.Column(db.Integer,db.ForeignKey('team.id'),nullable=False,comment="Bowling Team ID")
    innings_number=db.Column(db.Integer,nullable=False,comment="Innings Number (1,2,3,4)")
    is_completed=db.Column(db.Boolean,default=False,nullable=False,comment="Is Innings Completed")
    total_runs=db.Column(db.Integer,default=0,nullable=False,comment="Total Runs Scored")
    total_wickets=db.Column(db.Integer,default=0,nullable=False,comment="Total Wickets Fallen")
    total_overs=db.Column(db.Float,default=0.0,nullable=False,comment="Total Overs Bowled")
    extras=db.Column(db.Integer,default=0,nullable=False,comment="Total Extras Given")
    target=db.Column(db.Integer,comment="Target Runs for the Innings (if applicable)")
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False,comment="Record Creation Timestamp")
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,comment="Record Update Timestamp")
    # Relationships
    batting_team=db.relationship("Team",foreign_keys=[batting_team_id],backref="batting_innings",lazy='joined')
    batting_scorecards=db.relationship("BattingScorecard",backref="inning",lazy='dynamic',cascade='all,delete-orphan')
    bowling_scorecards=db.relationship("BowlingScorecard",backref="inning",lazy='dynamic',cascade='all,delete-orphan')
    partnerships=db.relationship("Partnership",backref="inning",lazy='dynamic',cascade='all,delete-orphan')
    balls=db.relationship("Ball",backref="inning",lazy='dynamic',cascade='all,delete-orphan',order_by='Ball.id')
    __table_args__=((db.UniqueConstraint('match_id','innings_number',name='uix_match_innings_number')),db.Index('idx_inning_match_id', 'match_id','batting_team_id'))
    def __repr__(self):
        return f"<Inning {self.innings_number} of Match {self.match_id}>"
    def to_dict(self):
        """Convert Inning object to dictionary"""
        return {
            'id':self.id,
            'match_id':self.match_id,
            'batting_team_id':self.batting_team_id,
            'bowling_team_id':self.bowling_team_id,
            'innings_number':self.innings_number,
            'is_completed':self.is_completed,
            'total_runs':self.total_runs,
            'total_wickets':self.total_wickets,
            'total_overs':self.total_overs,
            'extras':self.extras,
            'target':self.target,
            'created_at':self.created_at.isoformat(),
            'updated_at':self.updated_at.isoformat()
        }
    @property
    def run_rate(self):
        """Calculate and return the current run rate for the innings"""
        if self.total_overs > 0:
            return round(self.total_runs / self.total_overs, 2)
        return 0.0
    @property
    def required_run_rate(self):
        """Calculate and return the required run rate if target is set"""
        if self.target and self.total_overs > 0:
            runs_needed=self.target - self.total_runs
            overs_remaining=self.match.over_limit - self.total_overs
            if overs_remaining > 0:
                return round(runs_needed / overs_remaining, 2)
        return 0.0
    
