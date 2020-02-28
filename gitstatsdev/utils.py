from datetime import datetime
from decouple import config
import pandas as pd
import requests

from .models import DB, Repo
from .queries import repo_query

SECRET = config('SECRET')
URL = 'https://api.github.com/graphql'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
SECS_PER_HOUR = 3600


def run_query(query, variables):
    r = requests.post(URL,
                      headers={'Authorization': 'token ' + SECRET, },
                      json={'query': query,
                            'variables': variables
                            })
    return r


def pull_repo(owner, name):
    variables = {'owner': owner, 'name': name}
    data = run_query(repo_query, variables).json()['data']['repository']

    data['stars'] = data['stars']['totalCount']
    data['owner'] = data['owner']['login']
    data['primaryLanguage'] = data['primaryLanguage']['name']
    data['totalIssues'] = data['totalIssues']['totalCount']
    data['openIssues'] = data['openIssues']['totalCount']
    data['closedIssues'] = data['closedIssues']['totalCount']
    data['totalPRs'] = data['totalPRs']['totalCount']
    data['openPRs'] = data['openPRs']['totalCount']
    data['mergedPRs'] = data['mergedPRs']['totalCount']
    data['closedPRs'] = data['closedPRs']['totalCount']
    data['vulnerabilityAlerts'] = data['vulnerabilityAlerts']['totalCount']

    if (data['mergedPRs'] + data['closedPRs'] != 0):
        data['PRacceptanceRate'] = data['mergedPRs'] / (data['mergedPRs'] +
                                                        data['closedPRs'])
    else:
        data['PRacceptanceRate'] = None
    data['createdAt'] = datetime.strptime(data['createdAt'],
                                          DATE_FORMAT)
    data['updatedAt'] = datetime.strptime(data['updatedAt'],
                                          DATE_FORMAT)
    data['ageInDays'] = (datetime.now().date() -
                         data['createdAt'].date()).days
    data['starsPerDay'] = data['stars'] / data['ageInDays']
    data['forksPerDay'] = data['forks'] / data['ageInDays']
    data['PRsPerDay'] = data['totalPRs'] / data['ageInDays']
    data['issuesPerDay'] = data['totalIssues'] / data['ageInDays']

    pull_requests = data['pullRequests']['nodes']
    del data['pullRequests']

    if len(pull_requests) != 0:
        pr_df = pd.DataFrame.from_records(pull_requests)
        pr_df['author'] = [author.get('login') if author is not None else ''
                           for author in pr_df['author']]
        pr_df['createdAt'] = pd.to_datetime(pr_df['createdAt'],
                                            format=DATE_FORMAT)
        pr_df['closedAt'] = pd.to_datetime(pr_df['closedAt'],
                                           format=DATE_FORMAT)

        data['uniquePRauthors'] = pr_df['author'].nunique()

        openPRs = pr_df['state'] == 'OPEN'
        if openPRs.empty:
            data['medianOpenPRhrsAge'] = None
        else:
            openPRsecsAge = (datetime.now() -
                             pr_df['createdAt']).dt.total_seconds()[openPRs]
            data['medianOpenPRhrsAge'] = openPRsecsAge.median()/SECS_PER_HOUR

        closedPRs = pr_df['state'] == 'CLOSED'
        if closedPRs.empty:
            data['medianPRhrsToClose'] = None
        else:
            PRsecsToClose = (pr_df['closedAt'] -
                             pr_df['createdAt']).dt.total_seconds()[closedPRs]
            data['medianPRhrsToClose'] = PRsecsToClose.median()/SECS_PER_HOUR

        mergedPRs = pr_df['state'] == 'MERGED'
        if mergedPRs.empty:
            data['medianPRhrsToMerge'] = None
        else:
            PRsecsToMerge = (pr_df['closedAt'] -
                             pr_df['createdAt']).dt.total_seconds()[mergedPRs]
            data['medianPRhrsToMerge'] = PRsecsToMerge.median()/SECS_PER_HOUR

    else:
        data['uniquePRauthors'] = 0
        data['medianOpenPRhrsAge'] = None
        data['medianPRhrsToClose'] = None
        data['medianPRhrsToMerge'] = None

    return data


def add_or_update_repo(owner, name):
    try:
        # Add db_repo to Repo table (or check if existing)
        repo_dict = pull_repo(owner, name)
        db_repo = Repo(owner=repo_dict['owner'],
                       name=repo_dict['name'],
                       description=repo_dict['description'],
                       primary_language=repo_dict['primaryLanguage'],
                       created_at=repo_dict['createdAt'],
                       updated_at=repo_dict['updatedAt'],
                       disk_usage=repo_dict['diskUsage'],
                       stars=repo_dict['stars'],
                       forks=repo_dict['forks'],
                       total_issues=repo_dict['totalIssues'],
                       open_issues=repo_dict['openIssues'],
                       closed_issues=repo_dict['closedIssues'],
                       total_PRs=repo_dict['totalPRs'],
                       open_PRs=repo_dict['closedPRs'],
                       merged_PRs=repo_dict['mergedPRs'],
                       closed_PRs=repo_dict['closedPRs'],
                       vulnerabilities=repo_dict['vulnerabilityAlerts'],
                       unique_PR_authors=repo_dict['uniquePRauthors'],
                       PR_acceptance_rate=repo_dict['PRacceptanceRate'],
                       median_open_PR_hrs_age=repo_dict['medianOpenPRhrsAge'],
                       median_PR_hrs_to_merge=repo_dict['medianPRhrsToMerge'],
                       median_PR_hrs_to_close=repo_dict['medianPRhrsToClose'],
                       )
        DB.session.merge(db_repo)

    except Exception as e:
        print('Error processing {} {}: {}'.format(owner, name, e))
        raise e
    else:
        DB.session.commit()


def update_all_repos():
    for repo in Repo.query.all():
        add_or_update_repo(repo.owner, repo.name)
