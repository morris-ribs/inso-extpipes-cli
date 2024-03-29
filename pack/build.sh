#!/bin/bash
set -e
cd "${0%/*}/.."

TAG="${VERSION:-latest}"
IMAGE="${IMAGE:-extpipes-cli}"
PUBLISH="${PUBLISH:-false}"

echo "Building image $IMAGE:$TAG"

set +e
if $PUBLISH -eq "true"; then
  # building a poetry project, which provides `extpipes-cli` as a command
  # keeping `logs/*` in the image, so that the `extpipes-cli` logging can write to it
  pack build "$IMAGE:$TAG" --buildpack paketo-buildpacks/python \
                          --builder paketobuildpacks/builder:base \
                          --buildpack paketo-buildpacks/source-removal \
                          --default-process=run \
                          --env BP_INCLUDE_FILES='src/*:logs/*:extpipes-cli' \
                          --env BP_POETRY_VERSION='1.3.2' \
                          --publish
else
  pack build "$IMAGE:$TAG" --buildpack paketo-buildpacks/python \
                          --builder paketobuildpacks/builder:base \
                          --buildpack paketo-buildpacks/source-removal \
                          --default-process=run \
                          --env BP_INCLUDE_FILES='src/*:logs/*:extpipes-cli' \
                          --env BP_POETRY_VERSION='1.3.2' \
                          --env BP_LIVE_RELOAD_ENABLED=true
fi
set -e

RESULT=$?
exit $RESULT
