# -*- coding:utf-8 -*-
from time import sleep
import fcntl
import errno
from rocket.rocket_backend import RocketManager


class CanNotGetRocketManager(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Turret:
    # class shared var. with classname
    button_labels = ["Down", "Up", "Left", "Right", "_Fire"]
    time_pan = 0.0
    time_tilt = 0.0
    time_polling_span = 0.1  # check_limits polling step
    ctrl = None
    launcher = None

    def __init__(self):
        Turret.ctrl = None
        Turret.ctrl = RocketManager()
        err_msg = Turret.ctrl.acquire_devices()
        if err_msg:
            raise CanNotGetRocketManager(err_msg)
        self.launcher = Turret.ctrl.launchers[0]  # :-)

    def do_move(self, command_index, time):
        result = 0.0
        if not self.launcher.previous_limit_switch_states[command_index]:
            self.launcher.start_movement(command_index)
            if time:
                t = 0.0
                while t < time:
                    sleep(self.time_polling_span)
                    self.launcher.check_limits()
                    if self.launcher.previous_limit_switch_states[command_index]:
                        result = t
                        break
                    t += Turret.time_polling_span
                result = t
            self.launcher.stop_movement()
        return result

    def __del__(self):
        for launcher in Turret.ctrl.launchers:
            launcher.stop_movement()

    def do_down(self, time=0.3):
        Turret.time_tilt -= self.do_move(0, time)

    def do_up(self, time=0.3):
        Turret.time_tilt += self.do_move(1, time)

    def do_left(self, time=0.3):
        Turret.time_pan -= self.do_move(2, time)

    def do_right(self, time=0.3):
        Turret.time_pan += self.do_move(3, time)

    def do_fire(self, time=4.0):
        """
        """
        self.launcher.previous_fire_state = False
        self.launcher.start_movement(4)
        while 1:
            sleep(0.1)
            self.launcher.check_limits()
            if self.launcher.previous_fire_state:
                break
        self.launcher.stop_movement(4)

        if not self.launcher.previous_limit_switch_states[2]:
            self.do_left(0.1)
            self.do_right(0.1)
        else:
            self.do_right(0.1)
            self.do_left(0.1)

    def do_center(self):
        # pan center
        while not self.launcher.previous_limit_switch_states[2]:
            self.do_left()
        Turret.time_pan = 0.0
        while not self.launcher.previous_limit_switch_states[3]:
            self.do_right()
        self.do_left(time=self.time_pan/2.0)
        # tilt center
        while not self.launcher.previous_limit_switch_states[0]:
            self.do_down()
        Turret.time_tilt = 0.0
        while not self.launcher.previous_limit_switch_states[1]:
            self.do_up()
        self.do_down(time=self.time_tilt/2)

    def do_reset(self):
        while not self.launcher.previous_limit_switch_states[2]:
            self.do_left()
        while not self.launcher.previous_limit_switch_states[0]:
            self.do_down()


class RocketCommander:
    """ rocket control interpret by text commands.
    """
    def __init__(self):
        self.turret = Turret()
        self.lockfd = None

    def __del__(self):
        if hasattr(self, 'lockfd'):
            if self.lockfd:
                self.lockfd.close()

    def interpret(self, text):
        """
        result code:
        -1;already locked
        0;invalid command
        1;done
        """
        # print text
        result = {'code': [], 'msg': []}
        self.commands = []
        commands = text.split(' ')
        self.lockfd = file('/tmp/rocket.lock', 'w')
        try:
            fcntl.lockf(self.lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            for command in commands:
                if command == 'q ':
                    result['code'].append(0)
                    result['msg'].append("quit")
                    break
                elif command == 'u':
                    self.turret.do_up()
                    result['code'].append(1)
                    result['msg'].append("done")
                elif command == 'd':
                    result['code'].append(1)
                    result['msg'].append("done")
                    self.turret.do_down()
                elif command == 'l':
                    result['code'].append(1)
                    result['msg'].append("done")
                    self.turret.do_left()
                elif command == 'r':
                    result['code'].append(1)
                    result['msg'].append("done")
                    self.turret.do_right()
                # elif command == 'f':
                #    result['code'].append(1)
                #    result['msg'].append("done")
                #    self.turret.do_fire()
                elif command == 'c':
                    result['code'].append(1)
                    result['msg'].append("done")
                    self.turret.do_center()
                elif command == 'reset':
                    result['code'].append(1)
                    result['msg'].append("done")
                    self.turret.do_reset()
                else:
                    result['code'].append(0)
                    result['msg'].append("unknown command")
        except IOError as e:
            # EACCES is not EACCESS :-)
            if e.errno == errno.EACCES or e.errno == errno.EAGAIN:
                # alread locked
                result['code'].append(-1)
                result['msg'].append("alrady using. please wait few minuties.")
            else:
                # exception to upper level
                raise IOError(e)
        else:
            fcntl.lockf(self.lockfd, fcntl.LOCK_UN)
            self.lockfd.close()
        return result
