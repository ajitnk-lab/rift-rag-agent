#!/usr/bin/env python3
import requests
import json

# API Gateway endpoint from your deployed stack
API_ENDPOINT = "https://8bivbq3t6f.execute-api.us-east-1.amazonaws.com/prod/"

def test_agent_query(query):
    """Test the Bedrock Agent with a specific query"""
    payload = {
        "query": query,
        "sessionId": "test-rag-session-1"
    }
    
    try:
        print(f"🔍 Testing query: {query}")
        print("=" * 50)
        
        response = requests.post(API_ENDPOINT, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50 + "\n")

def main():
    """Run multiple test queries to verify RAG functionality"""
    
    test_queries = [
        "What champions have been played recently and what were their KDA ratios?",
        "Show me match data for any Korean players",
        "What game modes have been played?",
        "Tell me about the longest match duration",
        "Which champions had the highest damage output?"
    ]
    
    print("🚀 Testing Bedrock Agent RAG functionality")
    print("📊 Knowledge Base: League of Legends match data")
    print("🔗 S3 Vectors Index: rift-matches-index")
    print("\n")
    
    for query in test_queries:
        test_agent_query(query)

if __name__ == "__main__":
    main()
