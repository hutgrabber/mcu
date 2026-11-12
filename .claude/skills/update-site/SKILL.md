---
name: update-site
description: Change what mcu.hutlab.dev says. Research the latest Marvel release information, or make a small text change, and publish it through a pull request. Runs the content-editor agent.
argument-hint: "[what to change or check, or leave empty for a full refresh]"
context: fork
agent: content-editor
background: false
disable-model-invocation: true
---

Request from the site's owner: $ARGUMENTS

If the request above is empty, do a full research update. Check the Marvel release calendar for anything that has changed since the "Current as of" date in the footer of `src/template.html`: new or moved release dates, titles announced or renamed, and anything that has come out since. Prepare the changes as a pull request for review, without publishing.

Follow your instructions in full, including the publishing rules, and end with your report.
