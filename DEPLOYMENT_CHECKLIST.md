# 🚀 Deployment Checklist - Rift RAG Agent

## Pre-Deployment Requirements

### ✅ Environment Setup
- [ ] AWS CLI v2 installed and configured
- [ ] Node.js 18+ installed
- [ ] Python 3.9+ installed
- [ ] Docker installed and running
- [ ] CDK v2 installed (`npm install -g aws-cdk`)
- [ ] AWS credentials configured (`aws configure`)

### ✅ Project Setup
- [ ] Repository cloned
- [ ] Dependencies installed (`npm install`)
- [ ] Environment variables set:
  ```bash
  export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
  export CDK_DEFAULT_REGION=us-east-1
  ```

## Phase 1: Infrastructure Deployment

### ✅ S3 Vectors Stack
- [ ] Deploy: `cdk deploy S3VectorsPocStack --region us-east-1`
- [ ] Verify S3 Vectors bucket created: `rift-game-vectors-poc`
- [ ] Verify vector index created: `rift-matches-index`

### ✅ Bedrock Agent Stack
- [ ] Deploy: `cdk deploy BedrockAgentStack --region us-east-1`
- [ ] Verify Bedrock agent created: `rift-game-agent`
- [ ] Verify knowledge base created: `rift-game-kb`
- [ ] Verify IAM roles created

### ✅ Streamlit UI Stack
- [ ] Deploy: `cdk deploy RiftUIStack --region us-east-1`
- [ ] Verify Lambda function created: `rift-streamlit-web`
- [ ] Verify Function URL created and accessible
- [ ] Test UI loads: `curl -I <function-url>`

## Phase 2: Data and Agent Configuration

### ✅ Knowledge Base Setup
- [ ] Run: `python scripts/create_kb_simple.py`
- [ ] Verify knowledge base has S3 Vectors storage
- [ ] Verify data source created pointing to S3 bucket
- [ ] Verify embedding model configured (Titan v1)

### ✅ Bedrock Agent Deployment
- [ ] Run: `python scripts/deploy_bedrock_agent.py`
- [ ] Verify IAM role created: `RiftGameBedrockAgentRole`
- [ ] Verify agent uses Claude 3 Sonnet model
- [ ] Verify agent aliases created

### ✅ Agent-KB Connection
- [ ] Run: `python scripts/connect_s3vectors_to_agent.py`
- [ ] Verify agent associated with knowledge base
- [ ] Verify knowledge base state is ENABLED
- [ ] Verify agent alias has KB access

### ✅ Data Upload and Ingestion
- [ ] Upload data: `aws s3 sync data/ s3://league-journey-kb-simple-2025/`
- [ ] Fix IAM permissions if needed:
  ```bash
  aws iam put-role-policy --role-name BedrockKnowledgeBaseRole \
    --policy-name BedrockKnowledgeBasePolicy \
    --policy-document '{
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
    }'
  ```
- [ ] Start ingestion: `aws bedrock-agent start-ingestion-job --knowledge-base-id <KB_ID> --data-source-id <DS_ID>`
- [ ] Monitor ingestion: `aws bedrock-agent get-ingestion-job --knowledge-base-id <KB_ID> --data-source-id <DS_ID> --ingestion-job-id <JOB_ID>`
- [ ] Verify ingestion completes successfully with documents indexed

## Phase 3: Testing and Validation

### ✅ Component Testing
- [ ] Test knowledge base retrieval:
  ```bash
  aws bedrock-agent-runtime retrieve \
    --knowledge-base-id <KB_ID> \
    --retrieval-query '{"text": "What League players are in the data?"}'
  ```
- [ ] Test agent via retrieve-and-generate:
  ```bash
  aws bedrock-agent-runtime retrieve-and-generate \
    --input '{"text": "What League players do you have data for?"}' \
    --retrieve-and-generate-configuration '{
      "type": "KNOWLEDGE_BASE",
      "knowledgeBaseConfiguration": {
        "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "knowledgeBaseId": "<KB_ID>"
      }
    }'
  ```

### ✅ End-to-End Testing
- [ ] Test Streamlit app UI loads
- [ ] Test agent integration via API:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "What League players do you have data for?"}' \
    <function-url>/api/query
  ```
- [ ] Test specific queries:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "Tell me about the Pentakill on Jinx"}' \
    <function-url>/api/query
  ```

### ✅ Performance Validation
- [ ] Verify response times < 10 seconds
- [ ] Verify agent returns accurate data with citations
- [ ] Verify no rate limiting issues
- [ ] Check CloudWatch logs for errors

## Phase 4: Production Readiness

### ✅ Security Review
- [ ] Verify IAM roles have minimal permissions
- [ ] Verify Function URL CORS configuration
- [ ] Verify no hardcoded credentials
- [ ] Enable CloudTrail logging

### ✅ Monitoring Setup
- [ ] Configure CloudWatch alarms for Lambda errors
- [ ] Set up Bedrock usage monitoring
- [ ] Configure S3 Vectors cost alerts
- [ ] Set up log retention policies

### ✅ Documentation
- [ ] Update README with actual resource IDs
- [ ] Document any custom configurations
- [ ] Create runbook for common operations
- [ ] Document troubleshooting procedures

## Resource IDs (Update with actual values)

```bash
# Bedrock Agent
AGENT_ID="FM4QOCUL4O"
AGENT_ALIAS_ID="A22JDQSMQM"

# Knowledge Base
KB_ID="DW9OZ4OJIW"
DATA_SOURCE_ID="0OHQVDNZCG"

# Lambda Function
FUNCTION_NAME="rift-streamlit-web"
FUNCTION_URL="https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/"

# S3 Buckets
VECTOR_BUCKET="rift-game-vectors-poc"
DATA_BUCKET="league-journey-kb-simple-2025"
```

## Quick Commands Reference

```bash
# Check agent status
aws bedrock-agent get-agent --agent-id $AGENT_ID

# Check KB status
aws bedrock-agent get-knowledge-base --knowledge-base-id $KB_ID

# Check ingestion jobs
aws bedrock-agent list-ingestion-jobs --knowledge-base-id $KB_ID --data-source-id $DATA_SOURCE_ID

# Check Lambda function
aws lambda get-function --function-name $FUNCTION_NAME

# Test Streamlit app
curl -I $FUNCTION_URL
```

---

**✅ Deployment Complete!** 

Your Rift RAG Agent is now ready for production use.
