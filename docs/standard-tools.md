# Standard tools

`jq` and `yq` are standard command-line utilities installed by `scripts/setup-tools.sh` from `APT_PACKAGES`. They have no tracked configuration or shell initialization.

The AWS CLI is installed by the same script from `SNAP_PACKAGES` as `aws-cli --classic`; its binary is `/snap/bin/aws`.
