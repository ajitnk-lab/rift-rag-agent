#!/usr/bin/env python3
import boto3
import json
import time

def connect_knowledge_base_to_agent():
    """Connect S3 Vectors knowledge base to existing Bedrock Agent"""
    
    print("🔗 Connecting Knowledge Base to Bedrock Agent")
    print("=" * 50)
    
    # Initialize clients
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    # Configuration
    agent_id = "FM4QOCUL4O"  # Your existing agent ID
    bucket_name = "rift-game-vectors-poc"
    
    # 1. Create IAM role for Knowledge Base
    print("\n1. Creating IAM role for Knowledge Base...")
    
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
    
    kb_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
            }
        ]
    }
    
    kb_role_name = "RiftGameKnowledgeBaseRole"
    
    try:
        # Create role
        role_response = iam.create_role(
            RoleName=kb_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Rift Game Knowledge Base"
        )
        kb_role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {kb_role_arn}")
        
        # Create and attach policy
        policy_response = iam.create_policy(
            PolicyName="RiftGameKnowledgeBasePolicy",
            PolicyDocument=json.dumps(kb_policy),
            Description="Policy for Rift Game Knowledge Base S3 access"
        )
        
        iam.attach_role_policy(
            RoleName=kb_role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        print("   Waiting for role to propagate...")
        time.sleep(15)
        
    except iam.exceptions.EntityAlreadyExistsException:
        role_response = iam.get_role(RoleName=kb_role_name)
        kb_role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {kb_role_arn}")
    
    # 2. Get S3 Vectors index ARN from CloudFormation
    print("\n2. Getting S3 Vectors index ARN...")
    
    cf = boto3.client('cloudformation', region_name='us-east-1')
    try:
        stack_response = cf.describe_stacks(StackName='S3VectorsPocStack')
        outputs = stack_response['Stacks'][0]['Outputs']
        vector_index_arn = None
        
        for output in outputs:
            if output['OutputKey'] == 'VectorIndexArn':
                vector_index_arn = output['OutputValue']
                break
        
        if not vector_index_arn:
            print("❌ Could not find VectorIndexArn in stack outputs")
            return False
            
        print(f"✅ Found S3 Vectors index: {vector_index_arn}")
        
    except Exception as e:
        print(f"❌ Failed to get S3 Vectors index ARN: {e}")
        return False
    
    # 3. Create Knowledge Base with S3 Vectors
    print("\n3. Creating Knowledge Base...")
    
    try:
        kb_response = bedrock_agent.create_knowledge_base(
            name="rift-game-knowledge-base",
            description="Knowledge base for League of Legends match data",
            roleArn=kb_role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0',
                    'embeddingModelConfiguration': {
                        'bedrockEmbeddingModelConfiguration': {
                            'dimensions': 1536
                        }
                    }
                }
            },
            storageConfiguration={
                'type': 'RDS',
                'rdsConfiguration': {
                    'resourceArn': vector_index_arn,
                    'credentialsSecretArn': 'arn:aws:secretsmanager:us-east-1:039920874011:secret:rds-db-credentials/cluster-EXAMPLE',
                    'databaseName': 'bedrock_integration',
                    'tableName': 'bedrock_kb',
                    'fieldMapping': {
                        'primaryKeyField': 'id',
                        'vectorField': 'embedding',
                        'textField': 'chunks',
                        'metadataField': 'metadata'
                    }
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Created Knowledge Base: {kb_id}")
        
        # Wait for KB to be ready
        print("   Waiting for knowledge base to be ready...")
        max_attempts = 30
        for attempt in range(max_attempts):
            kb_status = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
            status = kb_status['knowledgeBase']['status']
            
            if status == 'ACTIVE':
                print(f"✅ Knowledge base is active")
                break
            elif status == 'FAILED':
                print(f"❌ Knowledge base creation failed")
                return False
            else:
                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
                time.sleep(10)
        
    except Exception as e:
        print(f"❌ Knowledge base creation failed: {e}")
        return False
    
    # 3. Associate Knowledge Base with Agent
    print("\n3. Associating Knowledge Base with Agent...")
    
    try:
        associate_response = bedrock_agent.associate_agent_knowledge_base(
            agentId=agent_id,
            agentVersion='DRAFT',
            knowledgeBaseId=kb_id,
            description="League of Legends match data knowledge base",
            knowledgeBaseState='ENABLED'
        )
        
        print(f"✅ Associated knowledge base with agent")
        
    except Exception as e:
        print(f"❌ Knowledge base association failed: {e}")
        return False
    
    # 4. Update and Prepare Agent
    print("\n4. Preparing agent with knowledge base...")
    
    try:
        # Prepare the agent to activate changes
        prepare_response = bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"✅ Agent preparation initiated")
        
        # Wait for preparation to complete
        print("   Waiting for agent preparation...")
        max_attempts = 30
        for attempt in range(max_attempts):
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            
            if status == 'PREPARED':
                print(f"✅ Agent prepared successfully with knowledge base")
                break
            elif status == 'FAILED':
                print(f"❌ Agent preparation failed")
                return False
            else:
                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
                time.sleep(10)
        
    except Exception as e:
        print(f"❌ Agent preparation failed: {e}")
        return False
    
    # 5. Summary
    print(f"\n{'='*50}")
    print("🎉 KNOWLEDGE BASE CONNECTED SUCCESSFULLY!")
    print(f"\n📋 Integration Details:")
    print(f"   Agent ID: {agent_id}")
    print(f"   Knowledge Base ID: {kb_id}")
    print(f"   S3 Vectors Bucket: {bucket_name}")
    print(f"   KB Role: {kb_role_arn}")
    
    print(f"\n🚀 Your agent can now access League of Legends match data!")
    print(f"   Test with questions about champions, KDA, or match statistics")
    
    return {
        'agent_id': agent_id,
        'knowledge_base_id': kb_id,
        'kb_role_arn': kb_role_arn
    }

if __name__ == "__main__":
    result = connect_knowledge_base_to_agent()
    if result:
        print(f"\nKnowledge base integration completed successfully!")
    else:
        print(f"\nIntegration failed!")
        exit(1)
