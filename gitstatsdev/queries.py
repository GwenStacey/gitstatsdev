repo_query = '''
    query ($owner: String!, $name: String!){
        repository(owner: $owner, name: $name) {
            name
            owner {
                login
                }
            description
            primaryLanguage {
                name
                }
            stars: stargazers {
                totalCount
                }
            forks: forkCount
            totalIssues: issues {
            totalCount
                }
            openIssues: issues (states: [OPEN]) {
                totalCount
                }
            closedIssues: issues (states: [CLOSED]) {
                totalCount
                }
            vulnerabilityAlerts {
                totalCount
                }
            totalPRs: pullRequests {
                totalCount
                }
            openPRs: pullRequests (states: [OPEN]) {
                totalCount
                }
            mergedPRs: pullRequests (states: [MERGED]) {
                totalCount
                }
            closedPRs: pullRequests (states: [CLOSED]) {
                totalCount
                }
            createdAt
            updatedAt
            diskUsage
        }
    }
    '''

initial_PR_query = '''
    query ($owner: String!, $name: String!){
        repository(owner: $owner, name: $name) {
            pullRequests(first: 50) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    id
                    state
                    createdAt
                    closedAt
                    title
                    bodyText
                    author {
                        login
                    }
                    participants {
                        totalCount
                    }
                    comments {
                        totalCount
                    }
                    reactions {
                        totalCount
                    }
                    commits {
                        totalCount
                    }
                    changedFiles
                    additions
                    deletions
                }
            }
        }
    }
    '''

cont_PR_query = '''
    query ($owner: String!, $name: String!, $cursor: String!) {
        repository(owner: $owner, name: $name) {
            pullRequests(first: 50 after: $cursor) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    id
                    state
                    createdAt
                    closedAt
                    title
                    bodyText
                    author {
                        login
                    }
                    participants {
                        totalCount
                    }
                    comments {
                        totalCount
                    }
                    reactions {
                        totalCount
                    }
                    commits {
                        totalCount
                    }
                    changedFiles
                    additions
                    deletions
                }
            }
        }
    }
    '''
