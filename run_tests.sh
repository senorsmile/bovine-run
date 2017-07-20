#!/usr/bin/env bash

stock_ansible() {
  #export ANSIBLE_STDOUT_CALLBACK=minimal
  #export ANSIBLE_STDOUT_CALLBACK=dense
  #export ANSIBLE_STDOUT_CALLBACK=log_plays
  #export ANSIBLE_STDOUT_CALLBACK=tree
  #export ANSIBLE_STDOUT_CALLBACK=json2 
  #export ANSIBLE_CALLBACK_WHITELIST='bovine_json, minimal'
  #export ANSIBLE_CALLBACK_WHITELIST='context_demo'
  #export ANSIBLE_CALLBACK_WHITELIST='debug'
  #export ANSIBLE_STDOUT_CALLBACK='debug'

  #export ANSIBLE_STDOUT_CALLBACK='bovine_json'
  export ANSIBLE_CALLBACK_WHITELIST='bovine_json'

  export PYTHONUNBUFFERED=1

  export ANSIBLE_SSH_ARGS="-o UserKnownHostsFile=/dev/null"
  export ANSIBLE_HOST_KEY_CHECKING=false

  ansible-playbook -v -i inventory/ site.yml $@ #| grep -v '^\s\+to retry'
}

python_api_ansible() {
  ./ansible_api.py 
}

vagrant_up() {
  vagrant up
}

main() {
  #vagrant_up

  echo

  time stock_ansible
  #python_api_ansible
}

main
