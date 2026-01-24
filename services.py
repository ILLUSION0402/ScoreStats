from models import Ball, Player
from extensions import db
def record_ball(data):
    print("Recording ball with data:", data)
    inning_id = data.get("inning_id")
    last_ball = Ball.query.filter_by(inning_id=inning_id).order_by(Ball.id.desc()).first()
    if not last_ball:
        over = 0
        balls = 1
        striker_id = data["striker_id"]
        non_striker_id = data["non_striker_id"]
    else:
        if last_ball.balls == 6:
            over = last_ball.over + 1
            balls = 1
            striker_id = last_ball.non_striker_id
            non_striker_id = last_ball.striker_id
        else:
            over = last_ball.over
            balls = last_ball.balls + 1
            striker_id = last_ball.striker_id
            non_striker_id = last_ball.non_striker_id
    runs = data.get("runs", 0)

    if runs % 2 == 1:
        striker_id, non_striker_id = non_striker_id, striker_id
    new_ball = Ball(
        inning_id=inning_id,
        over=over,
        balls=balls,
        striker_id=striker_id,
        non_striker_id=non_striker_id,
        bowler_id=data.get("bowler_id"),
        runs=data.get("runs", 0),
        is_wicket=data.get("is_wicket", False),
        extras=data.get("extras", 0),
        dismissed_player_id=data.get("dismissed_player_id")
    )
    db.session.add(new_ball)
    db.session.commit()
    return new_ball
def get_batting_stats(player_id):
    balls = Ball.query.filter_by( striker_id=player_id).all()
    runs = sum(ball.runs for ball in balls)
    balls_faced = len(balls)
    dismissals=Ball.query.filter_by(dismissed_player_id=player_id).count()
    fours = sum(1 for ball in balls if ball.runs == 4)
    sixes = sum(1 for ball in balls if ball.runs == 6)
    average = runs / dismissals if dismissals > 0 else runs
    strike_rate = (runs / balls_faced) * 100 if balls_faced > 0 else 0
    return {
        "runs": runs,
        "balls_faced": balls_faced,
        "fours": fours,
        "sixes": sixes,
        "average":round(average,2),
        "strike_rate": round(strike_rate,2)
    }
def get_batting_consistency_stats(player_id):
    innings = db.session.query(Ball.inning_id).filter((Ball.striker_id == player_id)).distinct().all()
    scores = []
    for (inning_id,) in innings:
        runs = db.session.query(db.func.sum(Ball.runs)).filter_by(inning_id=inning_id,striker_id=player_id).scalar() or 0
        scores.append(runs)
    if not scores:
        return {
            "mean": 0,
            "variance": 0,
            "standard_deviation": 0,
            "consistency": 0
        }   
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    standard_deviation = variance ** 0.5
    consistency=1/(1+variance)
    return {
        "mean": round(mean,2),
        "variance": round(variance,2),
        "standard_deviation": round(standard_deviation,2),
        "consistency": round(consistency,2)  

    }
def get_bowling_stats(player_id):
    balls = Ball.query.filter_by(bowler_id=player_id).all()
    runs_conceded = sum(ball.runs + ball.extras for ball in balls)
    wickets_taken = sum(1 for ball in balls if ball.is_wicket)
    overs_bowled = len(balls) // 6 +(len(balls) %6)/10
    average = runs_conceded / wickets_taken if wickets_taken > 0 else 0
    economy_rate = runs_conceded / overs_bowled if overs_bowled > 0 else 0
    strike_rate = len(balls) / wickets_taken if wickets_taken > 0 else 0
    return {
        "runs_conceded": runs_conceded,
        "wickets_taken": wickets_taken,
        "overs_bowled": overs_bowled,
        "average": round(average,2),
        "economy_rate": round(economy_rate,2),
        "strike_rate": round(strike_rate,2)
    }
def get_bowling_consistency_stats(player_id):
    innings = db.session.query(Ball.inning_id).filter((Ball.bowler_id == player_id)).distinct().all()
    wickets_list = []
    for (inning_id,) in innings:
        wickets = db.session.query(db.func.count(Ball.id)).filter(Ball.inning_id == inning_id,Ball.bowler_id == player_id,Ball.is_wicket == True).scalar() or 0
        wickets_list.append(wickets)
    if not wickets_list:
        return {
            "mean": 0,
            "variance": 0,
            "standard_deviation": 0,
            "consistency": 0
        }   
    mean = sum(wickets_list) / len(wickets_list)
    variance = sum((x - mean) ** 2 for x in wickets_list) / len(wickets_list)
    standard_deviation = variance ** 0.5
    consistency=1/(1+variance)
    return {
        "mean": round(mean,2),
        "variance": round(variance,2),
        "standard_deviation": round(standard_deviation,2),
        "consistency": round(consistency,2)
    }
def get_team_strength(team_id):
    players = db.session.query(Player).filter_by(team_id=team_id).all()
    batting_scores = []
    bowling_scores = []
    for player in players:
        batting_stats = get_batting_stats(player.id)
        bowling_stats = get_bowling_stats(player.id)
        batting_scores.append((batting_stats["average"] * batting_stats["strike_rate"])/100)
        bowling_scores.append(bowling_stats["wickets_taken"] /(bowling_stats["economy_rate"]+1) )
    batting_strength = sum(batting_scores) / len(players) if players else 0
    bowling_strength = sum(bowling_scores) / len(players) if players else 0
    team_strength=0.6*batting_strength +0.4*bowling_strength    
    return {
        "batting_strength": batting_strength,
        "bowling_strength": bowling_strength,
        "overall_strength": team_strength
    }
def get_consistency_stats(player_id):
    batting_consistency = get_batting_consistency_stats(player_id)
    bowling_consistency = get_bowling_consistency_stats(player_id)
    consistency=0.6*batting_consistency["consistency"] +0.4*bowling_consistency["consistency"]
    return {
        "batting_consistency": batting_consistency,
        "bowling_consistency": bowling_consistency,
        "consistency": consistency
    }
def get_team_features(team_id):
    players = Player.query.filter_by(team_id=team_id).all()

    batting_scores = []
    bowling_scores = []
    consistency_scores = []
    recent_forms = []

    for p in players:
        bat = get_batting_stats(p.id)
        bowl = get_bowling_stats(p.id)
        cons = get_consistency_stats(p.id)
        form = get_recent_form(p.id)

        batting_scores.append(bat["average"] * bat["strike_rate"])
        bowling_scores.append(
            bowl["wickets_taken"] / (bowl["economy_rate"] + 1)
            if bowl["economy_rate"] > 0 else 0
        )
        consistency_scores.append(cons["consistency"])
        recent_forms.append(form["recent_form"])

    # Raw aggregates
    batting_strength = sum(batting_scores) / len(batting_scores) if batting_scores else 0
    bowling_strength = sum(bowling_scores) / len(bowling_scores) if bowling_scores else 0
    consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
    recent_form = sum(recent_forms) / len(recent_forms) if recent_forms else 0

    # Normalize (simple max scaling)
    batting_norm = batting_strength / 100 if batting_strength > 0 else 0
    bowling_norm = bowling_strength / 10 if bowling_strength > 0 else 0
    consistency_norm = consistency  # already [0,1]
    recent_form_norm = recent_form / 50 if recent_form > 0 else 0

    return {
        "batting": round(min(batting_norm, 1), 3),
        "bowling": round(min(bowling_norm, 1), 3),
        "consistency": round(consistency_norm, 3),
        "recent_form": round(min(recent_form_norm, 1), 3)
    }

    
def get_recent_form(player_id, k=5):
    # Get innings in chronological order
    innings_ids = (
        db.session.query(Ball.inning_id)
        .filter(Ball.striker_id == player_id)
        .distinct()
        .order_by(Ball.inning_id)
        .all()
    )

    runs_per_innings = []

    for (inning_id,) in innings_ids:
        runs = (db.session.query(db.func.sum(Ball.runs)).filter(Ball.inning_id == inning_id,Ball.striker_id == player_id).scalar()) or 0
        runs_per_innings.append(runs)

    if not runs_per_innings:
        return {"recent_form": 0}

    # Take last k innings
    recent_runs = runs_per_innings[-k:]

    # Generate increasing weights (older → recent)
    n = len(recent_runs)
    weights = [(i + 1) for i in range(n)]
    weight_sum = sum(weights)

    weighted_form = sum(
        w * r for w, r in zip(weights, recent_runs)
    ) / weight_sum

    return {
        "recent_form": round(weighted_form, 2),
        "recent_innings": recent_runs
    }
def get_team_recent_form(team_id):
    players = Player.query.filter_by(team_id=team_id).all()

    forms = []
    for p in players:
        form = get_recent_form(p.id)
        forms.append(form["recent_form"])

    team_form = sum(forms) / len(forms) if forms else 0

    return {
        "team_recent_form": round(team_form, 2)
    }
def compute_team_score(team_id):
    f = get_team_features(team_id)

    score = (0.4 * f["batting"] + 0.3 * f["bowling"] + 0.2 * f["consistency"] + 0.1 * f["recent_form"])

    return {
        "team_id": team_id,
        "score": round(score, 4),
        "features": f
    }
def predict_match(team_a, team_b):
    A = compute_team_score(team_a)
    B = compute_team_score(team_b)

    SA = A["score"]
    SB = B["score"]

    if SA + SB == 0:
        return {
            "team_a_probability": 0.5,
            "team_b_probability": 0.5,
            "explanation": "Both teams have equal strength."
        }

    PA = SA / (SA + SB)
    PB = 1 - PA
    explanation = explain_prediction(team_a, team_b)

    return {
        "team_a": team_a,
        "team_b": team_b,
        "team_a_probability": round(PA, 4),
        "team_b_probability": round(PB, 4),
        "score_a": SA,
        "score_b": SB,
        "features_a": A["features"],
        "features_b": B["features"],
        "explanation": explanation
    }
def compare_features(features_a, features_b):
    diff = {}
    for key in features_a.keys():
        diff[key] = round(features_a[key] - features_b[key], 4)
    return diff
def get_dominant_factors(diff,top_n=3):
    sorted_factors = sorted(diff.items(), key=lambda x: abs(x[1]), reverse=True)
    dominant = sorted_factors[:top_n]
    return dominant
def explain_prediction(team_a, team_b):
    A = compute_team_score(team_a)
    B = compute_team_score(team_b)

    features_a = A["features"]
    features_b = B["features"]

    diffs = compare_features(features_a, features_b)
    dominant = get_dominant_factors(diffs)

    winner = team_a if A["score"] > B["score"] else team_b
    loser = team_b if winner == team_a else team_a

    lines = []

    for feature, diff in dominant:
        if diff > 0:
            lines.append(
                f"Team {team_a} has stronger {feature} (+{diff:.3f})"
            )
        else:
            lines.append(
                f"Team {team_b} has stronger {feature} (+{abs(diff):.3f})"
            )

    explanation = (
        f"Team {winner} is favored due to superior "
        + " and ".join(
            f.split("stronger ")[1].split(" ")[0]
            for f in lines
        )
        + "."
    )

    return {
        "team_a": team_a,
        "team_b": team_b,
        "winner": winner,
        "dominant_factors": dominant,
        "feature_differences": diffs,
        "explanation_lines": lines,
        "summary": explanation
    }

