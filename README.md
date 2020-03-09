# Pulumi AWS Tracking Pipeline

This project contains a Pulumi component named `nuage:aws:Analytics`.  The component
creates Pinpoint application which pushes analytic events into an S3 bucket via a
Kinesis Firehose.

* The `Analytics.py` file contains the `nuage:aws:Analytics` component.
* The `__main__.py` file contains an example Pulumi program which deploys an `Analytics`
    component.
* The `example` folder contains an Amplify website which sends analytics events to a
    Pinpoint application.


## Getting started

You need Python 3 (preferably 3.8) and Pulumi (preferably 1.12.0) installed to start working on this project.

In order to install your virtualenv, just go to the root of the project and:
```bash
make install
```

## IDE

Nuage recommends [Visual Studio Code](https://code.visualstudio.com/download) to work on this project, and some default settings have been configured in the [.vscode/settings.json](.vscode/settings.json).

These settings merely enforce the code-quality guidelines defined below, but if you use another IDE it's probably worth taking a quick look at it to ensure compliance with the standard.

By default, we recommend:
1. Putting your virtualenv in a `venv` folder at the project root
2. Using a `.env` file to define your environment variables (cf. [python-dotenv](https://pypi.org/project/python-dotenv/))

## Code quality

This project has opinionated code-quality requirements:
- Code formatter: [black](https://black.readthedocs.io/en/stable/)
- Code linter: [pylint](https://www.pylint.org)
- Code style guidelines: [flake8](https://flake8.pycqa.org/en/latest/)

All of these tools are enforced at the commit-level via [pre-commit](https://pre-commit.com)

You can run the following command to apply code-quality to your project at any point:
```bash
make quality
```

Code quality configuration files:
- IDE-agnostic coding style settings are set in the [.editorconfig](.editorconfig) file
- Python-related settings are set in the [setup.cfg](setup.cfg) file
- Pre-commit-related settings are set in the [.pre-commit-config.yaml](.pre-commit-config.yaml) file

## Deploying the example

The example component can be deployed as a normal Pulumi program:

```
pulumi up
```
