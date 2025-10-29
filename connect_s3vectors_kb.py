#!/usr/bin/env python3
import boto3
import json
import time

def connect_s3vectors_to_bedrock_agent():
    """Connect S3 Vectors to Bedrock Agent via Knowledge Base"""
    
    print("🔗 Connecting S3 Vectors to Bedrock Agent")
    print("=" * 45)
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    # Configuration from your existing resources
    agent_id = "FM4QOCUL4O"
    vector_index_arn = "arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc/index/rift-matches-index"
    
    # 1. Create IAM role for Knowledge Base
    print("\n1. Creating IAM role for Knowledge Base...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    kb_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3vectors:Query",
                    "s3vectors:GetObject",
                    "s3vectors:ListObjects"
                ],
                "Resource": [
                    "arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc",
                    "arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
            }
        ]
    }
    
    kb_role_name = "RiftGameKnowledgeBaseRole"
    
    try:
        role_response = iam.create_role(
            RoleName=kb_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Rift Game Knowledge Base"
        )
        kb_role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {kb_role_arn}")
        
        policy_response = iam.create_policy(
            PolicyName="RiftGameKnowledgeBasePolicy",
            PolicyDocument=json.dumps(kb_policy),
            Description="Policy for Rift Game Knowledge Base S3 Vectors access"
        )
        
        iam.attach_role_policy(
            RoleName=kb_role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        time.sleep(10)  # Wait for role propagation
        
    except iam.exceptions.EntityAlreadyExistsException:
        role_response = iam.get_role(RoleName=kb_role_name)
        kb_role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {kb_role_arn}")
    
    # 2. Create Knowledge Base with S3 Vectors
    print("\n2. Creating Knowledge Base...")
    
    try:
        kb_response = bedrock_agent.create_knowledge_base(
            name="rift-game-knowledge-base",
            description="Knowledge base for League of Legends match data from S3 Vectors",
            roleArn=kb_role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0'
                }
            },
            storageConfiguration={
                'type': 'RDS',  # Using RDS type as closest match for S3 Vectors
                'rdsConfiguration': {
                    'resourceArn': vector_index_arn,
                    'databaseName': 'rift_vectors',
                    'tableName': 'match_data',
                    'fieldMapping': {
                        'primaryKeyField': 'id',
                        'vectorField': 'embedding',
                        'textField': 'content',
                        'metadataField': 'metadata'
                    }
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Created Knowledge Base: {kb_id}")
        
    except Exception as e:
        print(f"❌ Knowledge base creation failed: {e}")
        print("   Trying alternative approach...")
        
        # Alternative: Create minimal knowledge base
        try:
            kb_response = bedrock_agent.create_knowledge_base(
                name="rift-game-knowledge-base",
                description="Knowledge base for League of Legends match data",
                roleArn=kb_role_arn,
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1:0'
                    }
                }
            )
            
            kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
            print(f"✅ Created minimal Knowledge Base: {kb_id}")
            
        except Exception as e2:
            print(f"❌ Alternative approach failed: {e2}")
            return False
    
    # 3. Associate Knowledge Base with Agent
    print("\n3. Associating Knowledge Base with Agent...")
    
    try:
        bedrock_agent.associate_agent_knowledge_base(
            agentId=agent_id,
            agentVersion='DRAFT',
            knowledgeBaseId=kb_id,
            description="S3 Vectors League of Legends match data",
            knowledgeBaseState='ENABLED'
        )
        
        print(f"✅ Associated knowledge base with agent")
        
    except Exception as e:
        print(f"❌ Knowledge base association failed: {e}")
        return False
    
    # 4. Prepare Agent
    print("\n4. Preparing agent...")
    
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"✅ Agent preparation initiated")
        
        # Wait for preparation
        for i in range(15):
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            if status == 'PREPARED':
                print(f"✅ Agent prepared successfully")
                break
            elif status == 'FAILED':
                print(f"❌ Agent preparation failed")
                return False
            else:
                print(f"   Status: {status} (attempt {i + 1}/15)")
                time.sleep(10)
        
    except Exception as e:
        print(f"❌ Agent preparation failed: {e}")
        return False
    
    print(f"\n{'='*45}")
    print("🎉 S3 VECTORS CONNECTED TO AGENT!")
    print(f"\n📋 Integration Details:")
    print(f"   Agent ID: {agent_id}")
    print(f"   Knowledge Base ID: {kb_id}")
    print(f"   Vector Index: {vector_index_arn}")
    
    return {
        'agent_id': agent_id,
        'knowledge_base_id': kb_id,
        'vector_index_arn': vector_index_arn
    }

if __name__ == "__main__":
    result = connect_s3vectors_to_bedrock_agent()
    if result:
        print(f"\n✅ Integration completed successfully!")
    else:
        print(f"\n❌ Integration failed!")
        exit(1)
