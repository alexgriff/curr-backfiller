import requests
import base64
import json
import os
import subprocess
from git import Repo, Git, GitCommandError

# CONSTANTS
SOLUTION_TAG = "__SOLUTION__"
CURRICULUM_BRANCH = "curriculum"
UNSYNCED_COMMIT_MSG = f" ALERT: Cell Mismatch. Auto-create {CURRICULUM_BRANCH} branch from solution + master"
SYNCED_COMMIT_MSG = f"Auto-create {CURRICULUM_BRANCH} branch from master + solution"
LESSON_COMMIT_MSG = f"Auto-create {CURRICULUM_BRANCH} branch from master"

# CHANGE THESE
owner= "learn-co-curriculum" # github org or username
path_to_labs = os.path.join(os.path.realpath(".."), "first-15-lessons") # path to lesson repos
oauth_token = os.environ['OAUTH_TOKEN'] # github oauth token value



# FUNCTIONS
# =========

def create_merged_notebook(lab):
    # strip leading numbers
    lab = lab[4:]
    master_content = get_notebook_contents(lab)
    sol_content = get_notebook_contents(lab, branch="solution")
    master_cells = get_cells(master_content)
    sol_cells = get_cells(sol_content)

    if len(master_cells) == 0: return (None, None)

    if is_synced_lab(master_cells, sol_cells):
        commit_msg = SYNCED_COMMIT_MSG
        cells = merge_cells_synced(master_cells=master_cells, sol_cells=sol_cells)
    else:
        log_lesson(master_cells, sol_cells)
        commit_msg = UNSYNCED_COMMIT_MSG if len(sol_cells) > 0 else LESSON_COMMIT_MSG
        cells = merge_cells_unsynced(master_cells=master_cells, sol_cells=sol_cells)


    master_content.update({"cells": cells})
    return (json.dumps(master_content), commit_msg)

def get_notebook_contents(lab, branch="master"):
    print(lab)
    headers = {"Authorization": f"token {oauth_token}"}
    response = requests.get(f"http://api.github.com/repos/{owner}/{lab}/contents/index.ipynb?ref={branch}", headers=headers)

    if response.status_code == 200:
        encoded_content = json.loads(response.content)['content']
        return json.loads(base64.b64decode(encoded_content))
    else:
        print("BAD API RESPONSE:")
        print(f"{response.content}\n")
        return None


def get_cells(content):
    if content:
        return content["cells"]
    else:
        return []

def is_markdown(cell):
    return cell["cell_type"] == "markdown"

def contains_tag(line):
    return SOLUTION_TAG in line.strip().split(" ")

def is_synced_lab(master_cells, sol_cells):
    master_md = [cell for cell in master_cells if is_markdown(cell)]
    sol_md = [cell for cell in sol_cells if is_markdown(cell)]

    return master_md == sol_md

def is_tagged_cell(cell):
    if cell["cell_type"] != "code":
        return False
    # does any line of the cell have the SOLUTION tag anywhere in it
    found_tag = [True for line in cell["source"] if contains_tag(line)]

    return bool(len(found_tag))


def tag_cell(cell):
    if not is_tagged_cell(cell):
        source = [f"# {SOLUTION_TAG} \n"] + cell["source"]
        cell.update({"source": source})

    return cell

def get_md_indices(cells):
    return [idx for idx, cell in enumerate(cells) if is_markdown(cell)]

def merge_cells_unsynced(master_cells = [], sol_cells = []):
    cells = []

    while (len(master_cells) or len(sol_cells)):
        m = master_cells.pop(0) if len(master_cells) else None
        s = sol_cells.pop(0) if len(sol_cells) else None
        if m: cells.append(m)
        if s and s["cell_type"] == "code":
            tagged = tag_cell(s)
            cells.append(tagged)

    return cells

def merge_cells_synced(master_cells = [], sol_cells = []):
    cells = []
    master_md_idx = get_md_indices(master_cells)
    sol_md_idx = get_md_indices(sol_cells)

    for i, m_idx in enumerate(master_md_idx):
        # exit if on the last md cell because there is no next cell
        if (i + 1) == len(master_md_idx):
            continue

        cell = master_cells[m_idx]

        cells.append(cell)

        # Get code blocks prior to next markdown cell from both branches
        # master
        for code_idx in range(master_md_idx[i] + 1, master_md_idx[i+1]):
            cells.append(master_cells[code_idx])
        # solution
        for sol_code_idx in range(sol_md_idx[i] + 1, sol_md_idx[i+1]):
            tagged_cell = tag_cell(sol_cells[sol_code_idx])
            cells.append(tagged_cell)


    # concat whatever is left
    master_last_index = master_md_idx[-1]
    sol_last_index = sol_md_idx[-1]

    trailing_cells = merge_cells_unsynced(master_cells = master_cells[master_last_index:], sol_cells = sol_cells[sol_last_index:])
    cells += trailing_cells
    return cells


def log_lesson(master_cells, sol_cells):
    log = open("logs.txt", "a")
    m_md = ["\n".join(cell["source"] for cell in master_cells if is_markdown(cell)]
    s_md = ["\n".join(cell["source"] for cell in sol_cells if is_markdown(cell)]

    diff = list(set(m) - set(s))
    formatted_diff = [f"{url}: {tag_branch(cell, m, s)}: {cell[0:25]}" for cell in diff]

    if len(diff):
        for l in formatted_diff:
            log.write(l)
    else:
        log.write(f"{url}: MASTER/SOL length mismatch")

    log.close()

# RUN
# =========

git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd)
old_cwd = os.getcwd()


labs = os.listdir(path_to_labs)
mismatches = []


for lab in labs:
    # create new json
    merged_nb_json, commit_msg = create_merged_notebook(lab)

    if merged_nb_json:
        # cd into repo
        os.chdir(f"{path_to_labs}/{lab}")
        cwd = os.getcwd()
        repo = Repo(cwd)
        git = repo.git

        if commit_msg == UNSYNCED_COMMIT_MSG:
            mismatches.append(repo.remotes.origin.url)

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
        git.add(os.path.realpath("."))
        try:
            git.commit("-m", commit_msg)
            print(f"Added Commit: {repo.commit()}")
        except GitCommandError:
            print("Nothing to commit")

        print(f"pushing to remote {CURRICULUM_BRANCH} branch for {lab}")
        repo.git.push("origin", CURRICULUM_BRANCH)

        # clean up
        git.checkout("master")
        os.chdir(old_cwd)
