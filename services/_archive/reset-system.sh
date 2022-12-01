#!/bin/bash

prompt_confirm() {
  while true; do
    read -r -n 1 -p "${1:-Continue?} [Y/N]: " REPLY
    case $REPLY in
      [yY])
        export SERVICE_ROOT="${PWD}"
        if ! docker info >> /dev/null 2>&1;
          then
            echo "Docker isn't running" >> /dev/null
          else
            echo "Stopping project containers"
            docker stop $(docker ps -aqf "name=^services_*") >> /dev/null 2>&1
            echo "Removing project containers"
            docker rm $(docker ps -aqf "name=^services_*") >> /dev/null 2>&1
            echo "Removing project images"
            docker rmi $(docker images | grep 'services_') >> /dev/null 2>&1
            echo "Clearing data from local volumes: MySQL data, MySQL Test data and RabbitMQ Data"
            docker volume rm $(docker volume ls -qf "name=^junction_services_*") >> /dev/null 2>&1
        fi
        echo "Cleanup complete!!!"
        return 0 ;;
      [nN])
        printf "\n";
        return 1 ;;
      *)
        printf " \033[31m %s \n\033[0m" "invalid input"
    esac
  done
}

prompt_confirm "Resetting system will clear all your system data. Do you still want to do it?" || exit 0
