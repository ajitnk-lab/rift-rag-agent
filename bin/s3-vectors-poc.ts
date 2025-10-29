#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { S3VectorsPocStack } from '../lib/s3-vectors-poc-stack';
import { BedrockAgentStack } from '../lib/bedrock-agent-stack';
import { RiftUIStack } from '../lib/rift-ui-stack';

const app = new cdk.App();

new S3VectorsPocStack(app, 'S3VectorsPocStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});

new BedrockAgentStack(app, 'BedrockAgentStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});

new RiftUIStack(app, 'RiftUIStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});
