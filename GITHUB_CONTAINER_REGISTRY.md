# GitHub Container Registry Setup

Modern and secure way to publish Docker images.

## 🚀 Quick Setup

### Method 1: GitHub CLI (Recommended - Most Secure)

```bash
# Install GitHub CLI
brew install gh

# Login (opens browser for OAuth)
gh auth login

# Login to Docker
gh auth token | docker login ghcr.io -u mirongit --password-stdin
```

Done! No manual tokens needed. ✅

### Method 2: Fine-grained Personal Access Token (Modern PAT)

**Create token:**
1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens**
2. Click "Generate new token"
3. Fill in:
   - **Name:** "Docker GHCR Access"
   - **Expiration:** 90 days (or custom)
   - **Repository access:** Select repositories → city-helper-ai-backend
   - **Permissions:**
     - Repository permissions → Contents: Read
     - Repository permissions → Packages: Read and write
4. Generate token
5. Copy token (save it securely!)

**Login:**
```bash
echo "YOUR_FINE_GRAINED_TOKEN" | docker login ghcr.io -u mirongit --password-stdin
```

**Advantages:**
- ✅ Granular permissions (only this repo)
- ✅ Expiration dates (better security)
- ✅ Can be revoked easily
- ✅ Audit logs

---

## 📦 Build and Push Workflow

### Local Development

```bash
# 1. Build image
docker build -t ghcr.io/miron-s-playground/city-helper-ai-backend:latest .

# 2. Tag with version (optional)
docker tag ghcr.io/miron-s-playground/city-helper-ai-backend:latest \
           ghcr.io/miron-s-playground/city-helper-ai-backend:v1.0.0

# 3. Push to registry
docker push ghcr.io/miron-s-playground/city-helper-ai-backend:latest
docker push ghcr.io/miron-s-playground/city-helper-ai-backend:v1.0.0

# 4. Verify
docker pull ghcr.io/miron-s-playground/city-helper-ai-backend:latest
docker run -p 3001:3001 ghcr.io/miron-s-playground/city-helper-ai-backend:latest
```

### Make Commands

Add to `Makefile`:
```makefile
REGISTRY := ghcr.io
IMAGE_NAME := miron-s-playground/city-helper-ai-backend
TAG := latest

docker-login:
	@gh auth token | docker login $(REGISTRY) -u mirongit --password-stdin

docker-build-push:
	docker build -t $(REGISTRY)/$(IMAGE_NAME):$(TAG) .
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)

docker-pull:
	docker pull $(REGISTRY)/$(IMAGE_NAME):$(TAG)

docker-run-remote:
	docker run -p 3001:3001 $(REGISTRY)/$(IMAGE_NAME):$(TAG)
```

Usage:
```bash
make docker-login        # Login once
make docker-build-push   # Build and push
make docker-pull         # Pull from registry
make docker-run-remote   # Run from registry
```

---

## 🤖 GitHub Actions (Automated CI/CD)

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Docker Publish

on:
  push:
    branches: [main]
    tags: ['v*']
  release:
    types: [published]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Image digest
        run: echo ${{ steps.meta.outputs.digest }}
```

**Features:**
- ✅ Uses built-in `GITHUB_TOKEN` (no manual tokens!)
- ✅ Automatic versioning from git tags
- ✅ Caching for faster builds
- ✅ Runs on: push to main, tags, releases

---

## 🧪 Complete Testing Pipeline

### Step 1: Local Build Test
```bash
# Build locally
docker build -t city-helper-backend:test .

# Run and test
docker run -d --name test-backend -p 3001:3001 city-helper-backend:test
sleep 5
curl http://localhost:3001/health
docker stop test-backend && docker rm test-backend
```

### Step 2: Push to Registry
```bash
# Login (if not already)
gh auth token | docker login ghcr.io -u mirongit --password-stdin

# Tag for registry
docker tag city-helper-backend:test ghcr.io/miron-s-playground/city-helper-ai-backend:test

# Push
docker push ghcr.io/miron-s-playground/city-helper-ai-backend:test
```

### Step 3: Pull and Run from Registry
```bash
# Clean local images (to verify pull)
docker rmi city-helper-backend:test
docker rmi ghcr.io/miron-s-playground/city-helper-ai-backend:test

# Pull from registry
docker pull ghcr.io/miron-s-playground/city-helper-ai-backend:test

# Run from registry
docker run -d --name test-remote -p 3001:3001 \
  ghcr.io/miron-s-playground/city-helper-ai-backend:test

# Test
sleep 5
curl http://localhost:3001/health

# View logs
docker logs test-remote

# Stop and clean
docker stop test-remote && docker rm test-remote
```

### Step 4: Test with Environment Variables
```bash
docker run -d --name test-env -p 3001:3001 \
  -e APP_ENV=production \
  -e APP_DEBUG=false \
  ghcr.io/miron-s-playground/city-helper-ai-backend:test

curl http://localhost:3001/health
docker logs test-env
docker stop test-env && docker rm test-env
```

---

## 🔒 Security and Privacy

### Make Image Private

**By default, images are PRIVATE in GHCR!** ✅

To verify/change:
1. GitHub → Packages → city-helper-ai-backend
2. Package settings → Change visibility
3. Keep as "Private" ✅

### Access Control

**Who can pull:**
- ✅ You (owner)
- ✅ Collaborators on the repo
- ✅ GitHub Actions (with GITHUB_TOKEN)
- ❌ Public (if private)

**Grant access to others:**
1. GitHub → Packages → city-helper-ai-backend
2. Package settings → Manage Actions access
3. Add repositories/users

---

## 📊 Monitoring and Maintenance

### View Image Details
```bash
# List tags
gh api /user/packages/container/city-helper-ai-backend/versions

# View image info
docker inspect ghcr.io/miron-s-playground/city-helper-ai-backend:latest
```

### Clean Old Images

**GitHub Web UI:**
1. GitHub → Packages → city-helper-ai-backend
2. Package settings → Manage versions
3. Delete old versions

**Automated cleanup** (add to workflow):
```yaml
- name: Delete old images
  uses: actions/delete-package-versions@v4
  with:
    package-name: city-helper-ai-backend
    package-type: container
    min-versions-to-keep: 10
    delete-only-untagged-versions: true
```

---

## 🚀 Production Deployment

### Deploy to Server

```bash
# On production server
docker login ghcr.io -u mirongit -p YOUR_TOKEN

# Pull latest
docker pull ghcr.io/miron-s-playground/city-helper-ai-backend:latest

# Run
docker run -d --name city-helper-prod \
  --restart unless-stopped \
  -p 3001:3001 \
  -e APP_ENV=production \
  --env-file /path/to/.env \
  ghcr.io/miron-s-playground/city-helper-ai-backend:latest
```

### With Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: ghcr.io/miron-s-playground/city-helper-ai-backend:latest
    container_name: city-helper-backend
    ports:
      - "3001:3001"
    environment:
      - APP_ENV=production
    env_file:
      - .env.production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## ⚡ Best Practices

✅ **DO:**
- Use GitHub CLI for local development (OAuth)
- Use `GITHUB_TOKEN` in Actions (automatic)
- Use fine-grained tokens if manual tokens needed
- Tag images with versions (`v1.0.0`)
- Keep images private by default
- Set expiration dates on tokens
- Use Docker layer caching (GitHub Actions)

❌ **DON'T:**
- Don't use classic PATs (deprecated)
- Don't commit tokens to repo
- Don't use `latest` tag in production
- Don't store secrets in Docker images
- Don't give tokens excessive permissions

---

## 🐛 Troubleshooting

### "Authentication failed"
```bash
# Check if logged in
docker login ghcr.io

# Re-login with GitHub CLI
gh auth token | docker login ghcr.io -u mirongit --password-stdin
```

### "Permission denied"
- Check fine-grained token has "packages: write" permission
- Check repository access in token settings
- Verify you're owner/collaborator of the repo

### "Image not found"
- Verify image name: `ghcr.io/<owner>/<repo>:<tag>`
- Check if image is private (need authentication)
- Check if tag exists: `docker image ls | grep ghcr`

### "Rate limit exceeded" (Docker Hub)
Not an issue with GHCR! GitHub has much higher limits. ✅

---

## 📝 Summary

**For local development:**
```bash
brew install gh
gh auth login
gh auth token | docker login ghcr.io -u mirongit --password-stdin
```

**For CI/CD:**
Use built-in `GITHUB_TOKEN` in Actions (automatic, no setup needed!)

**For team:**
Share access via GitHub repo collaborators (automatic access to packages)

**Security:**
✅ OAuth (GitHub CLI) - most secure
✅ Fine-grained tokens - granular control
✅ Private by default
✅ Audit logs
