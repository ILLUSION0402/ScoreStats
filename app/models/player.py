from datetime import datetime
from app.extensions import db
class Player(db.Model):
    """
    Represent the Player
    A player belongs to a team and participates in matches
    """
    __tablename__='player'
    id=db.Column(db.Integer,primary_key=True)
    # Info
    name=db.Column(db.String(100),nullable=False,index=True,comment="Full Player Name")
    jersey_number=db.Column(db.Integer,unique=True,nullable=False,comment="Jersey Number")
    role=db.Column(db.String(50),nullable=False,comment="Player Role (Batsman, Bowler, All-rounder, Wicketkeeper)")
    batting_style=db.Column(db.String(50),comment="Batting Style (Right-hand bat, Left-hand bat)")
    bowling_style=db.Column(db.String(50),comment="Bowling Style (Right-arm fast, Left-arm spin, etc.)")
    team_id=db.Column(db.Integer,db.ForeignKey('team.id',ondelete='CASCADE'),nullable=False,comment="Which Team the Player belongs to")
    is_active=db.Column(db.Boolean,default=True,nullable=False,comment="Is the Player currently active")
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False,comment="Record Creation Timestamp")
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,comment="Record Update Timestamp")
    def __repr__(self):
        return f"<Player {self.name} (Jersey: {self.jersey_number})>"
    def to_dict(self):
        """Convert Player object to dictionary"""
        return {
            'id':self.id,
            'name':self.name,
            'jersey_number':self.jersey_number,
            'role':self.role,
            'batting_style':self.batting_style,
            'bowling_style':self.bowling_style,
            'team_id':self.team_id,
            'created_at':self.created_at.isoformat(),
            'updated_at':self.updated_at.isoformat(),
            'is_active':self.is_active
        }