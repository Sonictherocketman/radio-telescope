#! /bin/bash
set -e;

ENV="production"

log() {
    echo "[$(date)] $@"
}

load_secrets() {
    if [ ! -f ./secrets.sh ]; then
        log "No secrets found!"
    else
        log "Sourcing secrets..."
        source ./secrets.sh;
    fi
}

update_codebase() {
    log "Updating codebase..."
    git pull
}

do_migrate() {
    log "Migrating database..."
    do_docker run --rm app ./manage.py migrate
}

do_collectstaticfiles() {
    log "Collecting static files..."
    do_docker run --rm app ./manage.py collectstatic --no-input
}

do_docker() {
    docker compose -f ./docker-compose.yml -f ./docker-compose.$ENV.yml $@
}

deploy_app() {
    log "Building new images..."
    do_docker build app

    log "Starting backup API version (zero-downtime)"
    do_docker up -d app_backup
    sleep 5;

    log "Deploying new containers..."
    do_docker up -d app
    sleep 5;
    do_migrate
    do_collectstaticfiles

    log "Removing old version (zero-downtime)..."
    do_docker stop app_backup

    log "Rebuilding the backup API for later use (zero-downtime)..."
    do_docker build app_backup
}

deploy_worker() {
    log "Starting worker..."
    do_docker build --pull worker
    do_docker up -d worker
}

deploy_scheduler() {
    log "Starting scheduler..."
    do_docker up -d --build --force-recreate scheduler
}

check_env() {
    if [ ! -f "./docker-compose.$ENV.yml" ]; then
        log "Incorrect environment. No compose file found for $ENV"
        exit -1;
    fi
}

stop_scheduler() {
    log "Stopping scheduled tasks..."
    do_docker stop scheduler
}

shutdown_queues() {
    log "Shutting down queues..."
    do_docker run --rm app bash -c './manage.py shutdown_queues'
    log "Waiting for queues to become idle (30 sec)..."
    sleep 30;
}

do_done() {
  log "$1 Process Complete!"
}

do_clean() {
    log "Removing stale images & containers..."
    docker image prune -f
    docker container prune -f
}

# Commands

do_up() {
    check_env
    load_secrets
    deploy_app
    deploy_worker
    deploy_scheduler
    do_done
}

do_down() {
    check_env
    load_secrets
    do_docker down
}

do_upgrade() {
    check_env
    load_secrets
    update_codebase
    stop_scheduler
    shutdown_queues
    deploy_app
    deploy_worker
    deploy_scheduler
    do_clean
    do_done
}

# Begin Arg Parsing

if [ -n "$2" ]; then
    case $2 in
        -e|--env)
            ENV=$3
        ;;
        -e|--env)
            ENV=$3
        ;;
        *)
            log "Error: Unknown environment: $2"
            exit -1;
        ;;
    esac

    log "Performing actions using settings for [$ENV] environment..."
fi

case $1 in
    up)
        do_up
    ;;
    down)
       do_down
    ;;
    upgrade)
        do_upgrade
    ;;
    *)
        log "Error: Unknown Command"
        exit -1;
    ;;
esac
