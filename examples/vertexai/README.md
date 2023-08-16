# Hamilton + Vertex AI Pipelines (Google Cloud)

In this example, were going to show how to run Hamilton with VertexAI pipeline by Google. We'll present two usage patterns:
1. Use the Google AI platform autopackaging features and enable faster iteration
2. Manually define pipeline components for full visibility and control

- [**Vertex AI**](https://cloud.google.com/vertex-ai/docs/pipelines/introduction) is the suite of MLOps services from Google Cloud. Vertex AI Pipelines is based on [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/), which allows to pipelines where each step is executed in a Docker container. It is a macro-orchestration system.
- [**Hamilton**](https://github.com/dagworks-inc/hamilton) is a micro-framework to describe dataflows in Python. Its strength is expressing the flow of data & computation in a way that is straightforward to create, maintain, and reuse (much like DBT has done for SQL). It is lightweight and can be run anywhere that python runs.  It is a micro-orchestration system.

## Why both?
Vertex AI Pipelines gives you access to compute to execute your pipeline for your production system. The framework to define pipeline is design for the code to be ran in the cloud and couples the pipeline definition with the infrastructure. Vertex AI is a paid service that integrates with other MLOps services from Google such as a model registry, a feature store, or inference endpoints.  

Hamilton is an open source tool that helps developers write clean and modular data transformations. It enables more granular lineage, easier code testing and refactoring, allows for quick development iterations. It is portable and can run anywhere Python can (script, webservice, Spark, browser, etc.).

Vertex AI Pipelines is a vehicle to bring Hamilton to production. The Hamilton DAG nodes are regular Python; they have no dedicated container or overhead compared to Vertex AI components. Once you have your workflow defined with Hamilton, you can break it down into several components to make benefit of particular Vertex AI features such as retries (if you need to).

# Setup
0. Have Docker installed
1. Move to this directory `cd hamilton/examples/vertexai`
2. Create a virtual environment `python -m venv ./venv`
3. Activate the virtual environment `. venv/bin/activate`
4. Install developer requirements `pip install -r requirements-dev.txt`. Some packages required to build the pipelines aren't not required to execute them.
5. Follow the instructions to install the gcloud CLI https://cloud.google.com/sdk/docs/install
6. Authenticate with the gcloud CLI `gcloud auth login`
7. create a project or set a project `gcloud config set project {PROJECT_ID}`
8. Set region `REGION = {REGION}` ([region list](https://cloud.google.com/docs/geography-and-regions))
9. Make sure to delete cloud resources once you are done `gcloud projects delete {PROJECT_ID}` ([ref](https://cloud.google.com/resource-manager/docs/creating-managing-projects#shutting_down_projects))


# Approach 1: Autopackaged script
This approach makes use of the gcloud CLI to autopackage a single Python script as a `CustomJob` for Vertex AI Pipelines. Users will need to select a base Docker image and specify Python dependencies, or built a custom Docker image themselves (more efficient for Docker users).

Benefits:
- The script has no dependency with Vertex AI or where it is executed
- Remove the need to learn / use Kubeflow Pipelines to define jobs
- Can quickly package the script to test locally or deploy on the cloud
Limitations:
- All operations appear as a single job, limiting the retries, caching, logging, etc.

## 1.1 Local run
[Reference](https://cloud.google.com/vertex-ai/docs/training/containerize-run-code-local)
You will use the CLI command `gcloud ai custom-jobs local-run` to package the script. This has several options ([see here](https://cloud.google.com/vertex-ai/docs/training/containerize-run-code-local)). Important ones:
- `--executor-image-uri`: specify a Docker image to execute the script (can be from a local or remote registry). This should have access to Python and can be further customized to your need.
- `--output-image-uri`: the name (i.e., tag) of the Docker container that will be created locally
- `--script`: the path to the Python script to execute, relative to `--local-package-path`
- `--local-package-path`: the working directory, by default is the parent directory of the `--script` path. It copy everything it contains and automatically pickup any `requirements.txt` file to install dependencies.
- `--extra-dirs`: pass a list of comma-separated directories to included in the container
- the command accepts additional arbitrary arguments that will be passed to your script. For example `--lr=0.01` is equivalent to `python {SCRIPT.py} --lr=0.01` 

In our case, use the following:
```
gcloud ai custom-jobs local-run\
  --executor-image-uri=python:3.10-slim-bullseye\
  --local-package-path=.\
  --script=script.py\
  --output-image-uri=vertex-local-script
```

## 1.2 Remote run
[Reference](https://cloud.google.com/vertex-ai/docs/training/create-custom-job#autopackaging)
You will use the CLI command `gcloud ai custom-jobs create` to package the script. It is very similar to the local version, but requires to specify the cloud infrastructure (region, machine type, replica count). Most of the arguments passed to `local-run` should now be passed to the option `--work-pool-spec`.

:warning: this will create a Docker image in your Artifact Registry and launch a low cost 
In our case, use the following:
```
gcloud ai custom-jobs create\
  --region=us-east1\
  --display-name=hamilton-vertex-autopackaged\
  --worker-pool-spec=machine-type=c2d-standard-2,executor-image-uri=python:3.10-slim-bullseye,local-package-path=.,script=script.py
```

# Approach 2