#!/bin/bash
# ssh_key_generator - designed to work with the Terraform External Data Source provider
# Usage: echo '{"key_name": "terraformdemo", "key_environment": "dev"}' | ./ssh_key_generator.sh

function error_exit() {
  echo "$1" 1>&2
  exit 1
}

function check_deps() {
  test -f $(which ssh-keygen) || error_exit "ssh-keygen command not found in path, please install it"
  test -f $(which jq) || error_exit "jq command not found in path, please install it"
}

function parse_input() {
  eval "$(jq -r '@sh "export KEY_NAME=\(.key_name) KEY_ENVIRONMENT=\(.key_environment)"')"
  if [[ -z "${KEY_NAME}" ]]; then export KEY_NAME=none; fi
  if [[ -z "${KEY_ENVIRONMENT}" ]]; then export KEY_ENVIRONMENT=none; fi
}

function create_ssh_key() {
  script_dir=$(dirname $0)
  export ssh_key_file="${script_dir}/${KEY_NAME}-${KEY_ENVIRONMENT}"
  if [[ ! -f "${ssh_key_file}" ]]; then
    ssh-keygen -q -m PEM -t rsa -b 4096 -N '' -f $ssh_key_file
  fi
}

function produce_output() {
  public_key_contents=$(cat ${ssh_key_file}.pub)
  private_key_contents=$(cat ${ssh_key_file} | awk '$1=$1' ORS='  \n')
  jq -n \
    --arg public_key "$public_key_contents" \
    --arg private_key "$private_key_contents" \
    --arg private_key_file "$ssh_key_file" \
    '{"public_key":$public_key,"private_key":$private_key,"private_key_file":$private_key_file}'
}

check_deps
parse_input
create_ssh_key
produce_output
