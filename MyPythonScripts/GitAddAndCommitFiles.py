#install gitpython --> "pip install gitpython"

#Below script is used to add multiple project folders and commit them one by one
import git
repo = git.Repo("C:\\Projects\\DOT NET") #Replace with actual folder path.
status = repo.git.status()

projList = status.splitlines()
projects = projList[5:-2]

for item in projects:
    item.strip()
    item = item.replace("\t","")
    repo.git.add(item)
    commit_message = item+" added"
    repo.git.commit(m = commit_message)
    print(commit_message)
print(projects)