# Update the two Render PR descriptions

This workflow updates only the descriptions of upstream PRs #109 and #110.
It checks the authenticated account, both tested commit hashes and existing
PR descriptions before writing, then verifies each saved result. Re-running
skips descriptions that already match. Changed commits or unexpected edits
stop the updater so they can be reviewed.

The workflow lives on `automation/update-pr-validation-notes`. It runs when
that branch is pushed. After configuring its secret, use **Re-run all jobs**
on the existing run; no workflow or merge into the default branch is needed.

## One-time authorization

The installed GitHub app covers OllieinCanada's repositories. It cannot edit
these upstream PRs in render-oss. A different execution environment alone
does not change that scope.

1. Create a short-lived **classic** GitHub personal access token under the
   OllieinCanada account with the `public_repo` scope. Choose the shortest
   practical expiration. A fine-grained token restricted to this fork cannot
   edit the upstream PRs.
2. Store it as an **Actions repository secret** named
   `RENDER_PR_UPDATE_TOKEN` in OllieinCanada/terraform-provider-render.
   Do not put the token in chat, a commit, or a workflow input.
3. Re-run the failed workflow, or ask the assistant to re-run it.
4. After both updates are verified, revoke the token and delete the secret.

`public_repo` grants broader access than just these two descriptions, within
permissions the account already has. The updater itself targets only these
two PRs. The secret is exposed only to the update step, and the job's built-in
GITHUB_TOKEN has read-only contents permission. The workflow does not print
tokens, change PR source code or state, merge anything, or call Render APIs.

The first run stops before editing PRs if the secret has not been configured.
