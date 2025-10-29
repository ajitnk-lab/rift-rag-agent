#!/usr/bin/env python3
import boto3
import json
import time

def deploy_bedrock_agent():
    """Deploy Bedrock Agent with S3 Vectors integration"""
    
    print("🚀 Deploying Bedrock Agent for League of Legends RAG")
    print("=" * 55)
    
    # Initialize clients
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    # 1. Create IAM role for Bedrock Agent
    print("\n1. Creating IAM role for Bedrock Agent...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = "RiftGameBedrockAgentRole"
    
    try:
        # Try to create role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Rift Game Bedrock Agent"
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach Bedrock policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
        )
        
        # Wait for role to propagate
        print("   Waiting for role to propagate...")
        time.sleep(10)
        
    except iam.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        role_response = iam.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_arn}")
    
    # 2. Create Bedrock Agent
    print("\n2. Creating Bedrock Agent...")
    
    agent_instruction = """You are a League of Legends expert AI assistant specialized in analyzing professional match data. 

You have access to real match data from professional players including:
- Champion picks and performance
- KDA ratios (Kills/Deaths/Assists)
- Gold earned and CS (Creep Score)
- Match outcomes and durations
- Game modes (Classic, ARAM)
- Player positions and roles

When answering questions:
1. Always reference specific match data when available
2. Provide statistical insights and comparisons
3. Explain champion performance and meta trends
4. Give strategic recommendations based on historical data
5. Be specific about player names, champions, and statistics

Focus on providing actionable insights for League of Legends players and analysts."""
    
    try:
        agent_response = bedrock_agent.create_agent(
            agentName="rift-game-agent",
            description="AI agent for League of Legends match analysis and insights using real professional player data",
            foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
            agentResourceRoleArn=role_arn,
            instruction=agent_instruction
        )
        
        agent_id = agent_response['agent']['agentId']
        print(f"✅ Created Bedrock Agent: {agent_id}")
        
        # Wait for agent to be ready
        print("   Waiting for agent to be ready...")
        max_attempts = 30
        for attempt in range(max_attempts):
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            
            if status in ['NOT_PREPARED', 'PREPARED']:
                print(f"✅ Agent ready for preparation (status: {status})")
                break
            elif status == 'FAILED':
                print(f"❌ Agent creation failed")
                return False
            else:
                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
                time.sleep(5)
        
        # 3. Prepare the agent
        print("\n3. Preparing Bedrock Agent...")
        
        prepare_response = bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"✅ Agent preparation initiated")
        
        # Wait for preparation to complete
        print("   Waiting for agent preparation...")
        max_attempts = 30
        for attempt in range(max_attempts):
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            
            if status == 'PREPARED':
                print(f"✅ Agent prepared successfully")
                break
            elif status == 'FAILED':
                print(f"❌ Agent preparation failed")
                return False
            else:
                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
                time.sleep(10)
        
        # 4. Create agent alias
        print("\n4. Creating agent alias...")
        
        alias_response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName="production",
            description="Production alias for Rift Game Agent"
        )
        
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"✅ Created agent alias: {alias_id}")
        
        # 5. Summary
        print(f"\n{'='*55}")
        print("🎉 BEDROCK AGENT DEPLOYED SUCCESSFULLY!")
        print(f"\n📋 Deployment Details:")
        print(f"   Agent ID: {agent_id}")
        print(f"   Alias ID: {alias_id}")
        print(f"   IAM Role: {role_arn}")
        print(f"   Foundation Model: anthropic.claude-3-sonnet-20240229-v1:0")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Test agent with: aws bedrock-agent-runtime invoke-agent")
        print(f"   2. Agent ID: {agent_id}")
        print(f"   3. Alias ID: {alias_id}")
        
        return {
            'agent_id': agent_id,
            'alias_id': alias_id,
            'role_arn': role_arn
        }
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

if __name__ == "__main__":
    result = deploy_bedrock_agent()
    if result:
        print(f"\nAgent deployed successfully!")
    else:
        print(f"\nDeployment failed!")
        exit(1)
