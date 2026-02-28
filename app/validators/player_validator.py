from marshmallow import Schema,fields,validates,ValidationError
from datetime import date
class PlayerCreateSchema(Schema):
    """Validate player creation input"""
    name=fields.Str(required=True,validate=lambda x:len(x)>=2,error_messages={'required':"Player name is required","validator_failed":"Team_name must have atleast 2 characters"})
    team_id=fields.Int(required=True,error_messages={"required":"Team ID is required"})
    role=fields.Str(required=False,validate=lambda x: x in ["batsman","bowler","all-rounder","wicket-keeper"],error_messages={"validation_failed":"Roles must be in batsman,bolwer,all-rounder,wicket keeper"})
    batting_style=fields.Str(required=False,validate=lambda x :x in ['right-hand','left-hand'])
    bowling_style=fields.Str(required=False,validate=lambda x: x in ['fast','medium','spin','leg-spin','off-spin'])
    jersey_number=fields.Int(required=False,validate=lambda x: x>=0,error_messages={"validation_failed":"jersey number must be greater than 0"})
class PlayerUpdateSchema(Schema):
    """Validate player update (all fields optional)"""
    name = fields.Str(required=False)
    team_id = fields.Int(required=False)
    role = fields.Str(required=False)
    batting_style = fields.Str(required=False)
    bowling_style = fields.Str(required=False)
    jersey_number = fields.Int(required=False)
    is_active = fields.Bool(required=False)