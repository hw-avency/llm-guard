# Build and deploy LLM Guard API to Google Cloud Run

This guide shows how to build the `llm_guard_api` container image and deploy it to Google Cloud Run.

## 1) Prerequisites

- A Google Cloud project with billing enabled.
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated.
- Docker (optional for local image testing).
- Required roles for your user account:
  - `roles/run.admin`
  - `roles/iam.serviceAccountUser`
  - `roles/cloudbuild.builds.editor`
  - `roles/artifactregistry.admin` (or repository-scoped writer permissions)

## 2) Set environment variables

```bash
export PROJECT_ID="YOUR_GCP_PROJECT_ID"
export REGION="us-central1"
export REPOSITORY="llm-guard"
export IMAGE="llm-guard-api"
export SERVICE="llm-guard-api"
```

## 3) Enable required APIs

```bash
gcloud config set project "$PROJECT_ID"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

## 4) Create Artifact Registry repository

```bash
gcloud artifacts repositories create "$REPOSITORY" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Docker images for LLM Guard"
```

If the repository already exists, this command can be skipped.

## 5) Build and push the image with Cloud Build

Run this from the repository root (`/workspace/llm-guard`):

```bash
gcloud builds submit \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest" \
  ./llm_guard_api
```

Yes — you can also fix this cleanly with a `cloudbuild.yaml`.
This repository now includes `cloudbuild.yaml` with:

- a Docker build step for `./llm_guard_api`, and
- `options.defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET`.

That logs option satisfies Cloud Build requirements when `--service-account` is used.

```bash
gcloud builds submit \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --config cloudbuild.yaml \
  --substitutions _IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest" \
  --service-account "projects/$PROJECT_ID/serviceAccounts/YOUR_BUILD_SA@$PROJECT_ID.iam.gserviceaccount.com" \
  .
```

Alternative valid log settings (if you do not use `defaultLogsBucketBehavior`) are:

- `--gcs-log-dir="gs://YOUR_LOGS_BUCKET/cloudbuild-logs"` (explicit logs bucket), or
- `--logging=CLOUD_LOGGING_ONLY` (or `--logging=NONE`).

## 6) Deploy to Cloud Run

```bash
gcloud run deploy "$SERVICE" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --platform managed \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest" \
  --allow-unauthenticated \
  --port 8000 \
  --cpu 1 \
  --memory 1Gi \
  --timeout 300
```

## 7) Verify deployment

```bash
gcloud run services describe "$SERVICE" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --format='value(status.url)'
```

Then test the health endpoint:

```bash
curl "$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')/health"
```

## 8) Optional: deploy with environment variables

If you need runtime configuration, pass environment variables at deploy time:

```bash
gcloud run deploy "$SERVICE" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest" \
  --set-env-vars "LOG_LEVEL=INFO"
```

## 9) Optional: local container test

```bash
docker build -t llm-guard-api:local ./llm_guard_api
docker run --rm -p 8000:8000 llm-guard-api:local
curl http://localhost:8000/health
```
