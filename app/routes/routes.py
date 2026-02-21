from flask import Blueprint, render_template,request,jsonify
from models import Match, Innings, Ball,Team
from extensions import db
from services import *
main= Blueprint("main",__name__)
@main.route("/create_match",methods=["POST"])
def create_match():
    data= request.get_json()
    team1= data.get("team1")
    team2= data.get("team2")
    over_limit= data.get("over_limit",20)
    match= Match(team1= team1, team2= team2, over_limit=over_limit)
    db.session.add(match)
    db.session.commit()
    return jsonify({"message":"Match created successfully","match_id": match.id}),201
@main.route("/start_inning/<int:match_id>",methods=["POST"])
def start_inning(match_id):
    data= request.get_json()
    batting_team= data.get("batting_team")
    bowling_team= data.get("bowling_team")
    innings_number= data.get("innings_number",1)
    inning_obj= Innings(match_id= match_id, batting_team= batting_team, bowling_team= bowling_team, innings_number= innings_number)
    existing = Innings.query.filter_by(match_id=match_id,innings_number=innings_number).first()
    if existing:
        return jsonify({"message": "Inning already exists"}), 400
    db.session.add(inning_obj)
    db.session.commit()
    return jsonify({"message":"Inning started successfully","inning_id": inning_obj.id}),201
@main.route("/api/record_ball",methods=["POST"])
def api_record_ball():
    data= request.get_json()
    new_ball= record_ball(data)
    return jsonify({"message":"Ball recorded successfully","ball_id": new_ball.id}),201
@main.route("/match/<int:match_id>/summary",methods=["GET"])
def get_match_summary(match_id):
    balls = Ball.query.join(Innings).filter(
        Innings.match_id == match_id
    ).all()
    total_runs = sum(ball.runs + ball.extras for ball in balls)
    total_wickets = sum(1 for ball in balls if ball.is_wicket)
    if balls:
        last_ball = max(balls, key=lambda b: (b.over, b.balls))
        overs = f"{last_ball.over}.{last_ball.balls}"
    else:
        overs = "0.0"

    return jsonify({
        "match_id": match_id,
        "total_runs": total_runs,
        "total_wickets": total_wickets,
        "overs": overs
    }),200
@main.route("/")
def home():
    teams=Team.query.all()
    matches= Match.query.all()
    return render_template("home.html",teams= teams,matches= matches)
@main.route("/match/<int:match_id>")
def score_match(match_id):
    match= Match.query.get(match_id)
    innings= Innings.query.filter_by(match_id= match_id).all()
    balls= Ball.query.join(Innings).filter(Innings.match_id== match_id).all()
    return render_template("match.html",match= match,innings= innings,balls= balls)
@main.route("/stats/<int:player_id>")
def player_stats(player_id):
   stats=get_batting_stats(player_id)
   consistency= get_consistency_stats(player_id)
   recent=get_recent_form(player_id)
   return render_template("player_stats.html",stats= stats,consistency= consistency,recent= recent,player_id= player_id)
@main.route("/predict_winner/<int:team_a>/<int:team_b>")
def predict_winner(team_a,team_b):
    prediction= predict_match(team_a,team_b)
    if prediction is None:
        return render_template("prediction.html", error="Prediction could not be made due to insufficient data."), 400
    return render_template("prediction.html",prediction= prediction)
