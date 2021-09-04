# -*- coding: utf-8 -*-
import logging
import usb
import usb.util
from time import sleep


class OriginalRocketLauncher:
    '''launcher object base class'''

    color_green = True
    has_laser = False

    green_directions = [1, 0, 2, 3, 4]
    # button_labels = ["Down", "Up", "Left", "Right", "_Fire"]

    def __init__(self, dev):
        '''constractor

        :param dev: device object from usb.core.find()
        :type dev: usb.core.Device object
        '''
        self.dev = dev  # set by __init__() arg
        self.cfg = None  # set by acquire()
        self.intf = None  # set by acquire()
        self.usb_debug = False
        self.previous_fire_state = False

        #  []*4 : Down, Up, Left, Right
        self.previous_limit_switch_states = [False]*4

    def acquire(self, dev):
        self.cfg = self.dev.get_active_configuration()
        self.intf = self.cfg[(0,0)]
        return 0

    def issue_command(self, command_index):

        signal = 0
        if command_index >= 0:
            signal = 1 << command_index

        if self.dev.is_kernel_driver_active(self.intf.bInterfaceNumber):
            self.dev.detach_kernel_driver(self.intf.bInterfaceNumber)
        try:
            # self.handle.controlMsg(0x21, 0x09, [signal], 0x0200)
            # controlMsg(self, requestType, request, buffer, value=0, index=0, timeout=100)
            # requestType:0x21 0b0010_0001 bit7:0 OUT
            # bit6-5:01 特定のUSBクラスに対して定義されたリクエスト(0b01)
            # bit4-0:00001 特定のインターフェイス宛
            # request0x09 Set Configuration
            # buffer:[signal]
            # value:0x0200
            self.dev.ctrl_transfer(bmRequestType=0x21,
                                   bRequest=0x09,
                                   wValue=0x0200,
                                   data_or_wLength=[signal])

        except usb.USBError:
            pass
        usb.util.dispose_resources(self.dev)
        self.dev.attach_kernel_driver(self.intf.bInterfaceNumber)

    def start_movement(self, command_index):
        self.issue_command(self.green_directions[command_index])

    def stop_movement(self):
        self.issue_command(-1)

    def check_limits(self):
        """For the "green" rocket launcher,
        the MSB of byte 2 comes on when a rocket is ready to fire,
        and is cleared again shortly after
        the rocket fires and cylinder is charged further."""

        if self.dev.is_kernel_driver_active(self.intf.bInterfaceNumber):
            self.dev.detach_kernel_driver(self.intf.bInterfaceNumber)
        bytes = self.dev.read(
            self.intf.endpoints()[0].bEndpointAddress,
            8)  # trasfer type guess endpoint automatically.
        if self.usb_debug:
            print("USB packet:", bytes)
        usb.util.dispose_resources(self.dev)
        self.dev.attach_kernel_driver(self.intf.bInterfaceNumber)

        limit_bytes = list(bytes)[0:2]
        self.previous_fire_state = limit_bytes[1] & (1 << 7)

        limit_signal = (limit_bytes[1] & 0x0F) | (limit_bytes[0] >> 6)

        new_limit_switch_states = [bool(limit_signal & (1 << i))
                                   for i in range(4)]
        self.previous_limit_switch_states = new_limit_switch_states

        return new_limit_switch_states


class BlueRocketLauncher(OriginalRocketLauncher):

    color_green = False

    def __init__(self, dev):
        OriginalRocketLauncher.__init__(self, dev)

    def start_movement(self, command_index):
        self.issue_command(command_index)

    def stop_movement(self):
        self.issue_command(5)

    def check_limits(self):
        """For the "blue" rocket launcher,
        the firing bit is only toggled when the rocket fires,
        then is immediately reset."""

        kernel_driver_active_flag = False
        bytes = None
        self.issue_command(6)

        if self.dev.is_kernel_driver_active(self.intf.bInterfaceNumber):
            kernel_driver_active_flag = True
            self.dev.detach_kernel_driver(self.intf.bInterfaceNumber)
        try:
            bytes = self.dev.read(
                self.intf.endpoints()[0].bEndpointAddress,
                1)  # trasfer type guess endpoint automatically.

        except usb.USBError as e:
            if e.strerror.find("No error") >= 0 or \
               e.strerror.find("could not claim interface") >= 0 or \
               e.strerror.find("Value too large") >= 0:

                pass
                #  if self.usb_debug:
                #  print("POLLING ERROR")

                # TODO: Should we try again in a loop?
            else:
                raise e
        usb.util.dispose_resources(self.dev)
        self.dev.attach_kernel_driver(self.intf.bInterfaceNumber)

        if self.usb_debug:
            print("USB packet:", bytes)

        self.previous_fire_state = bool(bytes)

        if bytes is None:
            return self.previous_limit_switch_states
        else:
            limit_signal, = bytes  # 1 elemnt tupple unpack !!
            new_limit_switch_states = [bool(limit_signal & (1 << i))
                                       for i in range(4)]

            self.previous_limit_switch_states = new_limit_switch_states
            return new_limit_switch_states


class BlackRocketLauncher(BlueRocketLauncher):

    striker_commands = [0xf, 0xe, 0xd, 0xc, 0xa, 0x14, 0xb]
    # button_labels = ["Down", "Up", "Left", "Right", "_Fire"]

    has_laser = True

    def issue_command(self, command_index):

        signal = self.striker_commands[command_index]

        if self.dev.is_kernel_driver_active(self.intf.bInterfaceNumber):
            self.dev.detach_kernel_driver(self.intf.bInterfaceNumber)
        try:
            # self.handle.controlMsg(0x21, 0x09, [signal, signal])
            self.dev.ctrl_transfer(bmRequestType=0x21,
                                   bRequest=0x09,
                                   data_or_wLength=[signal, signal])
        except usb.USBError:
            pass
        usb.util.dispose_resources(self.dev)
        self.dev.attach_kernel_driver(self.intf.bInterfaceNumber)

    def check_limits(self):

        return self.previous_limit_switch_states


class RocketManager:

    vendor_product_ids = [(0x1941, 0x8021),
                          (0x0a81, 0x0701),
                          (0x0a81, 0xff01),
                          (0x1130, 0x0202)]
    launcher_types = ["Original", "Webcam", "Wireless", "Striker II"]
    housing_colors = ["green", "blue", "silver", "black"]

    launcher_products = [
        {'vendor': 0x1941,
         'product': 0x8021,
         'launcher_type': "Original",
         'color': "green",
         'obj': OriginalRocketLauncher, },
        {'vendor': 0x0a81,
         'product': 0x0701,
         'launcher_type': "Webcam",
         'color': "blue",
         'obj': BlueRocketLauncher, },
        {'vendor': 0x0a81,
         'product': 0xff01,
         'launcher_type': "Wireless",
         'color': "silver",
         'obj': None,
         'msg': ("The {launcher_type} {color} Rocket Launcher "
                 "is not yet supported. "
                 "Try the {first_type} or {second_type} one."), },
        {'vendor': 0x1130,
         'product': 0x0202,
         'launcher_type': "Striker II",
         'color': "black",
         'obj': BlackRocketLauncher}, ]

    def __init__(self):
        self.launchers = []

    def acquire_devices(self):
        '''IMPOTANT: only connect ONE lanucher.

        If multiple launchers connected,
        detect only first detect device :-)

        self.launchers : hold found launcher device obujects.

        JP:USBミサイルランチャーが1台のみ接続される想定です。
        複数種類接続の場合はハードコーディングされた順番で
        最初に見つかったモノのみ認識します。
        また同一の製品を複数繋げた場合はusb.core.find関数が
        最初に見つけてきた方を認識します。その順序はfind関数
        の実装依存で私にも分かりません。

        :return: message, error message
        '''

        device_found = False

        for product in self.launcher_products:
            dev = usb.core.find(idVendor=product['vendor'],
                                idProduct=product['product'])
            if dev:
                break
        if dev is None:
            return "No USB Rocket Launcher appears\nto be connected."
        print("Located {0} Rocket Launcher device.".format(product['color']))
        # dev.reset()  # このインスタンスの最初でリセットかます:-)
        launcher = product['obj'](dev)
        if launcher is None:
            print(producnt['msg'].format(
                launcher_type=product['launcher_type'],
                color=product['color'],
                first_type=launcher_products[0]['launcher_type'],
                second_type=launcher_products[1]['launcher_type']))
        return_code = launcher.acquire(dev)
        if not return_code:
            self.launchers.append(launcher)
            device_found = True
        elif return_code == 2:
            string = """\
You don't have permission to operate the USB device.
To give yourself permission by default (in Ubuntu),
create the file /etc/udev/rules.d/40-missilelauncher.rules
with the following line:
SUBSYSTEM=="usb", ACTION=="add", ATTR{idVendor}=="{%04x}",
ATTR{idProduct}=="{%04x}", GROUP="plugdev", MODE="0660"
The .deb installer should have done this for you.
If you just installed the .deb,
you need to unplug and replug the USB device now.
This will apply the new permissions from the .rules file.
"""
            print(string.format(product['vendor'], product['product']))
            return """\
You don't have permission to operate the USB device.
If you just installed the .deb,
you need to plug cycle the USB device now.
This will apply the new permissions from the .rules file.
"""
