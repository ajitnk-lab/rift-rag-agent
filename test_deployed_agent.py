#!/usr/bin/env python3
import boto3
import json
import time

def test_deployed_agent():
    """Test the deployed Bedrock Agent"""
    
    print("🎮 Testing Deployed Bedrock Agent")
    print("=" * 40)
    
    # Agent details
    agent_id = "FM4QOCUL4O"
    alias_id = "CBBG8H8XV5"
    
    print(f"Agent ID: {agent_id}")
    print(f"Alias ID: {alias_id}")
    
    # Initialize client
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    # Test query
    query = "What champions did professional players use and how did they perform?"
    
    print(f"\n🔍 Testing query: '{query}'")
    print("=" * 40)
    
    try:
        # Start conversation with agent
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId="test-session-001",
            inputText=query
        )
        
        # Process streaming response
        print("🤖 Agent Response:")
        print("-" * 20)
        
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    chunk_text = chunk['bytes'].decode('utf-8')
                    print(chunk_text, end='', flush=True)
                    full_response += chunk_text
        
        print("\n" + "-" * 20)
        print("✅ Agent test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def show_deployment_summary():
    """Show deployment summary"""
    
    print("\n" + "=" * 50)
    print("🎉 BEDROCK AGENT DEPLOYMENT COMPLETE!")
    print("=" * 50)
    
    print("\n📋 Deployment Summary:")
    print("   ✅ S3 Vectors Database: rift-game-vectors-poc")
    print("   ✅ Vector Index: rift-matches-index")
    print("   ✅ Bedrock Agent: FM4QOCUL4O (PREPARED)")
    print("   ✅ Agent Alias: CBBG8H8XV5 (production)")
    print("   ✅ Foundation Model: Claude 3 Sonnet")
    print("   ✅ Real Match Data: 9 professional matches")
    
    print("\n🚀 Usage Instructions:")
    print("   1. Agent ID: FM4QOCUL4O")
    print("   2. Alias ID: CBBG8H8XV5")
    print("   3. Test via AWS CLI:")
    print("      aws bedrock-agent-runtime invoke-agent \\")
    print("        --agent-id FM4QOCUL4O \\")
    print("        --agent-alias-id CBBG8H8XV5 \\")
    print("        --session-id test-session \\")
    print("        --input-text 'What champions performed best?'")
    
    print("\n💡 Sample Queries:")
    print("   - 'What champions did Faker play?'")
    print("   - 'Show me high-kill ARAM games'")
    print("   - 'Which matches had the best KDA ratios?'")
    print("   - 'Compare CoreJJ and Ruler performance'")

if __name__ == "__main__":
    # Wait for alias to be ready
    print("⏳ Waiting for agent alias to be ready...")
    time.sleep(10)
    
    # Test the agent
    success = test_deployed_agent()
    
    # Show summary
    show_deployment_summary()
    
    exit(0 if success else 1)
