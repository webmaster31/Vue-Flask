task_routes = {
    "save_object": {"queue": "save"},
    "handle_object_save": {"queue": "save-notification"},
    "send_email": {"queue": "email"},
    "dump_clickwrap_acceptance": {"queue": "dump-clickwrap"}
}
