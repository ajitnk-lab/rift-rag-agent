# 🏗️ Architecture Documentation - Rift RAG Agent

## System Overview

The Rift RAG Agent is a serverless AI-powered system that provides intelligent analysis of League of Legends match data through a conversational interface.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 User Interface                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    HTTPS     ┌──────────────────────────────────────────┐  │
│  │   Web Browser   │◄────────────►│         Streamlit Web App               │  │
│  │                 │              │      (Containerized Lambda)             │  │
│  └─────────────────┘              └──────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ Function URL
                                           │ (Public Access)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS Lambda Layer                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                    rift-streamlit-web                                    │  │
│  │                                                                          │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │  │
│  │  │   Streamlit     │    │   FastAPI       │    │   Bedrock Client    │  │  │
│  │  │   Frontend      │◄──►│   Backend       │◄──►│   Integration       │  │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │  │
│  │                                                                          │  │
│  │  Configuration:                                                          │  │
│  │  • Memory: 1024 MB                                                       │  │
│  │  • Timeout: 900 seconds                                                  │  │
│  │  • Package: Container Image                                              │  │
│  │  • Runtime: Python 3.9                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ Bedrock Agent Runtime API
                                           │ (retrieve-and-generate)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AWS Bedrock Agent Layer                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                        rift-game-agent                                   │  │
│  │                        (ID: FM4QOCUL4O)                                  │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐│  │
│  │  │                    Agent Configuration                              ││  │
│  │  │                                                                     ││  │
│  │  │  • Model: Anthropic Claude 3 Sonnet                                ││  │
│  │  │  • Version: 3 (Latest)                                             ││  │
│  │  │  • Instruction: League of Legends expert AI assistant             ││  │
│  │  │  • Session TTL: 600 seconds                                        ││  │
│  │  │  • Knowledge Base: ENABLED                                         ││  │
│  │  └─────────────────────────────────────────────────────────────────────┘│  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐│  │
│  │  │                      Agent Aliases                                  ││  │
│  │  │                                                                     ││  │
│  │  │  • rift-kb-alias (A22JDQSMQM) → Version 3 ✅ ACTIVE               ││  │
│  │  │  • rift-agent-kb-alias (A2JUG8KOJA) → Version 2                   ││  │
│  │  │  • production (CBBG8H8XV5) → Version 1                            ││  │
│  │  │  • AgentTestAlias (TSTALIASID) → DRAFT                            ││  │
│  │  └─────────────────────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ Knowledge Base Query
                                           │ (Vector Similarity Search)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          Knowledge Base Layer                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                        rift-game-kb                                      │  │
│  │                        (ID: DW9OZ4OJIW)                                  │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐│  │
│  │  │                 Knowledge Base Configuration                        ││  │
│  │  │                                                                     ││  │
│  │  │  • Type: VECTOR                                                     ││  │
│  │  │  • Status: ACTIVE                                                   ││  │
│  │  │  • Embedding Model: Amazon Titan Embed Text v1                     ││  │
│  │  │  • Storage: S3 Vectors                                              ││  │
│  │  └─────────────────────────────────────────────────────────────────────┘│  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐│  │
│  │  │                      Data Source                                    ││  │
│  │  │                                                                     ││  │
│  │  │  • Name: league-data-source (ID: 0OHQVDNZCG)                       ││  │
│  │  │  • Type: S3                                                         ││  │
│  │  │  • Status: AVAILABLE                                                ││  │
│  │  │  • Source: s3://league-journey-kb-simple-2025/                     ││  │
│  │  │  • Documents Indexed: 14                                            ││  │
│  │  └─────────────────────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ Vector Storage & Retrieval
                                           │ (Embeddings & Similarity Search)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Storage Layer                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                         S3 Vectors                                       │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐│  │
│  │  │              Vector Bucket: rift-game-vectors-poc                   ││  │
│  │  │                                                                     ││  │
│  │  │  • Vector Index: rift-matches-index                                 ││  │
│  │  │  • Embedding Dimensions: 1536 (Titan v1)                           ││  │
│  │  │  • Storage: Optimized for similarity search                        ││  │
│  │  │  • Performance: Sub-second query response                           ││  │
│  │  └─────────────────────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                         S3 Data Bucket                                   │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐│  │
│  │  │            Source Bucket: league-journey-kb-simple-2025             ││  │
│  │  │                                                                     ││  │
│  │  │  • Player Profiles: *.txt files                                    ││  │
│  │  │  • Match Data: Structured text format                              ││  │
│  │  │  • Metadata: KDA, champions, win rates                             ││  │
│  │  │  • Content: League of Legends statistics                           ││  │
│  │  └─────────────────────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### Streamlit Web Application
- **Technology**: Python Streamlit framework
- **Deployment**: AWS Lambda Container Image
- **Access**: Public Function URL with CORS
- **Features**:
  - Interactive chat interface
  - Quick query buttons
  - Real-time responses
  - Citation display

### 2. Compute Layer

#### Lambda Function (rift-streamlit-web)
- **Runtime**: Container Image (Python 3.9)
- **Memory**: 1024 MB
- **Timeout**: 900 seconds (15 minutes)
- **Networking**: VPC not required
- **Permissions**: Bedrock Agent Runtime access

**Container Components**:
- **Streamlit**: Frontend UI framework
- **FastAPI**: Backend API endpoints
- **Bedrock Client**: AWS SDK integration
- **Dependencies**: boto3, streamlit, fastapi

### 3. AI Processing Layer

#### Bedrock Agent (rift-game-agent)
- **Model**: Anthropic Claude 3 Sonnet
- **Agent ID**: FM4QOCUL4O
- **Version**: 3 (Latest)
- **State**: PREPARED and ACTIVE

**Agent Configuration**:
```json
{
  "instruction": "League of Legends expert AI assistant specialized in analyzing professional match data...",
  "idleSessionTTL": 600,
  "knowledgeBaseState": "ENABLED",
  "orchestrationType": "DEFAULT"
}
```

**Prompt Templates**:
- Knowledge Base Response Generation: ENABLED
- Memory Summarization: DISABLED
- Post Processing: DISABLED
- Pre Processing: DISABLED
- Orchestration: ENABLED

### 4. Knowledge Management Layer

#### Knowledge Base (rift-game-kb)
- **Type**: VECTOR
- **Status**: ACTIVE
- **Embedding Model**: Amazon Titan Embed Text v1
- **Storage**: S3 Vectors

**Data Source Configuration**:
- **Type**: S3
- **Bucket**: league-journey-kb-simple-2025
- **Status**: AVAILABLE
- **Documents**: 14 indexed successfully

### 5. Storage Layer

#### S3 Vectors
- **Bucket**: rift-game-vectors-poc
- **Index**: rift-matches-index
- **Embedding Dimensions**: 1536
- **Query Performance**: Sub-second response times

#### S3 Data Bucket
- **Bucket**: league-journey-kb-simple-2025
- **Content**: League of Legends player profiles
- **Format**: Structured text files (.txt)
- **Size**: ~18 files (14 successfully processed)

## Data Flow

### 1. User Query Flow
```
User Input → Streamlit UI → FastAPI Backend → Lambda Function → 
Bedrock Agent Runtime API → Bedrock Agent → Knowledge Base → 
S3 Vectors → Vector Search → Embedding Similarity → 
Retrieved Documents → Claude 3 Sonnet → Generated Response → 
Lambda Response → Streamlit UI → User Display
```

### 2. Knowledge Base Ingestion Flow
```
Source Data (S3) → Data Source Crawler → Document Processing → 
Text Extraction → Chunking → Titan Embeddings → 
Vector Storage (S3 Vectors) → Index Update → Ready for Search
```

## Security Architecture

### IAM Roles and Policies

#### BedrockKnowledgeBaseRole
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3vectors:*"],
      "Resource": [
        "arn:aws:s3vectors:us-east-1:ACCOUNT:bucket/rift-game-vectors-poc",
        "arn:aws:s3vectors:us-east-1:ACCOUNT:bucket/rift-game-vectors-poc/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetObject"],
      "Resource": [
        "arn:aws:s3:::league-journey-kb-simple-2025",
        "arn:aws:s3:::league-journey-kb-simple-2025/*"
      ]
    }
  ]
}
```

#### RiftGameBedrockAgentRole
- Bedrock Agent execution permissions
- Knowledge Base access
- Model invocation rights

#### Lambda Execution Role
- Basic Lambda execution
- Bedrock Agent Runtime access
- CloudWatch Logs permissions

### Network Security
- **Function URL**: Public access with CORS restrictions
- **Encryption**: All data encrypted at rest and in transit
- **API Access**: Rate limited by AWS service quotas

## Performance Characteristics

### Response Times
- **UI Load**: ~1-2 seconds
- **Simple Queries**: ~3-5 seconds
- **Complex Queries**: ~6-10 seconds
- **Knowledge Base Search**: ~500ms-1s

### Scalability
- **Lambda Concurrency**: 1000 concurrent executions (default)
- **Bedrock Quotas**: Model-specific limits
- **S3 Vectors**: Virtually unlimited storage
- **Knowledge Base**: Up to 10,000 documents per data source

### Cost Optimization
- **Lambda**: Pay per request and duration
- **Bedrock**: Pay per token (input/output)
- **S3 Vectors**: Pay for storage and queries
- **S3 Standard**: Pay for storage and requests

## Monitoring and Observability

### CloudWatch Metrics
- Lambda function invocations, errors, duration
- Bedrock model invocations and token usage
- S3 Vectors query performance
- Knowledge Base ingestion job status

### Logging
- Lambda function logs: `/aws/lambda/rift-streamlit-web`
- Bedrock API calls: CloudTrail
- Application logs: Custom logging in Streamlit app

### Alerting
- Lambda function errors
- High response times
- Bedrock quota limits
- Knowledge Base ingestion failures

## Disaster Recovery

### Backup Strategy
- **Code**: Version controlled in Git
- **Infrastructure**: CDK templates
- **Data**: S3 cross-region replication (optional)
- **Configuration**: Documented in this repository

### Recovery Procedures
1. Redeploy infrastructure using CDK
2. Restore data from S3 backup
3. Re-run knowledge base ingestion
4. Verify agent functionality
5. Update DNS/URLs if needed

---

**Architecture Version**: 1.0  
**Last Updated**: October 29, 2025  
**Next Review**: November 29, 2025
