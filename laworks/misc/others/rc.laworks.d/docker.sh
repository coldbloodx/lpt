#!/bin/bash


source /etc/profile.d/nodeinfo

function install_docker()
{
    ostype=`lsb_release -is`
    case $ostype in
        CentOS | RedHatEnterpriseServer)
            #reinstall centos-release to reset centos default repos
            yum reinstall -y centos-release

            #remove docker related packages
            yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine docker-ce
            #install dependency
            yum install -y yum-utils device-mapper-persistent-data lvm2
            #add docker repo
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

            #install docker-ce
            yum install -y docker-ce docker-ce-cli containerd.io

            ;;
        Ubuntu)
            apt-get install -y apt-transport-https  ca-certificates  curl  gnupg-agent  software-properties-common

            curl -x $proxy -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

            add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

            apt-get update

            apt-get install -y docker-ce docker-ce-cli containerd.io

            ;;
        *)
            errexit "Unknown OS or lsb_release is not installed"
            ;;
    esac

}

function init_docker_proxy()
{

    mkdir -p /etc/systemd/system/docker.service.d
    cat > /etc/systemd/system/docker.service.d/proxy.conf << _EOF
    [Service]
    Environment="HTTP_PROXY=$proxy"

_EOF
}


function start_docker()
{
    systemctl daemon-reload

    systemctl stop docker
    systemctl start docker
    systemctl enable docker

    docker pull ubuntu
    docker pull centos
}

install_docker
init_docker_proxy
start_docker
