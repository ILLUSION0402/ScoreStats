# test_api.py

import requests 
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_create_team():
    """Test creating a team"""
    response = requests.post(f"{BASE_URL}/teams", json={
        "name": "Mumbai Indians",
        "short_name": "MI",
        "home_ground": "Wankhede Stadium"
    })
    
    print("Create Team:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()['team']['id']

def test_create_player(team_id):
    """Test creating a player"""
    response = requests.post(f"{BASE_URL}/players", json={
        "name": "Virat Kohli",
        "team_id": team_id,
        "role": "batsman",
        "batting_style": "right-hand",
        "jersey_number": 18
    })
    
    print("\nCreate Player:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()['player']['id']

def test_create_match(team1_id, team2_id):
    """Test creating a match"""
    response = requests.post(f"{BASE_URL}/matches", json={
        "team1_id": team1_id,
        "team2_id": team2_id,
    })
    
    print("\nCreate Match:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()['match']['id']

def test_record_toss(match_id, team_id):
    """Test recording toss"""
    response = requests.post(f"{BASE_URL}/matches/{match_id}/toss", json={
        "toss_winner_id": team_id,
        "toss_decision": "bat"
    })
    
    print("\nRecord Toss:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_start_innings(match_id, team1_id, team2_id):
    """Test starting innings"""
    response = requests.post(f"{BASE_URL}/balls/innings/start", json={
        "match_id": match_id,
        "batting_team_id": team1_id,
        "bowling_team_id": team2_id,
        "innings_number": 1
    })
    
    print("\nStart Innings:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()['innings']['id']

def test_record_ball(innings_id, striker_id, non_striker_id, bowler_id):
    """Test recording a ball"""
    response = requests.post(f"{BASE_URL}/balls/record", json={
        "innings_id": innings_id,
        "striker_id": striker_id,
        "non_striker_id": non_striker_id,
        "bowler_id": bowler_id,
        "runs": 4
    })
    
    print("\nRecord Ball:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_validation_errors():
    """Test validation errors"""
    print("\n=== Testing Validation Errors ===")
    
    # Invalid team name (too short)
    response = requests.post(f"{BASE_URL}/teams", json={
        "name": "MI",  # Too short
        "short_name": "MI"
    })
    print("\nInvalid Team Name:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    
    # Invalid runs value
    response = requests.post(f"{BASE_URL}/balls/record", json={
        "innings_id": 1,
        "striker_id": 1,
        "non_striker_id": 2,
        "bowler_id": 3,
        "runs": 10  # Invalid - max is 7
    })
    print("\nInvalid Runs:", response.status_code)
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    print("=== Cricket API Tests ===\n")
    
    # Test flow
    team1_id = test_create_team()
    
    # Create second team
    response = requests.post(f"{BASE_URL}/teams", json={
        "name": "Chennai Super Kings",
        "short_name": "CSK"
    })
    team2_id = response.json()['team']['id']
    
    # Create players
    player1_id = test_create_player(team1_id)
    
    response = requests.post(f"{BASE_URL}/players", json={
        "name": "Rohit Sharma",
        "team_id": team1_id,
        "role": "batsman"
    })
    player2_id = response.json()['player']['id']
    
    response = requests.post(f"{BASE_URL}/players", json={
        "name": "Jasprit Bumrah",
        "team_id": team2_id,
        "role": "bowler"
    })
    bowler_id = response.json()['player']['id']
    
    # Create match and test flow
    match_id = test_create_match(team1_id, team2_id)
    test_record_toss(match_id, team1_id)
    innings_id = test_start_innings(match_id, team1_id, team2_id)
    test_record_ball(innings_id, player1_id, player2_id, bowler_id)
    
    # Test validation
    test_validation_errors()
    
    print("\n=== All Tests Complete ===")