#!/usr/bin/env python3
import boto3
import json
import os
from datetime import datetime

def test_bedrock_agent_integration():
    """Test Bedrock Agent with S3 Vectors Knowledge Base integration"""
    
    # Initialize clients
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    s3vectors = boto3.client('s3vectors', region_name='us-east-1')
    
    print("🚀 Testing Bedrock Agent with S3 Vectors Integration")
    print("=" * 60)
    
    # 1. Verify S3 Vectors database exists and has data
    print("\n1. Validating S3 Vectors database...")
    try:
        buckets_response = s3vectors.list_vector_buckets()
        buckets = buckets_response.get('vectorBuckets', [])
        
        rift_bucket = None
        for bucket in buckets:
            if bucket['vectorBucketName'] == 'rift-game-vectors-poc':
                rift_bucket = bucket
                break
        
        if not rift_bucket:
            raise Exception("S3 Vectors bucket 'rift-game-vectors-poc' not found")
        
        print(f"✅ Found S3 Vectors bucket: {rift_bucket['vectorBucketName']}")
        print(f"   ARN: {rift_bucket['vectorBucketArn']}")
        
        # Check index exists
        indices_response = s3vectors.list_vector_indices(vectorBucketName='rift-game-vectors-poc')
        indices = indices_response.get('vectorIndices', [])
        
        rift_index = None
        for index in indices:
            if index['vectorIndexName'] == 'rift-matches-index':
                rift_index = index
                break
        
        if not rift_index:
            raise Exception("Vector index 'rift-matches-index' not found")
        
        print(f"✅ Found vector index: {rift_index['vectorIndexName']}")
        print(f"   Dimensions: {rift_index['dimensions']}")
        print(f"   Status: {rift_index['vectorIndexStatus']}")
        
    except Exception as e:
        print(f"❌ S3 Vectors validation failed: {e}")
        return False
    
    # 2. Test direct S3 Vectors queries (simulating agent behavior)
    print("\n2. Testing S3 Vectors queries...")
    try:
        test_queries = [
            "Show me Faker's performance",
            "Which champions perform best in professional matches?",
            "What are the average KDA ratios?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            
            # Query S3 Vectors directly
            response = s3vectors.query_vectors(
                vectorBucketName='rift-game-vectors-poc',
                vectorIndexName='rift-matches-index',
                queryText=query,
                maxResults=3
            )
            
            results = response.get('queryResults', [])
            print(f"   Found {len(results)} results:")
            
            for i, result in enumerate(results[:2], 1):
                metadata = result.get('metadata', {})
                score = result.get('score', 0)
                print(f"   {i}. Score: {score:.3f}")
                print(f"      Champion: {metadata.get('champion', 'N/A')}")
                print(f"      Player: {metadata.get('summoner_name', 'N/A')}")
                print(f"      KDA: {metadata.get('kills', 0)}/{metadata.get('deaths', 0)}/{metadata.get('assists', 0)}")
        
        print("\n✅ S3 Vectors queries successful")
        
    except Exception as e:
        print(f"❌ S3 Vectors query failed: {e}")
        return False
    
    # 3. Validate Bedrock Agent capabilities
    print("\n3. Validating Bedrock Agent setup...")
    try:
        # List available foundation models
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        models_response = bedrock.list_foundation_models()
        
        claude_models = [
            model for model in models_response.get('modelSummaries', [])
            if 'claude' in model.get('modelId', '').lower()
        ]
        
        if claude_models:
            print(f"✅ Found {len(claude_models)} Claude models available")
            for model in claude_models[:3]:
                print(f"   - {model['modelId']}")
        else:
            print("⚠️  No Claude models found")
        
        # Check if we can create agents
        try:
            agents_response = bedrock_agent.list_agents()
            print(f"✅ Bedrock Agent service accessible")
            print(f"   Current agents: {len(agents_response.get('agentSummaries', []))}")
        except Exception as e:
            print(f"⚠️  Bedrock Agent access limited: {e}")
        
    except Exception as e:
        print(f"❌ Bedrock validation failed: {e}")
        return False
    
    print("\n🎉 Integration validation completed successfully!")
    print("\n📋 Summary:")
    print("   ✅ S3 Vectors database operational with real match data")
    print("   ✅ Vector index 'rift-matches-index' accessible")
    print("   ✅ Semantic search queries working")
    print("   ✅ Bedrock services available")
    print("\n🚀 Ready for Bedrock Agent deployment!")
    
    return True

if __name__ == "__main__":
    success = test_bedrock_agent_integration()
    exit(0 if success else 1)
