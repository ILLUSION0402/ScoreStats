from app.extensions import db
class Partnership(db.Model):
    """
    Represent a partnership between two batsmen in an innings.
    Tracks runs scored, balls faced, and wickets fallen during the partnership.
    """
    __tablename__='partnership'
    id=db.Column(db.Integer,primary_key=True)
    inning_id=db.Column(db.Integer,db.ForeignKey('inning.id'),nullable=False,comment="Inning ID")
    batsman1_id=db.Column(db.Integer,db.ForeignKey('player.id'),nullable=False,comment="First Batsman ID")
    batsman2_id=db.Column(db.Integer,db.ForeignKey('player.id'),nullable=False,comment="Second Batsman ID")
    runs_scored=db.Column(db.Integer,default=0,nullable=False,comment="Runs scored in the partnership")
    balls_faced=db.Column(db.Integer,default=0,nullable=False,comment="Balls faced in the partnership")
    wickets_fallen=db.Column(db.Integer,default=0,nullable=False,comment="Wickets fallen in the partnership")
    is_active=db.Column(db.Boolean,default=True,nullable=False,comment="Is the partnership currently active")
    def __repr__(self):
        return f"<Partnership Inning:{self.inning_id} Batsmen:{self.batsman1_id},{self.batsman2_id} Runs:{self.runs_scored} Wickets:{self.wickets_fallen}>"
    def to_dict(self):
        """Convert Partnership object to dictionary"""
        return {
            'id':self.id,
            'inning_id':self.inning_id,
            'batsman1_id':self.batsman1_id,
            'batsman2_id':self.batsman2_id,
            'runs_scored':self.runs_scored,
            'balls_faced':self.balls_faced,
            'wickets_fallen':self.wickets_fallen,
            'is_active':self.is_active
        }
    @property
    def run_rate(self):
        """Calculate and return the run rate for the partnership"""
        if self.balls_faced > 0:
            overs=self.balls_faced / 6
            return round(self.runs_scored / overs, 2) if overs > 0 else 0.0
        return 0.0