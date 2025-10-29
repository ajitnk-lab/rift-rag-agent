#!/usr/bin/env python3
import boto3
import json
import time

def create_simple_kb():
    """Create a simple knowledge base and connect to agent"""
    
    print("🔗 Creating Simple Knowledge Base")
    print("=" * 35)
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    opensearch = boto3.client('opensearchserverless', region_name='us-east-1')
    
    agent_id = "FM4QOCUL4O"
    collection_name = "rift-kb-collection"
    
    # 1. Get existing role
    print("\n1. Getting IAM role...")
    try:
        role_response = iam.get_role(RoleName="RiftGameKnowledgeBaseRole")
        kb_role_arn = role_response['Role']['Arn']
        print(f"✅ Using role: {kb_role_arn}")
    except Exception as e:
        print(f"❌ Role not found: {e}")
        return False
    
    # 2. Create OpenSearch collection
    print("\n2. Creating OpenSearch collection...")
    try:
        collection_response = opensearch.create_collection(
            name=collection_name,
            description="Collection for Rift KB",
            type="VECTORSEARCH"
        )
        collection_arn = collection_response['createCollectionDetail']['arn']
        print(f"✅ Created collection: {collection_arn}")
        
        # Wait for active
        for i in range(20):
            collections = opensearch.list_collections(collectionFilters={'name': collection_name})
            if collections['collectionSummaries'] and collections['collectionSummaries'][0]['status'] == 'ACTIVE':
                print("✅ Collection active")
                break
            time.sleep(10)
            
    except Exception as e:
        print(f"❌ Collection creation failed: {e}")
        return False
    
    # 3. Create knowledge base
    print("\n3. Creating knowledge base...")
    try:
        kb_response = bedrock_agent.create_knowledge_base(
            name="rift-simple-kb",
            description="Simple KB for Rift agent",
            roleArn=kb_role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1:0'
                }
            },
            storageConfiguration={
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    'collectionArn': collection_arn,
                    'vectorIndexName': 'bedrock-knowledge-base-default-index',
                    'fieldMapping': {
                        'vectorField': 'bedrock-knowledge-base-default-vector',
                        'textField': 'AMAZON_BEDROCK_TEXT_CHUNK',
                        'metadataField': 'AMAZON_BEDROCK_METADATA'
                    }
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Created KB: {kb_id}")
        
    except Exception as e:
        print(f"❌ KB creation failed: {e}")
        return False
    
    # 4. Associate with agent
    print("\n4. Associating with agent...")
    try:
        bedrock_agent.associate_agent_knowledge_base(
            agentId=agent_id,
            agentVersion='DRAFT',
            knowledgeBaseId=kb_id,
            description="Simple KB for testing",
            knowledgeBaseState='ENABLED'
        )
        print("✅ Associated with agent")
        
    except Exception as e:
        print(f"❌ Association failed: {e}")
        return False
    
    # 5. Prepare agent
    print("\n5. Preparing agent...")
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        
        # Wait for preparation
        for i in range(15):
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            if status == 'PREPARED':
                print("✅ Agent prepared")
                break
            time.sleep(10)
        
    except Exception as e:
        print(f"❌ Agent preparation failed: {e}")
        return False
    
    print(f"\n✅ SUCCESS! KB ID: {kb_id}")
    return kb_id

if __name__ == "__main__":
    create_simple_kb()
