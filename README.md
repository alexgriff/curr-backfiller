# INSTRUCTIONS

Run `python index.py` from the root of this project

edit the variables at the top of the file

```
# CHANGE THESE
owner="alexgriff"
path_to_labs = os.path.join(os.path.realpath(".."), "labs")
```
Here, for example, there is a directory called `labs` one level above this project.

The `labs` directory contains local repos where the remote live at `github.com/alexgriff/<name-of-repo>`


## TODO
* configure Authentication Headers & SSH so can work for learn-co-curriculm org repos that may be private. Won't rate limit API, etc.
* make it 'do nothing' on a repo without a solution branch (ie not a lab)
