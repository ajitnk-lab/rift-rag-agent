# 🎮 Rift RAG Agent - League of Legends AI Assistant

A complete serverless AI solution powered by AWS Bedrock Agent, S3 Vectors, and containerized Streamlit UI for League of Legends match analysis and insights.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   Streamlit UI  │───▶│  Lambda Function │───▶│   Bedrock Agent     │───▶│   S3 Vectors KB  │
│  (Containerized)│    │  (Function URL)  │    │ (Claude 3 Sonnet)   │    │ (League Data)    │
└─────────────────┘    └──────────────────┘    └─────────────────────┘    └──────────────────┘
```

## 📋 Components

### 1. **Streamlit Web Application**
- **Location**: `streamlit_app/`
- **Type**: Containerized Lambda Function with Function URL
- **Purpose**: Interactive web interface for querying League of Legends data

### 2. **AWS Bedrock Agent**
- **Name**: `rift-game-agent` (ID: FM4QOCUL4O)
- **Model**: Anthropic Claude 3 Sonnet
- **Purpose**: AI assistant specialized in League of Legends match analysis

### 3. **Knowledge Base**
- **Name**: `rift-game-kb` (ID: DW9OZ4OJIW)
- **Storage**: S3 Vectors with Amazon Titan embeddings
- **Data**: League of Legends player profiles and match statistics

### 4. **CDK Infrastructure**
- **Stacks**: S3VectorsPocStack, BedrockAgentStack, RiftUIStack
- **Language**: TypeScript
- **Purpose**: Infrastructure as Code deployment

## 🚀 Development Setup

### Prerequisites
```bash
# Required tools
- Node.js 18+
- Python 3.9+
- AWS CLI v2
- Docker
- CDK v2
```

### 1. Clone and Setup
```bash
git clone <repository>
cd rift2ragagent
npm install
```

### 2. Environment Configuration
```bash
# Set AWS credentials
aws configure

# Set CDK environment
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=us-east-1
```

## 📦 Development & Deployment Guide

### Phase 1: Data Preparation and Ingestion

#### 1.1 Data Preparation using Riot API (Python)
**Files and Scripts:**
```
scripts/
├── data_collection/
│   ├── riot_api_client.py          # Riot Games API client
│   ├── player_data_fetcher.py      # Fetch player profiles and match data
│   ├── data_processor.py           # Process and format League data
│   └── upload_to_s3.py             # Upload processed data to S3
data/
├── player_profiles/
│   ├── test-puuid-123_profile.txt  # Sample player profile
│   ├── X-IhmL38ws...profile.txt    # Professional player data
│   └── *.txt                       # Additional player profiles
```

**Key Development Files:**
- **`scripts/data_collection/riot_api_client.py`**: Handles Riot Games API authentication and requests
- **`scripts/data_collection/player_data_fetcher.py`**: Fetches match history, KDA stats, champion data
- **`scripts/data_collection/data_processor.py`**: Converts API responses to structured text format
- **`scripts/upload_to_s3.py`**: Uploads processed data to S3 bucket for ingestion

**Data Format Example:**
```
Player Profile: test-puuid-123
Season 2024 Summary:
- Total Games: 3
- Overall Win Rate: 66.7%
- Top Champions: Jinx, Vayne, Caitlyn
- Key Moments: Pentakill on Jinx on 2023-10-31
```

#### 1.2 S3 Vector Database Setup
**CDK Stack:** `S3VectorsPocStack`
**File:** `lib/s3-vectors-poc-stack.ts`

**Resources Created:**
```typescript
// S3 Vectors Bucket
const vectorBucket = new s3vectors.Bucket(this, 'RiftGameVectorsBucket', {
  bucketName: 'rift-game-vectors-poc',
  indexName: 'rift-matches-index',
  embeddingDimensions: 1536, // Titan v1 dimensions
});
```

**Resource Names:**
- **S3 Vectors Bucket**: `rift-game-vectors-poc`
- **Vector Index**: `rift-matches-index`
- **Embedding Model**: `amazon.titan-embed-text-v1`

### Phase 2: Knowledge Base and Agent Creation

#### 2.1 Knowledge Base Creation with S3 Vectors
**CDK Stack:** `BedrockAgentStack`
**File:** `lib/bedrock-agent-stack.ts`

**Key Resources:**
```typescript
// Knowledge Base
const knowledgeBase = new bedrock.CfnKnowledgeBase(this, 'RiftGameKB', {
  name: 'rift-game-kb',
  description: 'League of Legends match data knowledge base',
  knowledgeBaseConfiguration: {
    type: 'VECTOR',
    vectorKnowledgeBaseConfiguration: {
      embeddingModelArn: 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
    }
  },
  storageConfiguration: {
    type: 'S3_VECTORS',
    s3VectorsConfiguration: {
      vectorBucketArn: vectorBucket.bucketArn,
      indexArn: vectorBucket.indexArn
    }
  }
});

// Data Source
const dataSource = new bedrock.CfnDataSource(this, 'LeagueDataSource', {
  knowledgeBaseId: knowledgeBase.attrKnowledgeBaseId,
  name: 'league-data-source',
  dataSourceConfiguration: {
    type: 'S3',
    s3Configuration: {
      bucketArn: 'arn:aws:s3:::league-journey-kb-simple-2025'
    }
  }
});
```

**Resource Names:**
- **Knowledge Base**: `rift-game-kb` (ID: `DW9OZ4OJIW`)
- **Data Source**: `league-data-source` (ID: `0OHQVDNZCG`)
- **Source Bucket**: `league-journey-kb-simple-2025`

#### 2.2 Bedrock Agent with Strands Integration
**Development Scripts:**
```
scripts/
├── deploy_bedrock_agent.py        # Main agent deployment script
├── connect_kb_to_agent.py         # Connect KB to agent
├── connect_s3vectors_to_agent.py  # S3 Vectors specific connection
└── sync_knowledge_base.py         # Data ingestion management
```

**Agent Configuration:**
```python
# deploy_bedrock_agent.py
agent_config = {
    'agentName': 'rift-game-agent',
    'foundationModel': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'instruction': '''You are a League of Legends expert AI assistant specialized in analyzing professional match data.
    
You have access to real match data from professional players including:
- Champion picks and performance
- KDA ratios (Kills/Deaths/Assists)
- Gold earned and CS (Creep Score)
- Match outcomes and durations
- Game modes (Classic, ARAM)
- Player positions and roles''',
    'idleSessionTTLInSeconds': 600,
    'agentResourceRoleArn': role_arn
}
```

**Resource Names:**
- **Agent**: `rift-game-agent` (ID: `FM4QOCUL4O`)
- **Agent Role**: `RiftGameBedrockAgentRole`
- **KB Role**: `BedrockKnowledgeBaseRole`
- **Active Alias**: `rift-kb-alias` (ID: `A22JDQSMQM`)

### Phase 3: Streamlit UI with Lambda Web Adapter

#### 3.1 Streamlit Application Development
**CDK Stack:** `RiftUIStack`
**File:** `lib/rift-ui-stack.ts`

**Application Structure:**
```
streamlit_app/
├── Dockerfile                     # Container configuration
├── requirements.txt               # Python dependencies
├── app.py                        # Main Streamlit application
├── bedrock_client.py             # Bedrock Agent integration
├── lambda_handler.py             # Lambda entry point
└── static/
    ├── style.css                 # Custom styling
    └── logo.png                  # Application logo
```

**Key Development Files:**

**`streamlit_app/app.py`** - Main Streamlit Interface:
```python
import streamlit as st
import boto3
from bedrock_client import BedrockAgentClient

# Initialize Bedrock client
bedrock_client = BedrockAgentClient(
    agent_id='FM4QOCUL4O',
    agent_alias_id='A22JDQSMQM',
    region='us-east-1'
)

# Streamlit UI components
st.title("🎮 Rift RAG - League of Legends AI")
st.markdown("*Powered by AWS Bedrock Agent & S3 Vectors*")

# Query interface
user_query = st.text_input("Ask about League of Legends data:")
if st.button("Query Agent"):
    response = bedrock_client.query_agent(user_query)
    st.write(response)
```

**`streamlit_app/bedrock_client.py`** - Agent Integration:
```python
import boto3
import json

class BedrockAgentClient:
    def __init__(self, agent_id, agent_alias_id, region):
        self.client = boto3.client('bedrock-agent-runtime', region_name=region)
        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id
    
    def query_agent(self, query):
        response = self.client.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                    'knowledgeBaseId': 'DW9OZ4OJIW'
                }
            }
        )
        return response['output']['text']
```

#### 3.2 Lambda Container Deployment
**CDK Configuration:**
```typescript
// lib/rift-ui-stack.ts
const streamlitFunction = new lambda.Function(this, 'RiftStreamlitWeb', {
  functionName: 'rift-streamlit-web',
  code: lambda.Code.fromAssetImage(path.join(__dirname, '../streamlit_app')),
  handler: lambda.Handler.FROM_IMAGE,
  runtime: lambda.Runtime.FROM_IMAGE,
  memorySize: 1024,
  timeout: Duration.seconds(900),
  environment: {
    'BEDROCK_AGENT_ID': 'FM4QOCUL4O',
    'BEDROCK_AGENT_ALIAS_ID': 'A22JDQSMQM',
    'KNOWLEDGE_BASE_ID': 'DW9OZ4OJIW'
  }
});

// Function URL Configuration
const functionUrl = streamlitFunction.addFunctionUrl({
  authType: lambda.FunctionUrlAuthType.NONE,
  cors: {
    allowCredentials: false,
    allowedHeaders: ['*'],
    allowedMethods: [lambda.HttpMethod.ALL],
    allowedOrigins: ['*'],
    exposedHeaders: ['*'],
    maxAge: Duration.days(1)
  }
});
```

**Container Configuration (`streamlit_app/Dockerfile`):**
```dockerfile
FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD ["lambda_handler.handler"]
```

**Resource Names:**
- **Lambda Function**: `rift-streamlit-web`
- **Function URL**: `https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/`
- **Container Registry**: ECR repository auto-created by CDK
- **Execution Role**: Auto-generated with Bedrock permissions

### Phase 1: Infrastructure Deployment

#### 1. Deploy S3 Vectors Stack
```bash
# Deploy S3 Vectors infrastructure
cdk deploy S3VectorsPocStack --region us-east-1

# Outputs:
# - S3 Vectors bucket: rift-game-vectors-poc
# - Vector index: rift-matches-index
```

#### 2. Deploy Bedrock Agent Stack
```bash
# Deploy Bedrock Agent infrastructure
cdk deploy BedrockAgentStack --region us-east-1

# Outputs:
# - Bedrock Agent: rift-game-agent
# - Knowledge Base: rift-game-kb
# - IAM roles and policies
```

#### 3. Deploy Streamlit UI Stack
```bash
# Build and deploy containerized Streamlit app
cdk deploy RiftUIStack --region us-east-1

# Outputs:
# - Lambda Function: rift-streamlit-web
# - Function URL: https://xxx.lambda-url.us-east-1.on.aws/
```

### Phase 2: Data and Agent Configuration

#### 1. Create Knowledge Base
```bash
# Run knowledge base creation script
python scripts/create_kb_simple.py

# This creates:
# - Knowledge base with S3 Vectors storage
# - Data source pointing to S3 bucket
# - Embedding configuration (Titan v1)
```

#### 2. Deploy Bedrock Agent
```bash
# Run agent deployment script
python scripts/deploy_bedrock_agent.py

# This creates:
# - IAM role: RiftGameBedrockAgentRole
# - Bedrock agent with Claude 3 Sonnet
# - Agent aliases for different versions
```

#### 3. Connect Agent to Knowledge Base
```bash
# Run connection script
python scripts/connect_s3vectors_to_agent.py

# This:
# - Associates knowledge base with agent
# - Enables knowledge base state
# - Creates agent alias with KB access
```

#### 4. Upload and Sync Data
```bash
# Upload League data to S3
aws s3 sync data/ s3://league-journey-kb-simple-2025/

# Start ingestion job
python scripts/sync_knowledge_base.py
```

## 🗂️ Resource Mapping & File Structure

### CDK Stacks and Resources

#### 1. S3VectorsPocStack (`lib/s3-vectors-poc-stack.ts`)
```typescript
export class S3VectorsPocStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // S3 Vectors Bucket for embeddings storage
    const vectorBucket = new s3vectors.Bucket(this, 'RiftGameVectorsBucket', {
      bucketName: 'rift-game-vectors-poc',
      indexName: 'rift-matches-index',
      embeddingDimensions: 1536,
    });

    // Output the bucket ARN and index ARN
    new CfnOutput(this, 'VectorBucketArn', {
      value: vectorBucket.bucketArn,
      description: 'S3 Vectors bucket ARN for embeddings'
    });
  }
}
```

**Created Resources:**
- **S3 Vectors Bucket**: `rift-game-vectors-poc`
- **Vector Index**: `rift-matches-index`
- **Embedding Dimensions**: 1536 (Titan v1 compatible)

#### 2. BedrockAgentStack (`lib/bedrock-agent-stack.ts`)
```typescript
export class BedrockAgentStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // IAM Role for Knowledge Base
    const kbRole = new iam.Role(this, 'BedrockKnowledgeBaseRole', {
      roleName: 'BedrockKnowledgeBaseRole',
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess')
      ]
    });

    // Knowledge Base
    const knowledgeBase = new bedrock.CfnKnowledgeBase(this, 'RiftGameKB', {
      name: 'rift-game-kb',
      description: 'League of Legends match data knowledge base',
      roleArn: kbRole.roleArn,
      knowledgeBaseConfiguration: {
        type: 'VECTOR',
        vectorKnowledgeBaseConfiguration: {
          embeddingModelArn: 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
        }
      },
      storageConfiguration: {
        type: 'S3_VECTORS',
        s3VectorsConfiguration: {
          vectorBucketArn: 'arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc',
          indexArn: 'arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc/index/rift-matches-index'
        }
      }
    });

    // Data Source
    const dataSource = new bedrock.CfnDataSource(this, 'LeagueDataSource', {
      knowledgeBaseId: knowledgeBase.attrKnowledgeBaseId,
      name: 'league-data-source',
      description: 'League of Legends match data from S3',
      dataSourceConfiguration: {
        type: 'S3',
        s3Configuration: {
          bucketArn: 'arn:aws:s3:::league-journey-kb-simple-2025'
        }
      }
    });
  }
}
```

**Created Resources:**
- **Knowledge Base**: `rift-game-kb` (ID: `DW9OZ4OJIW`)
- **Data Source**: `league-data-source` (ID: `0OHQVDNZCG`)
- **IAM Role**: `BedrockKnowledgeBaseRole`
- **Source Bucket**: `league-journey-kb-simple-2025`

#### 3. RiftUIStack (`lib/rift-ui-stack.ts`)
```typescript
export class RiftUIStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Lambda Execution Role
    const lambdaRole = new iam.Role(this, 'StreamlitLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ],
      inlinePolicies: {
        BedrockAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'bedrock-agent-runtime:RetrieveAndGenerate',
                'bedrock-agent-runtime:Retrieve',
                'bedrock:InvokeModel'
              ],
              resources: ['*']
            })
          ]
        })
      }
    });

    // Containerized Lambda Function
    const streamlitFunction = new lambda.Function(this, 'RiftStreamlitWeb', {
      functionName: 'rift-streamlit-web',
      code: lambda.Code.fromAssetImage(path.join(__dirname, '../streamlit_app')),
      handler: lambda.Handler.FROM_IMAGE,
      runtime: lambda.Runtime.FROM_IMAGE,
      memorySize: 1024,
      timeout: Duration.seconds(900),
      role: lambdaRole,
      environment: {
        'BEDROCK_AGENT_ID': 'FM4QOCUL4O',
        'BEDROCK_AGENT_ALIAS_ID': 'A22JDQSMQM',
        'KNOWLEDGE_BASE_ID': 'DW9OZ4OJIW',
        'AWS_DEFAULT_REGION': 'us-east-1'
      }
    });

    // Function URL for public access
    const functionUrl = streamlitFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowCredentials: false,
        allowedHeaders: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedOrigins: ['*'],
        exposedHeaders: ['*'],
        maxAge: Duration.days(1)
      }
    });

    // Output the Function URL
    new CfnOutput(this, 'StreamlitAppUrl', {
      value: functionUrl.url,
      description: 'Streamlit application URL'
    });
  }
}
```

**Created Resources:**
- **Lambda Function**: `rift-streamlit-web`
- **Function URL**: `https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/`
- **IAM Role**: `StreamlitLambdaRole`
- **Container Image**: ECR repository (auto-created)

### Python Scripts and Their Functions

#### Data Preparation Scripts
```
scripts/
├── data_collection/
│   ├── riot_api_client.py          # Riot Games API wrapper
│   ├── player_data_fetcher.py      # Fetch player profiles and matches
│   ├── data_processor.py           # Convert API data to text format
│   └── upload_to_s3.py             # Upload processed data to S3
├── deploy_bedrock_agent.py         # Create and configure Bedrock agent
├── connect_kb_to_agent.py          # Associate knowledge base with agent
├── connect_s3vectors_to_agent.py   # S3 Vectors specific KB connection
├── create_kb_simple.py             # Create knowledge base and data source
└── sync_knowledge_base.py          # Manage data ingestion jobs
```

#### Key Script Functions:

**`scripts/deploy_bedrock_agent.py`**:
```python
def deploy_bedrock_agent():
    # Creates IAM role: RiftGameBedrockAgentRole
    # Creates Bedrock agent: rift-game-agent (FM4QOCUL4O)
    # Creates agent aliases for different versions
    # Configures Claude 3 Sonnet model
    pass
```

**`scripts/connect_s3vectors_to_agent.py`**:
```python
def connect_agent_to_kb():
    # Associates agent FM4QOCUL4O with KB DW9OZ4OJIW
    # Enables knowledge base state
    # Creates alias: rift-kb-alias (A22JDQSMQM)
    # Configures S3 Vectors integration
    pass
```

**`scripts/create_kb_simple.py`**:
```python
def create_knowledge_base():
    # Creates knowledge base: rift-game-kb (DW9OZ4OJIW)
    # Creates data source: league-data-source (0OHQVDNZCG)
    # Configures S3 Vectors storage
    # Sets up Titan embeddings
    pass
```

### Streamlit Application Structure

#### Core Application Files
```
streamlit_app/
├── Dockerfile                     # Container configuration
├── requirements.txt               # Python dependencies
├── lambda_handler.py              # Lambda entry point
├── app.py                        # Main Streamlit application
├── bedrock_client.py             # Bedrock Agent integration
├── config.py                     # Configuration management
└── static/
    ├── style.css                 # Custom CSS styling
    └── logo.png                  # Application branding
```

**`streamlit_app/lambda_handler.py`** - Lambda Entry Point:
```python
import streamlit as st
from streamlit.web import cli as stcli
import sys
import os

def handler(event, context):
    """Lambda handler for Streamlit app"""
    # Configure Streamlit for Lambda environment
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    
    # Start Streamlit server
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501"]
    stcli.main()
```

**`streamlit_app/bedrock_client.py`** - Agent Integration:
```python
class BedrockAgentClient:
    def __init__(self):
        self.agent_id = os.environ.get('BEDROCK_AGENT_ID', 'FM4QOCUL4O')
        self.agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'A22JDQSMQM')
        self.kb_id = os.environ.get('KNOWLEDGE_BASE_ID', 'DW9OZ4OJIW')
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        self.client = boto3.client('bedrock-agent-runtime', region_name=self.region)
    
    def query_agent(self, query: str) -> dict:
        """Query the Bedrock agent with knowledge base integration"""
        response = self.client.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'modelArn': f'arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                    'knowledgeBaseId': self.kb_id
                }
            }
        )
        return {
            'response': response['output']['text'],
            'citations': response.get('citations', []),
            'sessionId': response.get('sessionId')
        }
```

### Resource IDs and Endpoints

#### Production Resource Identifiers
```bash
# Bedrock Resources
AGENT_ID="FM4QOCUL4O"
AGENT_NAME="rift-game-agent"
AGENT_ALIAS_ID="A22JDQSMQM"
AGENT_ALIAS_NAME="rift-kb-alias"

# Knowledge Base Resources
KB_ID="DW9OZ4OJIW"
KB_NAME="rift-game-kb"
DATA_SOURCE_ID="0OHQVDNZCG"
DATA_SOURCE_NAME="league-data-source"

# Storage Resources
VECTOR_BUCKET="rift-game-vectors-poc"
VECTOR_INDEX="rift-matches-index"
DATA_BUCKET="league-journey-kb-simple-2025"

# Lambda Resources
FUNCTION_NAME="rift-streamlit-web"
FUNCTION_URL="https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/"

# IAM Roles
AGENT_ROLE="RiftGameBedrockAgentRole"
KB_ROLE="BedrockKnowledgeBaseRole"
LAMBDA_ROLE="StreamlitLambdaRole"
```

#### API Endpoints and ARNs
```bash
# Bedrock Agent ARN
AGENT_ARN="arn:aws:bedrock:us-east-1:039920874011:agent/FM4QOCUL4O"

# Knowledge Base ARN
KB_ARN="arn:aws:bedrock:us-east-1:039920874011:knowledge-base/DW9OZ4OJIW"

# S3 Vectors ARNs
VECTOR_BUCKET_ARN="arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc"
VECTOR_INDEX_ARN="arn:aws:s3vectors:us-east-1:039920874011:bucket/rift-game-vectors-poc/index/rift-matches-index"

# Lambda Function ARN
LAMBDA_ARN="arn:aws:lambda:us-east-1:039920874011:function:rift-streamlit-web"

# Model ARNs
CLAUDE_MODEL_ARN="arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
TITAN_EMBED_ARN="arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
```

## 🔧 Configuration Details

### Bedrock Agent Configuration
```json
{
  "agentName": "rift-game-agent",
  "foundationModel": "anthropic.claude-3-sonnet-20240229-v1:0",
  "instruction": "League of Legends expert AI assistant...",
  "idleSessionTTL": 600,
  "knowledgeBaseState": "ENABLED"
}
```

### S3 Vectors Configuration
```json
{
  "vectorBucketArn": "arn:aws:s3vectors:us-east-1:ACCOUNT:bucket/rift-game-vectors-poc",
  "indexArn": "arn:aws:s3vectors:us-east-1:ACCOUNT:bucket/rift-game-vectors-poc/index/rift-matches-index",
  "embeddingModel": "amazon.titan-embed-text-v1"
}
```

### Lambda Function Configuration
```json
{
  "functionName": "rift-streamlit-web",
  "packageType": "Image",
  "memorySize": 1024,
  "timeout": 900,
  "authType": "NONE"
}
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Ingestion Job Failures
**Problem**: Knowledge base ingestion fails with S3 permissions error
```bash
# Solution: Update IAM policy
aws iam put-role-policy --role-name BedrockKnowledgeBaseRole \
  --policy-name BedrockKnowledgeBasePolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["s3:ListBucket", "s3:GetObject"],
        "Resource": [
          "arn:aws:s3:::league-journey-kb-simple-2025",
          "arn:aws:s3:::league-journey-kb-simple-2025/*"
        ]
      }
    ]
  }'
```

#### 2. Agent Not Finding Data
**Problem**: Agent returns "no data found" responses
```bash
# Check ingestion status
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id DW9OZ4OJIW \
  --data-source-id 0OHQVDNZCG

# Restart ingestion if needed
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id DW9OZ4OJIW \
  --data-source-id 0OHQVDNZCG
```

#### 3. Lambda Function Timeout
**Problem**: Streamlit app times out on agent queries
```bash
# Increase timeout (max 15 minutes)
aws lambda update-function-configuration \
  --function-name rift-streamlit-web \
  --timeout 900
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Check agent status
aws bedrock-agent get-agent --agent-id FM4QOCUL4O

# Check knowledge base status
aws bedrock-agent get-knowledge-base --knowledge-base-id DW9OZ4OJIW

# Check Lambda function
aws lambda get-function --function-name rift-streamlit-web

# Test Streamlit app
curl https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/
```

### Performance Monitoring
- **CloudWatch Logs**: Monitor Lambda execution logs
- **Bedrock Metrics**: Track agent invocation success rates
- **S3 Vectors**: Monitor query performance and costs

## 🧪 Testing

### Unit Tests
```bash
# Test agent functionality
python tests/test_agent.py

# Test knowledge base retrieval
python tests/test_kb.py

# Test Streamlit integration
python tests/test_ui.py
```

### Integration Tests
```bash
# Test end-to-end flow
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What League players do you have data for?"}' \
  https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/api/query
```

## 📈 Scaling Considerations

### Performance Optimization
- **Lambda Concurrency**: Set reserved concurrency for consistent performance
- **S3 Vectors**: Monitor index size and query latency
- **Bedrock Quotas**: Request quota increases for high-volume usage

### Cost Optimization
- **Lambda Provisioned Concurrency**: For consistent low latency
- **S3 Vectors Storage**: Regular cleanup of unused embeddings
- **Bedrock Model Selection**: Balance cost vs. performance needs

## 🔐 Security

### IAM Roles and Policies
- **BedrockKnowledgeBaseRole**: Minimal permissions for KB access
- **RiftGameBedrockAgentRole**: Agent execution permissions
- **Lambda Execution Role**: Function URL and Bedrock access

### Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **Access Control**: Function URL with CORS restrictions
- **Audit Logging**: CloudTrail for all API calls

## 📚 API Reference

### Streamlit App Endpoints
```bash
# Health check
GET /

# Query agent
POST /api/query
Content-Type: application/json
{
  "query": "Your League of Legends question"
}
```

### Response Format
```json
{
  "response": "Agent response with League data and insights",
  "citations": ["S3 source references"],
  "sessionId": "unique-session-identifier"
}
```

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes
3. Test locally with CDK
4. Deploy to dev environment
5. Run integration tests
6. Submit pull request

### Code Standards
- **TypeScript**: ESLint + Prettier
- **Python**: Black + Flake8
- **CDK**: Follow AWS best practices
- **Documentation**: Update README for changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review CloudWatch logs
3. Verify IAM permissions
4. Test individual components
5. Create GitHub issue with logs

---

**Built with ❤️ using AWS CDK, Bedrock, and Streamlit**
