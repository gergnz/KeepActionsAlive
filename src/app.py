from github import Github
import boto3
import json
import os
import requests


def get_params():
    """
    Retrieve environment variables
    """
    pat_name = os.getenv("PAT_SECRET_NAME")
    pat = get_pat(pat_name)

    return pat


def get_pat(pat_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=pat_name)
    secret_string = json.loads(response["SecretString"])

    return secret_string["PAT"]

def get_user_repos(gh):
    """
    Get all repos for an organization
    """
    repos = []

    user_repos = gh.get_user().get_repos(type="owner")
    repos = [r for r in user_repos if not r.fork and not r.archived]

    return repos

def get_workflows(repos):
    """
    Get all the workflows with a `disabled_inactivity` state.
    """
    disabled_workflows = []

    for repo in repos:
        workflows_to_enable = [
            w for w in repo.get_workflows() if w.state == "active"
        ]

        disabled_workflows += workflows_to_enable

    return disabled_workflows


def disable_enable_workflows(pat, workflows):
    """
    Enable all the workflows.
    """
    for workflow in workflows:
        disable_url = f"{workflow.url}/disable"
        enable_url = f"{workflow.url}/enable"
        header = {"Authorization": f"Bearer {pat}"}
        requests.put(disable_url, headers=header)
        requests.put(enable_url, headers=header)


def lambda_handler(event, context):
    """
    Enable all inactive workflows.
    """
    pat = get_params()

    gh = Github(login_or_token=pat)

    repos = get_user_repos(gh)
    workflows = get_workflows(repos)
    disable_enable_workflows(pat, workflows)

    return {"statusCode": 200}

lambda_handler(1,1)
