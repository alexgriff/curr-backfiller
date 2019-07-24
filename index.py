import requests
import base64
import json

solution_tag = "__SOLUTION__"

labs = [
 "dsc-intro-to-sets-lab",
 "dsc-permutations-and-factorials-lab",
 "dsc-intro-to-probability-lab",
 "dsc-combinations-lab"
]

# FUNCTIONS
def create_merged_notebook(lab):
    master_content = get_notebook_contents(lab)
    sol_content = get_notebook_contents(lab, branch="solution")

    cells = merge_cells(master_cells = master_content["cells"], sol_cells = sol_content["cells"])

    master_content.update({"cells": cells})

    f = open(f"{lab}.ipynb", "w")
    f.write(json.dumps(master_content))
    f.close()

def get_notebook_contents(lab, branch="master"):
    response = requests.get(f"http://api.github.com/repos/alexgriff/{lab}/contents/index.ipynb?ref={branch}")
    encoded_content = json.loads(response.content)['content']
    return json.loads(base64.b64decode(encoded_content))


def tag_cell(cell):
    source = [f"# {solution_tag} \n"] + cell["source"]
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

for lab in labs:
    create_merged_notebook(lab)
