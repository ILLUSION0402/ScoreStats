from marshmallow import Schema, fields, ValidationError, validates, validate
class TeamCreateSchema(Schema):
    '''
    Validates team creation input
    
    '''
    name=fields.Str(required=True,validate=validate.Length(min=3),error_messages={'required':"Team name is required","validator_failed":"Team_name must have atleast 3 characters"})
    short_name=fields.Str(required=True,validate=validate.Length(max=10),error_messages={'required':"short name is required","validator_failed":"Short name must have atmost 10 characters"})
    logo_url=fields.Url(required=False,allow_none=True)
    @validates('short_name')
    def validated_short_name(self, value, **kwargs):
        '''
        short name should be in upper case
        '''
        if not value.isupper():
            raise ValidationError("short name should be in upper case")
class TeamUpdateSchema(Schema):
    '''
    Validate team updates input(all fields optional)
    '''
    name =fields.Str(required=False)
    short_name=fields.Str(required=False)
    logo_url=fields.Url(required=False,allow_none=True)
    
    
