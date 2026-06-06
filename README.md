# start the server

fastapi dev <location_file>

 Step 1 — Build the image locally

  From inside /Users/shubhamupadhyay/Downloads/rec
  eipt/fastapi:

  docker build --platform linux/amd64 -t
  receipt-api .

  Why --platform linux/amd64? App Runner runs on
  x86_64. If you're on an Apple Silicon Mac
  (M1/M2/M3), Docker would build an arm64 image by
   default and App Runner would refuse to run it.
  This flag forces x86_64.

  Step 2 — Test it locally

  docker run --rm -p 8080:8080 --env-file .env
  receipt-api

  - --rm removes the container when you stop it
  (no clutter)
  - -p 8080:8080 maps container port → your laptop
   port
  - --env-file .env injects your GEMINI_API_KEY
  from .env

  Then in another terminal (or browser):
  curl http://localhost:8080/
  # expect: {"message":"hello world"}
  
  curl -X POST http://localhost:8080/summarize/ \
    -H "Content-Type: application/json" \
    -d '{"text":"FastAPI is a modern Python web 
  framework for building APIs."}'
  
  Stop it with Ctrl+C. If both calls work, the
  image is good.

  Step 3 — Create the ECR repository (one-time)

  In the AWS Console:
  1. Go to ECR → Repositories → Create repository
  2. Visibility: Private
  3. Name: receipt-api
  4. Leave the rest as default → Create

  Or via CLI (pick your region, e.g. ap-south-1
  for Mumbai):
  aws ecr create-repository \
    --repository-name receipt-api \
    --region ap-south-1

  After creation, ECR shows you the repo URI:
  <account-id>.dkr.ecr.<region>.amazonaws.com/rece
  ipt-api
  Copy this — you'll need it.
  
  Step 4 — Authenticate Docker to ECR

  aws ecr get-login-password --region ap-south-1 \
    | docker login --username AWS --password-stdin
   <account-id>.dkr.ecr.ap-south-1.amazonaws.com

  This logs your Docker CLI into ECR for ~12
  hours. You'll see Login Succeeded.

  ▎ If aws isn't installed or configured: brew 
  ▎ install awscli then aws configure (needs an 
  ▎ IAM access key with ECR permissions).

  Step 5 — Tag & push

  Docker images need a tag matching the ECR repo
  URI before they can be pushed:

  # Tag the local image with the ECR URI
  docker tag receipt-api:latest \
    <account-id>.dkr.ecr.ap-south-1.amazonaws.com/
  receipt-api:latest

  # Push it
  docker push <account-id>.dkr.ecr.ap-south-1.amaz
  onaws.com/receipt-api:latest

  You'll see layers uploading. First push is slow;
   later pushes are fast because Docker only sends
   changed layers.

  Step 6 — Verify it's in ECR

  In AWS Console → ECR → receipt-api — you'll see
  the latest tag with a digest, size, and "Pushed
  at" timestamp. Or via CLI:

  aws ecr list-images --repository-name
  receipt-api --region ap-south-1

  What's next (preview of Step 7)

  Once the image is in ECR, you go to App Runner →
   Create service, pick Container registry → 
  Amazon ECR, browse to your receipt-api:latest
  image, set port 8080, add GEMINI_API_KEY as an
  env var, and deploy. Want me to walk through
  that part now, or stop here until you've
  completed Steps 1–6?

✻ Churned for 19s

※ recap: You're deploying the FastAPI app to AWS 
  App Runner via ECR, and the Dockerfile is ready.
   Next: build it locally with `docker build 
  --platform linux/amd64 -t receipt-api .` and 
  test with `docker run --rm -p 8080:8080
  --env-file .env receipt-api`. (disable recaps in
   /config)

──────────────────────────────────────────────────
❯ walk me through step 7
──────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle)

# learn-aws
