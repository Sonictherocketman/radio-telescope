import logging


logger = logging.getLogger('astronomer')


class _State:

    state = {}

    def set_button_callback(
        self,
        channel,
        callback,
        bouncetime=200,
    ):
        if callback := self.state.get(str(channel)):
            raise ValueError('A callback is already registered to this channel.')

        if GPIO:
            logger.info(f'Registered callback for channel: {channel}')
            GPIO.add_event_detect(
                channel,
                GPIO.RISING,
                callback=callback,
                bouncetime=bouncetime,
            )
        else:
            logger.info('Registered dummy callback.')

        self.state[str(channel)] = callback


State = _State()
