#!/bin/bash

if ! $(which jq &>/dev/null); then
    echo jq command not found
    exit 1
fi
if ! $(which gh &>/dev/null); then
    echo gh command not found
    exit 2
fi

model=$(gh api graphql --paginate -F owner=mozilla -F repo=deepspeech -f query="$(cat release-assets.graphql)" \
    | jq -r '.data.repository.latestRelease.releaseAssets.nodes[] | select(.name | endswith("models.pbmm")).downloadUrl')
>&2 echo "Link to model is: $model"
curl -L $model -o deepspeech.pbmm

scorer=$(gh api graphql --paginate -F owner=mozilla -F repo=deepspeech -f query="$(cat release-assets.graphql)" \
    | jq -r '.data.repository.latestRelease.releaseAssets.nodes[] | select(.name | endswith("models.scorer")).downloadUrl')
>&2 echo "Link to scorer is: $scorer"
curl -L $scorer -o deepspeech.scorer
