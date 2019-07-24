import requests
import base64
import json
import os
import subprocess
from git import Repo, Git, GitCommandError

# CONSTANTS
SOLUTION_TAG = "__SOLUTION__"
CURRICULUM_BRANCH = "curriculum-team"

# CHANGE THESE
owner="alexgriff" # github org or username
path_to_labs = os.path.join(os.path.realpath(".."), "labs") # path to lesson repos
oauth_token = os.environ['OAUTH_TOKEN'] # github oauth token value

# FUNCTIONS
def create_merged_notebook(lab):
    master_content = get_notebook_contents(lab)
    sol_content = get_notebook_contents(lab, branch="solution")

    if sol_content:
        cells = merge_cells(master_cells = master_content["cells"], sol_cells = sol_content["cells"])

        master_content.update({"cells": cells})
        return json.dumps(master_content)
    else:
        return None

def get_notebook_contents(lab, branch="master"):
    headers = {"Authorization": f"token {oauth_token}"}
    response = requests.get(f"http://api.github.com/repos/{owner}/{lab}/contents/index.ipynb?ref={branch}", headers=headers)

    if response.status_code == 200:
        encoded_content = json.loads(response.content)['content']
        return json.loads(base64.b64decode(encoded_content))
    else:
        return None


def tag_cell(cell):
    source = [f"# {SOLUTION_TAG} \n"] + cell["source"]
    cell.update({"source": source})

    return cell

def merge_cells(master_cells = [], sol_cells = []):
    cells = []

    while (len(master_cells) or len(sol_cells)):
        m = master_cells.pop(0) if len(master_cells) else None
        s = sol_cells.pop(0) if len(sol_cells) else None
        if m: cells.append(m)
        if s and s["cell_type"] == "code":
            tagged = tag_cell(s)
            cells.append(tagged)

    return cells



# RUN
# ============================
git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd)

labs = os.listdir(path_to_labs)

for lab in labs:
    # create new json
    merged_nb_json = create_merged_notebook(lab)

    if merged_nb_json:
        # cd into repo
        os.chdir(f"{path_to_labs}/{lab}")
        cwd = os.getcwd()
        repo = Repo(cwd)
        git = repo.git

        # switch to curriculum branch if exists or create new branch
        try:
            git.checkout(CURRICULUM_BRANCH)
        except GitCommandError:
            git.checkout("HEAD", b=CURRICULUM_BRANCH)

        # write index.ipynb
        f = open(f"{cwd}/index.ipynb", "w")
        f.write(merged_nb_json)
        f.close()

        # generate markdown
        subprocess.call(["jupyter", "nbconvert", "index.ipynb",  "--to", "markdown"])
        subprocess.call(["mv", "index.md", "README.md"])


        # add, commit, push
        git.add(".")
        try:
            git.commit("-m", "AUTO: Create curriculum-team branch")
            print(f"Added Commit: {repo.commit()}")
        except GitCommandError:
            print("Nothing to commit")

        print(f"pushing to remote {CURRICULUM_BRANCH} branch for {lab}")
        repo.git.push("origin", CURRICULUM_BRANCH)

        # clean up
        git.checkout("master")
        os.chdir(os.getcwd())
    else:
        print("Skipping, No solution branch")
