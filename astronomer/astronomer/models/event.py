from dataclasses import dataclass
import json


@dataclass
class Event:
    event: str = None
    id: str = None
    data: str = ''

    class Type:
        PING = 'ping'
        CONFIGURE = 'configure'
        ADD_TASK = 'add-task'
        UPDATE_TASK = 'update-task'
        DELETE_TASK = 'delete-task'

    @property
    def is_message(self):
        return self.event and self.event.lower() == 'message'

    @property
    def json(self):
        return json.loads(self.data)


