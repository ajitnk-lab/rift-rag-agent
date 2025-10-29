#!/usr/bin/env python3
import boto3
import requests
import json
import time

RIOT_API_KEY = "RGAPI-764e10c9-017d-42b2-bd85-3074f52daff2"

def delete_mock_data():
    """Delete all mock/sample data from S3 Vectors"""
    s3vectors = boto3.client('s3vectors', region_name='us-east-1')
    
    mock_keys = [
        "match_001",
        "match_002", 
        "NA1_sample_001",
        "NA1_sample_002"
    ]
    
    for key in mock_keys:
        try:
            s3vectors.delete_vectors(
                vectorBucketName="rift-game-vectors-poc",
                indexName="rift-matches-index",
                keys=[key]
            )
            print(f"🗑️ Deleted mock data: {key}")
        except Exception as e:
            print(f"❌ Error deleting {key}: {e}")

def get_account_by_riot_id(game_name, tag_line, region="americas"):
    """Get account info using Riot ID"""
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json(), region
    return None, None

def get_matches_for_player(account_data, region, count=5):
    """Get match data for a player"""
    s3vectors = boto3.client('s3vectors', region_name='us-east-1')
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    puuid = account_data['puuid']
    game_name = account_data['gameName']
    
    # Get match history
    matches_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    match_response = requests.get(matches_url, headers=headers)
    if match_response.status_code != 200:
        print(f"❌ Failed to get matches for {game_name}: {match_response.status_code}")
        return 0
        
    match_ids = match_response.json()
    stored_count = 0
    
    for match_id in match_ids:
        # Get match details
        match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        match_response = requests.get(match_url, headers=headers)
        
        if match_response.status_code != 200:
            continue
            
        match_data = match_response.json()
        info = match_data['info']
        
        # Find player's data
        player_data = None
        for participant in info['participants']:
            if participant['puuid'] == puuid:
                player_data = participant
                break
        
        if not player_data:
            continue
            
        # Create rich text summary
        champion = player_data['championName']
        position = player_data.get('teamPosition', 'Unknown')
        kda = f"{player_data['kills']}/{player_data['deaths']}/{player_data['assists']}"
        result = "Victory" if player_data['win'] else "Defeat"
        duration = info['gameDuration'] // 60
        
        # Get items
        items = [str(item) for item in [
            player_data.get('item0', 0), player_data.get('item1', 0), 
            player_data.get('item2', 0), player_data.get('item3', 0),
            player_data.get('item4', 0), player_data.get('item5', 0)
        ] if item > 0]
        
        # Rich text for embedding
        text = f"{info['gameMode']}, {duration} minutes, {champion} {position}, {kda} KDA, {result}, CS: {player_data.get('totalMinionsKilled', 0)}, Gold: {player_data.get('goldEarned', 0)}, Damage: {player_data.get('totalDamageDealtToChampions', 0)}"
        
        try:
            # Generate embedding
            embedding_response = bedrock.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=json.dumps({"inputText": text})
            )
            embedding = json.loads(embedding_response['body'].read())['embedding']
            
            # Store in S3 Vectors
            s3vectors.put_vectors(
                vectorBucketName="rift-game-vectors-poc",
                indexName="rift-matches-index",
                vectors=[{
                    "key": match_id,
                    "data": {"float32": embedding},
                    "metadata": {
                        "summoner": game_name,
                        "champion": champion,
                        "position": position,
                        "mode": info['gameMode'],
                        "duration": str(duration),
                        "result": result,
                        "kda": kda,
                        "cs": str(player_data.get('totalMinionsKilled', 0)),
                        "gold": str(player_data.get('goldEarned', 0))
                    }
                }]
            )
            print(f"✅ {game_name}: {champion} {position} ({result}) - {match_id}")
            stored_count += 1
            
        except Exception as e:
            print(f"❌ Error storing {match_id}: {e}")
        
        time.sleep(1.2)  # Rate limiting
    
    return stored_count

def populate_real_data():
    """Get real data from multiple players"""
    
    # Pro players and streamers with known Riot IDs
    players = [
        ("Doublelift", "NA1", "americas"),
        ("Bjergsen", "NA1", "americas"),
        ("CoreJJ", "NA1", "americas"),
        ("Jankos", "EUW", "europe"),
        ("Caps", "G2", "europe"),
        ("Rekkles", "EUW", "europe"),
        ("Canyon", "KR1", "asia"),
        ("ShowMaker", "KR1", "asia"),
        ("Keria", "KR1", "asia"),
        ("Ruler", "KR1", "asia")
    ]
    
    total_stored = 0
    successful_players = 0
    
    for game_name, tag_line, region in players:
        print(f"\n🔍 Trying: {game_name}#{tag_line}")
        
        account_data, found_region = get_account_by_riot_id(game_name, tag_line, region)
        
        if account_data:
            print(f"✅ Found: {account_data['gameName']}")
            stored = get_matches_for_player(account_data, found_region, count=3)
            total_stored += stored
            if stored > 0:
                successful_players += 1
        else:
            print(f"❌ Not found: {game_name}#{tag_line}")
        
        time.sleep(2)  # Rate limiting between players
    
    print(f"\n📊 Summary:")
    print(f"✅ Players found: {successful_players}")
    print(f"✅ Total matches stored: {total_stored}")

def main():
    print("🧹 Step 1: Cleaning mock data...")
    delete_mock_data()
    
    print("\n📥 Step 2: Fetching real data from multiple players...")
    populate_real_data()
    
    print("\n🎉 Done! Your vector database now contains only real match data.")

if __name__ == "__main__":
    main()
