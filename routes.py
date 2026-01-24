from flask import Blueprint, render_template,request,jsonify
from models import Match, Innings, Ball
from extensions import db
from services import record_ball
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
    total_wickets = sum(ball.wickets for ball in balls)
    overs=max(ball.over for ball in balls) if balls else 0
    return jsonify({
        "match_id": match_id,
        "total_runs": total_runs,
        "total_wickets": total_wickets,
        "overs": overs
    }),200
