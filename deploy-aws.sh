#!/bin/bash
# AWS Deployment Script for ORU Transcript Formatter
# This script builds and pushes your Docker image to AWS ECR for App Runner deployment

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ECR_REPO:-oru-transcript-formatter}"
IMAGE_TAG="${1:-latest}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AWS Deployment Script${NC}"
echo "================================"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}❌ AWS CLI not found. Installing...${NC}"
    echo "Please install AWS CLI first: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Get AWS account ID
echo -e "${BLUE}📋 Getting AWS account information...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo -e "${YELLOW}❌ Could not get AWS account ID.${NC}"
    echo "Please configure AWS credentials: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS Account ID: $AWS_ACCOUNT_ID${NC}"
echo -e "${GREEN}✅ Region: $AWS_REGION${NC}"
echo ""

# Check if ECR repository exists, create if not
echo -e "${BLUE}🔍 Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION &>/dev/null; then
    echo -e "${YELLOW}⚠️  Repository doesn't exist. Creating...${NC}"
    aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION
    echo -e "${GREEN}✅ Repository created: $ECR_REPO${NC}"
else
    echo -e "${GREEN}✅ Repository exists: $ECR_REPO${NC}"
fi

ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
ECR_IMAGE="$ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG"

echo ""
echo -e "${BLUE}🏗️  Building Docker image...${NC}"
docker build -t $ECR_REPO:$IMAGE_TAG .

echo ""
echo -e "${BLUE}🏷️  Tagging image...${NC}"
docker tag $ECR_REPO:$IMAGE_TAG $ECR_IMAGE

echo ""
echo -e "${BLUE}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

echo ""
echo -e "${BLUE}📤 Pushing image to ECR...${NC}"
docker push $ECR_IMAGE

echo ""
echo -e "${GREEN}✅ Successfully deployed!${NC}"
echo "================================"
echo -e "Image URI: ${BLUE}$ECR_IMAGE${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Go to AWS App Runner Console: https://console.aws.amazon.com/apprunner/"
echo "2. Create a new service (or update existing)"
echo "3. Use this image URI: $ECR_IMAGE"
echo "4. Set environment variable: ANTHROPIC_API_KEY"
echo "5. Configure port: 8000"
echo ""
echo -e "${GREEN}🔄 App Runner will automatically deploy your new image!${NC}"

