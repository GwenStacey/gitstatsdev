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
            pullRequests (last: 50) {
                nodes {
                author {
                    login
                    }
                state
                createdAt
                closedAt
                changedFiles
                additions
                deletions
                }
            }
        }
    }
    '''
