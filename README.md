# INSTRUCTIONS

Run `python index.py` from the root of this project. The assumption is there is a folder of repositories to be updated that lives elsewhere

edit the variables at the top of the file

```
# CHANGE THESE
owner="alexgriff" # github org or username
path_to_labs = os.path.join(os.path.realpath(".."), "labs") # path to lesson repos
oauth_token = os.environ['OAUTH_TOKEN'] # github oauth token value
```
Here, for example, there is a directory called `labs` one level above this project.

The `labs` directory contains local repos where the remote live at `github.com/alexgriff/<name-of-repo>`

In this example, there is an environment variable called `OAUTH_TOKEN` that holds a [GitHub Oauth token](https://help.github.com/en/articles/git-automation-with-oauth-tokens). Feel free to paste a string here directly as long as it's not pushed to GitHub.


## TODO
* configure ~Authentication Headers~ & ~SSH~(i think????) so can work for learn-co-curriculm org repos that may be private. Won't rate limit API, etc.
* ~make it 'do nothing' on a repo without a solution branch (ie not a lab)~
