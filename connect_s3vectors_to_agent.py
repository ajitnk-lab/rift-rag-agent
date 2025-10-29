#!/usr/bin/env python3
import boto3
import json
import time

def create_knowledge_base_with_s3vectors():
    """Create Knowledge Base using S3 Vectors and connect to Bedrock Agent"""
    
    print("🔗 Connecting S3 Vectors to Bedrock Agent")
    print("=" * 50)
    
    # Initialize clients
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    # Configuration
    agent_id = "FM4QOCUL4O"
    s3_bucket = "rift-game-vectors-poc"
    vector_index_name = "rift-matches-index"
    kb_name = "rift-matches-knowledge-base"
    
    print(f"Agent ID: {agent_id}")
    print(f"S3 Bucket: {s3_bucket}")
    print(f"Vector Index: {vector_index_name}")
    
    # Create IAM role for Knowledge Base
    role_name = "BedrockKnowledgeBaseRole"
    
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
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3vectors:QueryVectors",
                    "s3vectors:GetVectorIndex"
                ],
                "Resource": [
                    f"arn:aws:s3:::{s3_bucket}",
                    f"arn:aws:s3:::{s3_bucket}/*",
                    f"arn:aws:s3vectors:us-east-1:*:bucket/{s3_bucket}/index/{vector_index_name}"
                ]
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
            }
        ]
    }
    
    try:
        # Create IAM role
        print("\n📋 Creating IAM role...")
        try:
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            print(f"✅ Created role: {role_name}")
        except iam.exceptions.EntityAlreadyExistsException:
            print(f"✅ Role already exists: {role_name}")
        
        # Attach policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="BedrockKnowledgeBasePolicy",
            PolicyDocument=json.dumps(policy_document)
        )
        
        role_arn = f"arn:aws:iam::039920874011:role/{role_name}"
        print(f"✅ Role ARN: {role_arn}")
        
        # Wait for role propagation
        print("⏳ Waiting for IAM role propagation...")
        time.sleep(10)
        
        # Create Knowledge Base with S3 Vectors
        print("\n🗄️ Creating Knowledge Base...")
        
        kb_response = bedrock_agent.create_knowledge_base(
            name=kb_name,
            description="Knowledge base for League of Legends match data using S3 Vectors",
            roleArn=role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0'
                }
            },
            storageConfiguration={
                'type': 'S3_VECTORS',
                's3VectorsConfiguration': {
                    'vectorBucketArn': f'arn:aws:s3:::{s3_bucket}',
                    'indexName': vector_index_name,
                    'indexArn': f'arn:aws:s3vectors:us-east-1:039920874011:bucket/{s3_bucket}/index/{vector_index_name}'
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Created Knowledge Base: {kb_id}")
        
        # Wait for Knowledge Base to be ready
        print("⏳ Waiting for Knowledge Base to be ready...")
        while True:
            kb_status = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
            status = kb_status['knowledgeBase']['status']
            print(f"   Status: {status}")
            
            if status == 'ACTIVE':
                break
            elif status == 'FAILED':
                print("❌ Knowledge Base creation failed")
                return False
            
            time.sleep(5)
        
        # Associate Knowledge Base with Agent
        print(f"\n🤖 Associating Knowledge Base with Agent {agent_id}...")
        
        bedrock_agent.associate_agent_knowledge_base(
            agentId=agent_id,
            agentVersion='DRAFT',
            knowledgeBaseId=kb_id,
            description="League of Legends match data from S3 Vectors",
            knowledgeBaseState='ENABLED'
        )
        
        print("✅ Knowledge Base associated with Agent")
        
        # Prepare agent (create new version)
        print("\n🔄 Preparing Agent with Knowledge Base...")
        prepare_response = bedrock_agent.prepare_agent(agentId=agent_id)
        print("✅ Agent preparation initiated")
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! S3 Vectors connected to Bedrock Agent")
        print("=" * 50)
        print(f"Knowledge Base ID: {kb_id}")
        print(f"Agent ID: {agent_id}")
        print("The agent can now access your League of Legends match data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    create_knowledge_base_with_s3vectors()
