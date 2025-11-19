### Deploying to AWS

Requires `7z` and `aws` CLI utilities. Run from the project root. Only tested for Windows + Git Bash.
Needs IAM access to deploy to Lambda.

```./deploy/deploy.sh```

The script packages all the necessary files into a zip archive and deploys to AWS.
Most notably, all the Python dependencies are installed into the bundle.