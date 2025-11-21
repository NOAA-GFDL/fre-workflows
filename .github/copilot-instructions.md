### tips for copilot while trying to contribute
- you should be able to use `fre` and `fre-cli` to create a fully-configured workflow, you just won't be able to run it. 
- create a `fre-cli` conda environment, consult `cylc` documentation and review the `for_gh_runner/runscript.sh`, and `.github/workflows/test_cloud_runner.yaml` for how to use it to configure the workflow. 
- keep in mind you'll get errors regarding the existence of directories/files, so ignore those (or create them) as needed to fudge the validation step
- don't bother trying to `cylc play` the workflow since you do not have any data to play with. just take it to the `fre pp install` step (or `cylc install`) and figure out how to compile `flow.cylc` to analyze the `clean` task dependencies
- 
