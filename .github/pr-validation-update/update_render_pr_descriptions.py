#!/usr/bin/env python3
"""Update both Render PR descriptions using your existing GitHub CLI login.

Requires Python 3 and the GitHub CLI (gh), already authenticated with permission
 to edit these PRs. Run once to update both; --preview shows the prepared text
 without accessing GitHub. This file contains public PR text, no credentials.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

REPO = "render-oss/terraform-provider-render"
ACCOUNT = "OllieinCanada"
UPDATES = json.loads('[{"number": 109, "head": "099a81310d3be5009cc3fa1ca98af1ee237e59c7", "original_body_sha256": "6c10fa482b0f1650124960a5940aa9d447e81fa4752a54f0782b01b556e7e875", "body": "## Summary\\n\\n- Add one canonical parser and formatter for bare, tagged, and digest-pinned image references.\\n- Preserve complete digests and registry credentials during refresh.\\n- Prefer digests when historical state contains both a tag and a digest.\\n- Add unit, request-builder, and full provider lifecycle regressions.\\n\\n## Root cause\\n\\n`ImageRuntimeSource` parsed `@` and `:` independently. Because a digest such as `sha256:<hex>` also contains a colon, the second branch populated `tag` with the digest hex after the digest branch had already run.\\n\\nThe update formatter then preferred `tag` over `digest`, so malformed historical state was serialized as a tag reference instead of recovering to the digest-pinned reference.\\n\\n## Before / after\\n\\nGiven this API reference:\\n\\n```text\\nghcr.io/acme/app@sha256:<hex>\\n```\\n\\nBefore this change, the reported refreshed Terraform state exposed:\\n\\n```hcl\\nimage_url = \\"ghcr.io/acme/app\\"\\ntag       = \\"<hex>\\"\\ndigest    = \\"sha256:<hex>\\"\\n```\\n\\nAn unrelated service update could therefore send:\\n\\n```text\\nghcr.io/acme/app:<hex>\\n```\\n\\nAfter this change, state remains mutually exclusive:\\n\\n```hcl\\nimage_url = \\"ghcr.io/acme/app\\"\\ntag       = null\\ndigest    = \\"sha256:<hex>\\"\\n```\\n\\nCreate and update requests send the original reference:\\n\\n```text\\nghcr.io/acme/app@sha256:<hex>\\n```\\n\\n## Validation\\n\\nRevalidated on Linux x86_64 with Go 1.26.10, Terraform 1.15.6 and golangci-lint 2.11.4.\\n\\nBoth the published commit `099a81310d3be5009cc3fa1ca98af1ee237e59c7` and GitHub\'s merge candidate `248d3ed3c20cdc1ec7f55206fa4aa831a8ea0de3` against main `2a6f1563fad96c5f28c35583c096df29fdcc5ee0` passed:\\n\\n- `TF_ACC=1 go test -p=2 ./... -count=1 -timeout=20m` \\u2014 full acceptance suite, including the provider lifecycle regression\\n- `go vet -p=2 ./...`\\n- `golangci-lint run --timeout 10m` \\u2014 zero issues\\n- gofmt and `git diff --check`\\n\\nTargeted race checks also passed on the merge candidate for the parser, request builder and digest-pinned provider lifecycle:\\n\\n```sh\\nTF_ACC=1 go test -race -p=2 ./internal/provider/common ./internal/provider/webservice/resource/internal ./internal/provider/webservice/resource -run \'Test(ParseImageReference|Image|UpdateServiceRequestFromModel_PreservesDigestAfterUnrelatedUpdate|WebServiceResource_DigestPinnedImageRoundTrip)\' -count=1 -timeout=5m\\n```\\n\\nThe contributor\'s supplemental tests at `97cc60223c3b18663d600a804bfb09823bed73fb` also passed their focused package command on Linux. That additional validation covers worker/cron image updates and is recorded separately from the PR\'s published commit.\\n\\nThe earlier Windows acceptance-test limitation has been resolved by these Linux runs. Existing acceptance tests replay cassettes; the added lifecycle test uses a local fake API. No live Render credentials or resources were used.\\n\\n## Compatibility\\n\\nThere are no schema, generated-client, or dependency changes. Existing bare and tagged references remain supported, including registry ports and nested paths. Digest algorithm prefixes are preserved exactly, and the existing schema conflict validation still prevents new configurations from setting both `tag` and `digest`.\\n\\nHistorical state containing both values now prefers the digest, allowing affected configurations to recover on refresh/apply.\\n\\n## Risk and rollback\\n\\nRisk is limited to image-reference parsing and formatting. Malformed empty tag or digest separators now produce a read error instead of silently creating invalid state. Reverting the commit restores the prior behavior, including the digest-update failure.\\n\\n## Issue\\n\\nFixes #106\\n"}, {"number": 110, "head": "5bd1637a53981696a34b7714bdb46abe1ea7e097", "original_body_sha256": "c9de03b56cd68889269b2aee22ae5ea493a71907aa3ac833cf938bf28bd30957", "body": "## Summary\\n\\n- centralize the post-update deploy decision in `common.UpdateService`\\n- skip only the guaranteed-to-fail deploy when the update response reports a suspended service\\n- preserve explicit `skip_deploy_after_service_update` behavior, active-service deploys, and errors from active-service deploy failures\\n- return the fully updated wrapped service so Terraform can persist successful service, environment-variable, secret-file, disk, override, environment, and domain writes\\n\\n## Invariant\\n\\nOnce remote configuration writes have succeeded, an impossible trailing deploy must not cause Terraform to discard the successful new state.\\n\\n## Request order\\n\\nThe shared update path retains its existing order: scaling/autoscaling, service update, environment variables, secret files, disk, notification and log-stream overrides, environment membership, and custom domains. Only the final create-deploy request is skipped, and only when the post-update API response explicitly reports `suspended` (or the provider-level skip is enabled). Unknown and newly introduced states continue to deploy.\\n\\n## Validation\\n\\nRevalidated on Linux x86_64 with Go 1.26.10, Terraform 1.15.6 and golangci-lint 2.11.4.\\n\\nBoth the published commit `5bd1637a53981696a34b7714bdb46abe1ea7e097` and GitHub\'s merge candidate `87d919f7e92fa7165e0e3d8ddd741bfa4fcf7c0c` against main `2a6f1563fad96c5f28c35583c096df29fdcc5ee0` passed:\\n\\n- `TF_ACC=1 go test -p=2 ./... -count=1 -timeout=20m` \\u2014 full acceptance suite, including the provider lifecycle regression\\n- `go vet -p=2 ./...`\\n- `golangci-lint run --timeout 10m` \\u2014 zero issues\\n- gofmt and `git diff --check`\\n\\nTargeted race checks also passed on the merge candidate for the deployment policy, HTTP request regressions and suspended-worker lifecycle:\\n\\n```sh\\nTF_ACC=1 go test -race -p=2 ./internal/provider/common ./internal/provider/backgroundworker/resource -run \'Test(UpdateService|ShouldDeployAfterUpdate|BackgroundWorkerResource_SuspendedUpdateConverges)\' -count=1 -timeout=5m\\n```\\n\\nExisting acceptance tests replay cassettes; the added lifecycle test uses a local fake API. No live Render credentials or resources were used.\\n\\nFixes #104\\n"}]')

def gh(*args, input_text=None):
    result = subprocess.run(["gh", *args], input=input_text, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "GitHub CLI failed")
    return result.stdout

def view(number):
    return json.loads(gh("pr", "view", str(number), "--repo", REPO,
                         "--json", "body,headRefOid"))

def check_current(update, current):
    if current["headRefOid"] != update["head"]:
        raise RuntimeError("PR #%s has a different commit; its validation notes must be reviewed first." % update["number"])
    if current["body"] == update["body"]:
        return False
    digest = hashlib.sha256(current["body"].encode()).hexdigest()
    if digest != update["original_body_sha256"]:
        raise RuntimeError("PR #%s was edited since these notes were prepared. Stopping to preserve those edits." % update["number"])
    return True

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="show both prepared descriptions without connecting to GitHub")
    args = parser.parse_args()
    if args.preview:
        for update in UPDATES:
            print("PR #%s\n%s\n" % (update["number"], update["body"]))
        return 0
    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI (gh) is required on this computer. No changes were made.")
    login = gh("api", "user", "--jq", ".login").strip()
    if login.casefold() != ACCOUNT.casefold():
        raise RuntimeError("GitHub CLI is signed in as %s, expected %s. No changes were made." % (login, ACCOUNT))
    # Check both PRs before editing either one.
    for update in UPDATES:
        check_current(update, view(update["number"]))
    for update in UPDATES:
        number = update["number"]
        if not check_current(update, view(number)):
            print("PR #%s already has the updated description." % number, flush=True)
            continue
        gh("api", "repos/%s/pulls/%s" % (REPO, number), "--method", "PATCH", "--input", "-",
           input_text=json.dumps({"body": update["body"]}))
        actual = view(number)
        if actual["headRefOid"] != update["head"] or actual["body"] != update["body"]:
            raise RuntimeError("PR #%s changed during the update; inspect it before continuing." % number)
        print("Updated and verified: https://github.com/%s/pull/%s" % (REPO, number), flush=True)
    print("Both PR descriptions are up to date.", flush=True)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, KeyboardInterrupt) as error:
        print("Stopped: %s" % error, file=sys.stderr)
        print("Earlier successful updates, if any, remain saved. Rerunning is safe after resolving the error.", file=sys.stderr)
        sys.exit(1)
