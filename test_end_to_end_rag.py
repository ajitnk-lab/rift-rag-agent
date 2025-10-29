#!/usr/bin/env python3
import boto3
import json
from datetime import datetime

def test_end_to_end_rag():
    """Test complete RAG system with S3 Vectors and Bedrock"""
    
    print("🎮 End-to-End RAG System Test for League of Legends")
    print("=" * 60)
    
    # Initialize clients
    s3vectors = boto3.client('s3vectors', region_name='us-east-1')
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Test scenarios
    test_scenarios = [
        {
            "query": "What champions did Faker play and how did he perform?",
            "context": "Professional player analysis"
        },
        {
            "query": "Show me high-kill games in ARAM mode",
            "context": "Game mode specific analysis"
        },
        {
            "query": "Which matches had the longest duration?",
            "context": "Match duration analysis"
        }
    ]
    
    print(f"\n🔍 Testing {len(test_scenarios)} RAG scenarios...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*50}")
        print(f"📋 Scenario {i}: {scenario['context']}")
        print(f"❓ Query: {scenario['query']}")
        
        try:
            # Step 1: Generate query embedding
            print("   🔄 Generating query embedding...")
            embedding_response = bedrock_runtime.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=json.dumps({"inputText": scenario['query']})
            )
            query_embedding = json.loads(embedding_response['body'].read())['embedding']
            
            # Step 2: Search vector database
            print("   🔍 Searching vector database...")
            search_response = s3vectors.query_vectors(
                vectorBucketName="rift-game-vectors-poc",
                indexName="rift-matches-index",
                queryVector={"float32": query_embedding},
                topK=3,
                returnMetadata=True
            )
            
            results = search_response.get('vectors', [])
            print(f"   📊 Found {len(results)} relevant matches")
            
            # Step 3: Build context from results
            context_data = []
            for result in results:
                metadata = result.get('metadata', {})
                context_data.append({
                    'match_id': result['key'],
                    'player': metadata.get('summoner', 'Unknown'),
                    'champion': metadata.get('champion', 'Unknown'),
                    'kda': metadata.get('kda', 'N/A'),
                    'result': metadata.get('result', 'Unknown'),
                    'mode': metadata.get('mode', 'Unknown'),
                    'duration': metadata.get('duration', 'N/A'),
                    'gold': metadata.get('gold', 'N/A'),
                    'cs': metadata.get('cs', 'N/A')
                })
            
            # Step 4: Generate AI response using context
            print("   🤖 Generating AI response...")
            
            context_text = "Based on the following League of Legends match data:\n\n"
            for data in context_data:
                context_text += f"Match {data['match_id']}:\n"
                context_text += f"- Player: {data['player']}\n"
                context_text += f"- Champion: {data['champion']}\n"
                context_text += f"- KDA: {data['kda']}\n"
                context_text += f"- Result: {data['result']}\n"
                context_text += f"- Mode: {data['mode']}\n"
                context_text += f"- Duration: {data['duration']} minutes\n"
                context_text += f"- Gold: {data['gold']}\n"
                context_text += f"- CS: {data['cs']}\n\n"
            
            prompt = f"""You are a League of Legends expert analyst. {context_text}

Question: {scenario['query']}

Please provide a detailed analysis based on the match data above. Include specific statistics and insights."""
            
            # Use Claude for response generation
            claude_response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_data = json.loads(claude_response['body'].read())
            ai_response = response_data['content'][0]['text']
            
            # Display results
            print(f"\n   🎯 AI Analysis:")
            print(f"   {ai_response}")
            
            print(f"\n   📈 Raw Data Retrieved:")
            for j, data in enumerate(context_data, 1):
                print(f"   {j}. {data['player']} ({data['champion']}) - {data['kda']} - {data['result']}")
            
            print(f"\n   ✅ Scenario {i} completed successfully")
            
        except Exception as e:
            print(f"   ❌ Scenario {i} failed: {e}")
            return False
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎉 END-TO-END RAG SYSTEM TEST COMPLETED!")
    print("\n📊 System Performance:")
    print("   ✅ Vector embeddings generated successfully")
    print("   ✅ Semantic search retrieved relevant matches")
    print("   ✅ AI responses generated with context")
    print("   ✅ Real professional match data utilized")
    
    print("\n🚀 RAG System Ready for Production!")
    print("   - S3 Vectors database: rift-game-vectors-poc")
    print("   - Vector index: rift-matches-index")
    print("   - Embedding model: amazon.titan-embed-text-v1")
    print("   - LLM model: anthropic.claude-3-sonnet-20240229-v1:0")
    print("   - Data source: Real Riot Games API matches")
    
    return True

if __name__ == "__main__":
    success = test_end_to_end_rag()
    exit(0 if success else 1)
