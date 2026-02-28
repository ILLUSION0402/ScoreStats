from app import create_app
from app.extensions import db
from app.models import Team,Player,Match,Inning,Ball,Partnership,BattingScorecard,BowlingScorecard
from sqlalchemy import inspect
app=create_app("development")
with app.app_context():
    db.create_all()
    print(" tables in database:")
    print(inspect(db.engine).get_table_names())