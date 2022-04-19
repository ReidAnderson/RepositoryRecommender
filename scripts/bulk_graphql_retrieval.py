import requests
import json
import pandas as pd
import time

debug = False

def get_repo_query(query_name:str, repo_owner: str, repo_name: str) -> str:
    return "%s: repository(owner:\\\"%s\\\", name:\\\"%s\\\") {   object(expression: \\\"master:README.md\\\") {     ... on Blob {   text  }  }, languages(first:50) { edges { size, node { name } } }, stargazerCount, forkCount, nameWithOwner, branchProtectionRules(first:20) { edges { node { requiredStatusChecks { app {name, description}, context }, requiredStatusCheckContexts } } }, dependencyGraphManifests(first: 30) {      edges {        node {          filename          dependenciesCount dependencies(first: 30) { edges { node {  packageName  } } }      }      }    }  }"%(query_name,repo_owner,repo_name)

def get_http_payload(graphql_queries: list[str]) -> str:
    payload: str = "{\"query\":\" query {"

    for query in graphql_queries:
        payload += query

    payload += "}\",\"variables\":{}}"

    return payload

secrets = None

most_starred_df = pd.read_csv('../data/100kMostWatchedFor2021.csv')

with open('../data/secrets.json', 'r') as f:
    secrets = json.load(f)

print(secrets)

request_text = "{\"query\":\"query {  NetPatch: repository(owner:\\\"ReidAnderson\\\", name:\\\"NetPatch\\\") {   object(expression: \\\"master:README.md\\\") {     ... on Blob {   text  }  }, languages(first:50) { edges { size, node { name } } }, stargazerCount, forkCount, nameWithOwner, branchProtectionRules(first:20) { edges { node { requiredStatusChecks { app {name, description}, context }, requiredStatusCheckContexts } } }, dependencyGraphManifests(first: 30) {      edges {        node {          filename          dependenciesCount dependencies(first: 30) { edges { node {  packageName  } } }      }      }    }  }}\",\"variables\":{}}"

# print(request_text)
# print("{\"query\":\" query {" + get_repo_query("NetPatch", "ReidAnderson", "NetPatch") + "} \",\"variables\":{}}")
# print(get_http_payload(get_repo_query("NetPatch", "ReidAnderson", "NetPatch")))

queries: list[str] = []

for i in range(1,10):
    queries.append(get_repo_query("NetPatch"+str(i), "ReidAnderson", "NetPatch"))

# print("-------------------------------------")
# print(get_http_payload(queries))

headers = {
    "Authorization": f"bearer {secrets['githubPat']}",
    "Accept": "application/vnd.github.hawkgirl-preview+json"
}

http_payload: str = get_http_payload(queries)

queries = []
for idx, row in most_starred_df.iterrows():
    repo_path = (str(row['name'])).split('/')
    owner = repo_path[0]
    repo = repo_path[1]
    queries.append(get_repo_query(f"repo{idx}", owner, repo))

step_size = 6
for i in range(0, len(queries), step_size):
    try:
        queries_step = queries[i:i+step_size]
        http_payload = get_http_payload(queries_step)

        if debug:
            print('-------------------------')
            print(http_payload)
            print('-------------------------')

        response = requests.post('https://api.github.com/graphql', data = http_payload, headers = headers)

        if response.status_code != 200:
            response = requests.post('https://api.github.com/graphql', data = http_payload, headers = headers)

            if response.status_code != 200:
                raise Exception('Something non-200 returned' + response.text)

        responseJson = json.loads(response.text)
        with open(f"../output/graphql_result_{i}.json", "w", encoding='utf-8') as outfile:
            json.dump(responseJson, outfile)

        time.sleep(1)
    except Exception:
        error = "Exception thrown on request"
        with open(f"../output/graphql_result_{i}.json", "w", encoding='utf-8') as outfile:
            json.dump(error, outfile)

# response = requests.post('https://api.github.com/graphql', data = http_payload, headers = headers)

# if response.status_code != 200:
#     raise Exception('Something non-200 returned')

# responseJson = json.loads(response.text)
# print(responseJson)

