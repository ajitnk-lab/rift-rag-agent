#!/usr/bin/env python3
import boto3
import json

def validate_bedrock_integration():
    """Validate Bedrock Agent integration readiness"""
    
    print("🚀 Validating Bedrock Agent Integration Readiness")
    print("=" * 55)
    
    # 1. Verify S3 Vectors database
    print("\n1. Checking S3 Vectors database...")
    try:
        s3vectors = boto3.client('s3vectors', region_name='us-east-1')
        
        # List buckets
        buckets_response = s3vectors.list_vector_buckets()
        buckets = buckets_response.get('vectorBuckets', [])
        
        rift_bucket = None
        for bucket in buckets:
            if bucket['vectorBucketName'] == 'rift-game-vectors-poc':
                rift_bucket = bucket
                break
        
        if rift_bucket:
            print(f"✅ S3 Vectors bucket found: {rift_bucket['vectorBucketName']}")
            print(f"   Created: {rift_bucket['creationTime']}")
        else:
            print("❌ S3 Vectors bucket 'rift-game-vectors-poc' not found")
            return False
            
    except Exception as e:
        print(f"❌ S3 Vectors check failed: {e}")
        return False
    
    # 2. Test vector query capability
    print("\n2. Testing vector query capability...")
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test a simple query
        query = "Faker performance"
        print(f"   Testing query: '{query}'")
        
        # Generate embedding
        embedding_response = bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps({"inputText": query})
        )
        query_embedding = json.loads(embedding_response['body'].read())['embedding']
        
        # Query vectors
        response = s3vectors.query_vectors(
            vectorBucketName="rift-game-vectors-poc",
            indexName="rift-matches-index",
            queryVector={"float32": query_embedding},
            topK=1,
            returnMetadata=True
        )
        
        results = response.get('vectors', [])
        if results:
            print(f"✅ Vector queries working correctly")
            print(f"   Found {len(results)} results")
            match = results[0]
            metadata = match.get('metadata', {})
            print(f"   Sample result: {metadata.get('summoner', 'N/A')} - {metadata.get('champion', 'N/A')}")
        else:
            print("❌ No results returned from vector query")
            return False
            
    except Exception as e:
        print(f"❌ Vector query test failed: {e}")
        return False
    
    # 3. Check Bedrock service availability
    print("\n3. Checking Bedrock service availability...")
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        # List foundation models
        models_response = bedrock.list_foundation_models()
        models = models_response.get('modelSummaries', [])
        
        # Find Claude models
        claude_models = [m for m in models if 'claude' in m.get('modelId', '').lower()]
        titan_models = [m for m in models if 'titan' in m.get('modelId', '').lower()]
        
        print(f"✅ Bedrock service accessible")
        print(f"   Claude models available: {len(claude_models)}")
        print(f"   Titan models available: {len(titan_models)}")
        
        if claude_models:
            print(f"   Recommended model: {claude_models[0]['modelId']}")
        
    except Exception as e:
        print(f"❌ Bedrock service check failed: {e}")
        return False
    
    # 4. Check Bedrock Agent service
    print("\n4. Checking Bedrock Agent service...")
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
        
        # Try to list agents (may be empty)
        agents_response = bedrock_agent.list_agents()
        agents = agents_response.get('agentSummaries', [])
        
        print(f"✅ Bedrock Agent service accessible")
        print(f"   Existing agents: {len(agents)}")
        
    except Exception as e:
        print(f"❌ Bedrock Agent service check failed: {e}")
        return False
    
    # 5. Summary
    print("\n" + "=" * 55)
    print("🎉 VALIDATION SUCCESSFUL!")
    print("\n📋 Integration Status:")
    print("   ✅ S3 Vectors database operational")
    print("   ✅ Real match data accessible via semantic search")
    print("   ✅ Bedrock foundation models available")
    print("   ✅ Bedrock Agent service ready")
    
    print("\n🚀 Next Steps:")
    print("   1. Deploy Bedrock Agent with Knowledge Base")
    print("   2. Configure agent to use S3 Vectors data")
    print("   3. Test end-to-end agent conversations")
    
    return True

if __name__ == "__main__":
    success = validate_bedrock_integration()
    exit(0 if success else 1)
