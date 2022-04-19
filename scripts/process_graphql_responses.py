import os
import json

def get_unique_dependencies(dependencyGraphManifests):
    total_deps = 0
    total_unique_deps = 0
    deps = set()

    for manifest in dependencyGraphManifests:
        if manifest is None or 'node' not in manifest or manifest['node'] is None or 'dependenciesCount' not in manifest['node']:
            continue

        total_deps += manifest['node']['dependenciesCount']

        for dependency in manifest['node']['dependencies']['edges']:
            deps.add(dependency['node']['packageName'])

    total_unique_deps = len(deps)
    return list(deps)

allowed_languages = ['c#', 'typescript', 'javascript', 'go', 'ruby', 'python', 'java', 'php']

directory_path: str = '../output'
process_limit: int = 2000

language_map = {
    'c#': 0,
    'typescript': 1,
    'javascript': 1,
    'go': 2,
    'ruby': 3,
    'python': 4,
    'java': 5,
    'php': 6
}
name_map = {}
dependency_map = {}
repo_specific_data = {}

cnt = 0
repos_per_file = 5
error_files = 0
error_repos = 0
filtered_repos = 0
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    output_json = None

    if not os.path.isfile(file_path) or (process_limit is not None and cnt > process_limit):
        continue

    with open(file_path, 'r', encoding='utf8') as f:
        output_json = json.load(f)

    if isinstance(output_json, str) or 'data' not in output_json.keys():
        error_files += 1
        continue

    repos = output_json['data'].keys()

    for repo in repos:
        repo_data = output_json['data'][repo]
        if repo_data is None or 'languages' not in repo_data or repo_data['languages'] is None:
            error_repos += 1
            continue

        has_valid_language = False
        for language in repo_data['languages']['edges']:
            if language['node']['name'].lower() in allowed_languages:
                has_valid_language = True

        if not has_valid_language:
            filtered_repos += 1
            continue

        if repo_data['dependencyGraphManifests'] is None or 'edges' not in repo_data['dependencyGraphManifests']:
            error_repos += 1
            continue

        name_map[repo] = repo_data['nameWithOwner']
        dependency_map[repo] = get_unique_dependencies(repo_data['dependencyGraphManifests']['edges'])

    cnt += 1

print(f'Errored on {error_files} files. (implies {error_files * repos_per_file} repos)')
print(f'Errored on {error_repos} additional repos.')
print(f'Filtered out {filtered_repos} additional repos.')
print(f'Successfully retrieved data for {len(dependency_map.keys())}')

result = {
    'repoErrors': error_files * repos_per_file + error_repos,
    'repoFilters': filtered_repos,
    'repoTotalWithDependencies': len(dependency_map.keys()),
    'nameMap': name_map,
    'dependencyMap': dependency_map
}

with open("../data/processed_data.json", "w", encoding='utf8') as outfile:
    json.dump(result, outfile)
