# `curriculum-team` Branch Backfiller

Running this script with a given directory of repositories will create a new remote branch called `curriculum-team` on each repository with interleaves solution and master code cells.

The existing master and solution branches remain unchanged.

#### Test Outputs
* [private lab on learn-co-curriculum](https://github.com/learn-co-curriculum/alex-branch-test-dsc-bernoulli-and-binomial-distribution-lab/tree/curriculum-team)
* [lab on learn-co-curriculum](https://github.com/learn-co-curriculum/alex-branch-test-dsc-regression-model-validation-lab/tree/curriculum-team)
* [non-lab on learn-co-curriculum](https://github.com/learn-co-curriculum/alex-branch-test-dsc-regression-model-validation) _included in test input, behavior for a repo with no solution branch is to do nothing_

See more example notebook files in the `/examples` dir

## INSTRUCTIONS
Run `python index.py` from the root of this project. The assumption is there is a folder of repositories to be updated that lives elsewhere

To run, change the variables at the top of the file as needed

```
# CHANGE THESE
owner="learn-co-curriculum" # github org or username
path_to_labs = os.path.join(os.path.realpath(".."), "labs") # path to lesson repos
oauth_token = os.environ['OAUTH_TOKEN'] # github oauth token value
```
Here, for example, there is a directory called `labs` one level above this project.

The `labs` directory contains local repos where the remote live at `github.com/learn-co-curriculm/<name-of-repo>`

In this example, there is an environment variable called `OAUTH_TOKEN` that holds a [GitHub Oauth token](https://help.github.com/en/articles/git-automation-with-oauth-tokens). Feel free to paste a string here directly as long as it's not pushed to GitHub.

## TODO
* ~configure Authentication Headers & SSH (i think????) so can work for learn-co-curriculm org repos that may be private. Won't rate limit API, etc.~
* ~make it 'do nothing' on a repo without a solution branch (ie not a lab)~
