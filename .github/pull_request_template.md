## Describe your changes

## Issue ticket number and link (if applicable)

## Checklist before requesting a review

- [ ] I ran my code
- [ ] I tried to make my code readable
- [ ] I tried to comment my code
- [ ] I wrote a new test, if applicable
- [ ] I wrote new instructions/documentation, if applicable
- [ ] I ran pytest and inspected it's output
- [ ] I ran pylint and attempted to implement some of it's feedback
- [ ] No print statements; all user-facing info uses logging module

## Manual Pipeline Run Details

The `test_cloud_runner` pipeline is not automatically associated as a required check with the PR; it must be triggered to test changes in a full post-processing run.

To trigger the manual pipeline:
1. Go to `Actions` tab
2. Choose `test_cloud_runner` on left (you should see "This workflow has a workflow_dispatch event trigger.")
3. Click the dropdown "Run workflow":

    a. If trying to merge from a branch on fre-workflows - choose branch from the first drop down, leave the next 2 inputs blank, and choose the fre-cli branch to test

    b. If trying to merge from a fre-workflows fork - input the fork name (ex: [user]/fre-workflows), input the fork's branch name, and choose the fre-cli branch to test
4. Click "Run workflow"

Note: you may need to reload the page to see your running workflow. 

**Was the manual pipeline (`test_cloud_runner`) triggered for this PR?**
- [ ] Yes
- [ ] No

**Result of manual pipeline run:**

(Paste relevant logs, output, or a link to the workflow run here)
