#!/bin/bash -e

#export WEAVE_URL=${WEAVE_URL:="https://raw.githubusercontent.com/zettio/weave/master/weaver/weave"}
K8S_VERSION=1.1.1

usage() {
cat <<EOF
Usage:
jencactl etcd
jencactl proxy
jencactl hyperkube
jencactl start
jencactl stop
jencactl restart
jencactl images
jencactl updatecode
jencactl help
EOF
	exit 1
}

# stop any container that the output of docker ps matches against the
# given grep pattern
grepstop-container() {
	local pattern=$1
	docker rm -f $(docker ps -a | grep $pattern | awk '{print $1}')
}

# start the etcd docker container
cmd-etcd() {
	docker run -d \
	  --name etcd \
	  --net host \
	  kubernetes/etcd:2.0.5.1 \
	  /usr/local/bin/etcd \
	  	--addr=127.0.0.1:4001 \
	  	--bind-addr=0.0.0.0:4001 \
	  	--data-dir=/var/etcd/data
}

# start the various kubernetes containers via the kyperkube
cmd-hyperkube() {
	docker run -d \
		--net host \
		-v /var/run/docker.sock:/var/run/docker.sock \
		gcr.io/google_containers/hyperkube:v${K8S_VERSION} \
		/hyperkube kubelet \
			--api_servers=http://localhost:8080 \
			--v=2 \
			--address=0.0.0.0 \
			--enable_server \
			--hostname_override=127.0.0.1 \
			--config=/etc/kubernetes/manifests
}

# start the kubernetes proxy (we are running the kubelet on this node)
cmd-proxy() {
	docker run -d \
		--net host \
		--privileged \
		gcr.io/google_containers/hyperkube:v${K8S_VERSION} \
		/hyperkube proxy \
			--master=http://127.0.0.1:8080 \
			--v=2
}

# wrapper to start the whole stack
cmd-start() {
	cmd-etcd
	cmd-hyperkube
	cmd-proxy
}

# logic to remove only the jenca/kubernetes containers
cmd-stop() {
	grepstop-container k8s_scheduler || true
	grepstop-container k8s_apiserver || true
	grepstop-container k8s_controller-manager || true
	grepstop-container k8s_controller-manager || true
	grepstop-container k8s_POD || true
	grepstop-container proxy || true
	grepstop-container kubelet || true
	grepstop-container etcd	|| true
	#docker rm -f INSERTNAMESHERE
}

cmd-restart() {
	cmd-stop
	cmd-start
}

# this tool is designed for the user to have already sorted out what branch each repo
# is on and have committed any changes etc
cmd-updatecode-repo() {
	local repo=$1;

	if [[ ! -d "/vagrant/repos/${repo}" ]]; then
		echo "cloning $repo"
		mkdir -p /vagrant/repos
		cd /vagrant/repos && git clone "git@github.com:jenca-cloud/${repo}.git"
	fi

	cd /vagrant/repos/${repo} && git pull
}

cmd-updatecode() {
	cmd-updatecode-repo jenca-authorization
	cmd-updatecode-repo jenca-authentication
	cmd-updatecode-repo jenca-runtime
	cmd-updatecode-repo jenca-projects
	cmd-updatecode-repo jenca-library
	cmd-updatecode-repo jenca-router
	cmd-updatecode-repo jenca-gui
	cmd-updatecode-repo jenca-level-storage
}

cmd-build-image() {
	local repo=$1;
	cd /vagrant/repos/${repo} && make images
}

cmd-run-tests() {
	local repo=$1;
	cd /vagrant/repos/${repo} && make test
}

cmd-images() {
	cmd-build-image jenca-authentication
	cmd-build-image jenca-authorization
	cmd-build-image jenca-projects
	cmd-build-image jenca-router
	cmd-build-image jenca-gui
	cmd-build-image jenca-level-storage
	cmd-build-image jenca-library
}

cmd-test() {
	cmd-run-tests jenca-authentication
	cmd-run-tests jenca-authorization
	cmd-run-tests jenca-projects
	cmd-run-tests jenca-router
	cmd-run-tests jenca-gui
	cmd-run-tests jenca-level-storage
	cmd-run-tests jenca-library
}

main() {
	case "$1" in
	etcd)					        shift; cmd-etcd; $@;;
	hyperkube)					  shift; cmd-hyperkube; $@;;
	proxy)					      shift; cmd-proxy; $@;;
	start)					      shift; cmd-start; $@;;
	stop)					        shift; cmd-stop; $@;;
	restart)					    shift; cmd-restart; $@;;
	updatecode)					  shift; cmd-updatecode; $@;;
	images)					      shift; cmd-images; $@;;
	test)					        shift; cmd-test; $@;;
	*)                    usage $@;;
	esac
}

main "$@"
