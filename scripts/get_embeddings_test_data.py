import json
from collections import Counter
import math
import random
import pandas as pd

training_samples = 100000

def counter_cosine_similarity(dep_list1, dep_list2):
    if len(dep_list1) == 0 or len(dep_list2) == 0:
      return 0

    dep1_cnts = Counter(dep_list1)
    dep2_cnts = Counter(dep_list2)

    # convert to word-vectors
    dependencies  = list(dep1_cnts.keys() | dep2_cnts.keys())
    dep1_vect = [dep1_cnts.get(dependency, 0) for dependency in dependencies]       
    dep2_vect = [dep2_cnts.get(dependency, 0) for dependency in dependencies]

    # find cosine
    len_a  = sum(av*av for av in dep1_vect) ** 0.5             
    len_b  = sum(bv*bv for bv in dep2_vect) ** 0.5             
    dot    = sum(av*bv for av,bv in zip(dep1_vect, dep2_vect)) 
    return dot / (len_a * len_b)   

gh_data = None

with open('../data/processed_data.json', 'r', encoding='utf8') as f:
  gh_data = json.load(f)

deps = gh_data['dependencyMap']

populated_deps = {}

all_dependencies = set()
for repo, dep in deps.items():
    if len(dep) > 0:
        populated_deps[repo] = dep
        for el in dep:
            all_dependencies.add(el)

deps = populated_deps

all_dependencies_json = {}
all_dependencies_string_lookup = {}

cnt = 0
for dep in list(all_dependencies):
    all_dependencies_json[cnt] = dep
    all_dependencies_string_lookup[dep] = cnt
    cnt+=1

int_deps = {}
for repo, dep in deps.items():
    new_dep = []
    for el in dep:
        new_dep.append(all_dependencies_string_lookup[el])
    int_deps[repo] = new_dep

deps = int_deps

train_set = []

for i in range(0,training_samples):
  repo1 = random.choice(list(deps.keys()))
  repo2 = random.choice(list(deps.keys()))
  result = counter_cosine_similarity(deps[repo1], deps[repo2])
  train_set.append((deps[repo1], deps[repo2], result))

df = pd.DataFrame(train_set)

df.to_csv("../data/embeddings_train_data.csv",index=False)


with open("../data/all_deps.json", "w", encoding='utf8') as outfile:
    json.dump(all_dependencies_json, outfile)