### Project Setup

Project dependencies can be installed with `venv`:

```
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Exact commands may vary depending on platform.

Ensure the `PYTHONPATH` includes the `src/` directory.

### Running the tests

Install dev dependencies:

```pip install -r requirements-dev.txt```

Run the tests:

```pytest```

For coverage, instead run:

```
coverage run --source=src -m pytest
coverage report -m
```

### Deploying to AWS

Requires `7z` and `aws` CLI utilities. Run from the project root. Only tested for Windows + Git Bash.
Needs IAM access to deploy to Lambda.

```./deploy/deploy.sh```

The script packages all the necessary files into a zip archive and deploys to AWS.
Most notably, all the Python dependencies are installed into the bundle.