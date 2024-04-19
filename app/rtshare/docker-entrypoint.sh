#! /bin/sh
# A basic entrypoint script
set -e;

log() {
    echo "[$(date)] $1";
}

start_app() {
    daphne \
        --port 8000 \
        -b 0.0.0.0 \
        --verbosity 1 \
        --no-server-name \
        --http-timeout 320 \
        rtshare.asgi:application
}

# start_monitor() {
#     python manage.py monitor_cluster
# }

start_beat() {
    celery -A rtshare beat -s /opt/scheduler/celerybeat-schedule
}

start_worker() {
    celery \
        -A rtshare \
        worker \
        -l info \
        -Q default,processing,management,alerts \
        -E \
        --max-tasks-per-child 3
}

# Begin Main

if [ -z "$RUN_MODE" ]; then
    log "No mode provided. Use: api, worker, beat, or monitor";
    exit 1;
fi

if [ "$RUN_MODE" = "worker" ]; then
    start_worker
elif [ "$RUN_MODE" = "monitor" ]; then
    start_monitor
elif [ "$RUN_MODE" = "beat" ]; then
    start_beat
elif [ "$RUN_MODE" = "app" ]; then
    start_app
else
    echo "Invalid RUN MODE $RUN_MODE";
fi
