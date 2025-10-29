# 🔧 Troubleshooting Guide - Rift RAG Agent

## Common Issues and Solutions

### 1. Knowledge Base Ingestion Failures

#### Issue: S3 Permissions Error
```
Error: User is not authorized to perform: s3:ListBucket on resource
```

**Solution:**
```bash
# Update IAM policy for BedrockKnowledgeBaseRole
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

#### Issue: Metadata Size Too Large
```
Error: Filterable metadata must have at most 2048 bytes
```

**Solution:**
- Check data files for excessive metadata
- Reduce metadata size in source files
- Split large files into smaller chunks

#### Issue: Unsupported File Format
```
Error: Ignored files as their file format was not supported
```

**Solution:**
- Remove image files (PNG, ICO, etc.) from data bucket
- Keep only text files (.txt, .md, .json)
- Use supported formats: TXT, PDF, DOC, HTML, CSV, XLS

### 2. Agent Not Finding Data

#### Issue: Agent Returns "No Data Found"
**Symptoms:**
- Agent responds with "I don't have information about..."
- Empty search results

**Diagnosis:**
```bash
# Check ingestion job status
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id DW9OZ4OJIW \
  --data-source-id 0OHQVDNZCG

# Check if documents were indexed
aws bedrock-agent get-ingestion-job \
  --knowledge-base-id DW9OZ4OJIW \
  --data-source-id 0OHQVDNZCG \
  --ingestion-job-id <JOB_ID>
```

**Solution:**
```bash
# Restart ingestion job
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id DW9OZ4OJIW \
  --data-source-id 0OHQVDNZCG

# Wait for completion and verify documents indexed > 0
```

#### Issue: Agent-KB Association Missing
**Diagnosis:**
```bash
# Check if agent is associated with KB
aws bedrock-agent list-agent-knowledge-bases \
  --agent-id FM4QOCUL4O \
  --agent-version 3
```

**Solution:**
```bash
# Re-associate agent with KB
aws bedrock-agent associate-agent-knowledge-base \
  --agent-id FM4QOCUL4O \
  --agent-version DRAFT \
  --knowledge-base-id DW9OZ4OJIW \
  --description "League of Legends match data for game analysis" \
  --knowledge-base-state ENABLED
```

### 3. Lambda Function Issues

#### Issue: Function Timeout
**Symptoms:**
- 504 Gateway Timeout errors
- Requests taking > 15 minutes

**Solution:**
```bash
# Increase timeout (max 900 seconds)
aws lambda update-function-configuration \
  --function-name rift-streamlit-web \
  --timeout 900

# Increase memory if needed
aws lambda update-function-configuration \
  --function-name rift-streamlit-web \
  --memory-size 1024
```

#### Issue: Container Image Issues
**Symptoms:**
- Function fails to start
- "Runtime.InvalidEntrypoint" errors

**Solution:**
```bash
# Check function configuration
aws lambda get-function --function-name rift-streamlit-web

# Redeploy if needed
cdk deploy RiftUIStack --region us-east-1
```

#### Issue: Function URL Not Working
**Symptoms:**
- 403 Forbidden errors
- CORS issues

**Solution:**
```bash
# Check Function URL configuration
aws lambda get-function-url-config --function-name rift-streamlit-web

# Update CORS if needed
aws lambda update-function-url-config \
  --function-name rift-streamlit-web \
  --cors '{
    "AllowCredentials": false,
    "AllowHeaders": ["*"],
    "AllowMethods": ["*"],
    "AllowOrigins": ["*"],
    "ExposeHeaders": ["*"],
    "MaxAge": 86400
  }'
```

### 4. Bedrock Agent Issues

#### Issue: Rate Limiting
**Symptoms:**
- "ThrottlingException: Your request rate is too high"

**Solution:**
- Wait between requests (30+ seconds)
- Implement exponential backoff
- Request quota increases from AWS Support

#### Issue: Model Access Denied
**Symptoms:**
- "AccessDeniedException" when invoking agent

**Solution:**
```bash
# Enable model access in Bedrock console
# Or via CLI (if available in your region)
aws bedrock put-model-invocation-logging-configuration \
  --logging-config '{
    "cloudWatchConfig": {
      "logGroupName": "/aws/bedrock/modelinvocations",
      "roleArn": "arn:aws:iam::ACCOUNT:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase"
    }
  }'
```

### 5. CDK Deployment Issues

#### Issue: Stack Deployment Fails
**Symptoms:**
- CDK deploy errors
- Resource creation failures

**Solution:**
```bash
# Check CDK version
cdk --version

# Bootstrap if needed
cdk bootstrap aws://ACCOUNT/us-east-1

# Deploy with verbose logging
cdk deploy --verbose

# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name <STACK_NAME>
```

#### Issue: Resource Limits
**Symptoms:**
- "LimitExceeded" errors
- Service quotas reached

**Solution:**
- Request quota increases via AWS Support
- Clean up unused resources
- Use different regions if needed

### 6. Data and Content Issues

#### Issue: Poor Search Results
**Symptoms:**
- Agent finds irrelevant information
- Low-quality responses

**Solution:**
- Improve data quality and structure
- Add more descriptive metadata
- Use better file naming conventions
- Increase chunk overlap in embeddings

#### Issue: Missing Citations
**Symptoms:**
- Agent responses without source references

**Solution:**
- Verify S3 source URIs are correct
- Check data source configuration
- Ensure proper metadata in source files

## Diagnostic Commands

### Health Check Script
```bash
#!/bin/bash
echo "=== Rift RAG Agent Health Check ==="

# Check agent
echo "Checking Bedrock Agent..."
aws bedrock-agent get-agent --agent-id FM4QOCUL4O --query "agent.agentStatus"

# Check knowledge base
echo "Checking Knowledge Base..."
aws bedrock-agent get-knowledge-base --knowledge-base-id DW9OZ4OJIW --query "knowledgeBase.status"

# Check Lambda function
echo "Checking Lambda Function..."
aws lambda get-function --function-name rift-streamlit-web --query "Configuration.State"

# Check latest ingestion job
echo "Checking Latest Ingestion Job..."
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id DW9OZ4OJIW \
  --data-source-id 0OHQVDNZCG \
  --max-results 1 \
  --query "ingestionJobSummaries[0].{Status:status,Documents:statistics.numberOfNewDocumentsIndexed}"

# Test Function URL
echo "Testing Streamlit App..."
curl -I https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/ 2>/dev/null | head -1

echo "=== Health Check Complete ==="
```

### Performance Test Script
```bash
#!/bin/bash
echo "=== Performance Test ==="

# Test agent response time
echo "Testing agent query..."
time aws bedrock-agent-runtime retrieve-and-generate \
  --input '{"text": "What League players do you have data for?"}' \
  --retrieve-and-generate-configuration '{
    "type": "KNOWLEDGE_BASE",
    "knowledgeBaseConfiguration": {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
      "knowledgeBaseId": "DW9OZ4OJIW"
    }
  }' > /dev/null

# Test Streamlit app response time
echo "Testing Streamlit app..."
time curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What League players do you have data for?"}' \
  https://k35ucxkawlc3ljpah6ajexbwh40mubph.lambda-url.us-east-1.on.aws/api/query > /dev/null

echo "=== Performance Test Complete ==="
```

## Monitoring and Alerts

### CloudWatch Metrics to Monitor
- Lambda function errors and duration
- Bedrock agent invocation success rate
- S3 Vectors query latency
- Knowledge base ingestion job status

### Recommended Alarms
```bash
# Lambda function errors
aws cloudwatch put-metric-alarm \
  --alarm-name "RiftStreamlitErrors" \
  --alarm-description "Lambda function errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=rift-streamlit-web

# Lambda function duration
aws cloudwatch put-metric-alarm \
  --alarm-name "RiftStreamlitDuration" \
  --alarm-description "Lambda function duration" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 30000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=rift-streamlit-web
```

## Getting Help

### Log Locations
- **Lambda Logs**: `/aws/lambda/rift-streamlit-web`
- **Bedrock Logs**: Check CloudTrail for API calls
- **CDK Logs**: Local terminal output during deployment

### Support Channels
1. Check AWS Service Health Dashboard
2. Review AWS Documentation
3. Contact AWS Support for quota increases
4. Check GitHub issues for known problems

---

**Need more help?** Create an issue with:
- Error messages and stack traces
- CloudWatch log excerpts
- Steps to reproduce the problem
- Your AWS region and account details (without sensitive info)
