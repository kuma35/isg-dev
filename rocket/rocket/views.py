# -*- coding: utf-8 -*-
# Create your views here.
import re
from django.template import Context, loader
from django.http import HttpResponse
import json
from rocket.forms import CommandForm, SizeForm
from rocket.rocket_web import RocketCommander, CanNotGetRocketManager


def index(request):
    """display index page"""
    msg = ""  #  debug message if you need.
    template = loader.get_template('index.html')
    context = {'msg': msg, }
    return HttpResponse(template.render(context, request))


def controlPad(request):
    """recive from client javascript sent data"""
    msg = ""
    if request.method == 'POST':
        form = CommandForm(request.POST)
        commandLine = ''
        if form.is_valid():  # All validation rules pass
            commandLine = form.cleaned_data['command']
            commander = None
            try:
                commander = RocketCommander()
            except CanNotGetRocketManager as e:
                print(e)
            else:
                result = commander.interpret(commandLine)
                msg += " ".join(result['msg'])
        else:
            msg += "request not valid."
    else:
        form = CommandForm()  # An unbound form
    template = loader.get_template('controlPad.html')
    context = {
        'command_form': form,
        'msg': msg, }
    return HttpResponse(template.render(context, request))


def _getBrowser(userAgent):
    """get client browser type"""
    reChrome = re.compile("Chrome")
    reFirefox = re.compile("Firefox")
    reOpera = re.compile("Opera")
    maChrome = reChrome.search(userAgent)
    if maChrome:
        return 'chrome'
    maFireFox = reFirefox.search(userAgent)
    if maFireFox:
        return 'firefox'
    maOpera = reOpera.search(userAgent)
    if maOpera:
        return 'opera'
    return 'other'


def liveStream(request):
    """for live page."""
    msg = ""
    isMotionJpeg = False
    browserType = _getBrowser(request.META['HTTP_USER_AGENT'])
    msg += "useragent[%s],browserType=[%s]"%(request.META['HTTP_USER_AGENT'], browserType)
    if browserType == 'chrome' or browserType == 'firefox':
        # operaではmotion jpegは動かなかった。
        isMotionJpeg = True

    template = loader.get_template('live.html')
    context = {'msg': msg,
               'is_motion_jpeg': isMotionJpeg, }
    return HttpResponse(template.render(context, request))


def cursorPad(request):
    """display cursorPad page. no use"""
    template = loader.get_template('cursorPad.html')
    context = {}
    return HttpResponse(template.render(context, request))


def controlCommand(request, cmd=""):
    """recive command from client page and execute

    special return code:

    - -2 no connect launcher.
    - "no connect"

    :param request: request object
    :param string cmd: command char
    :return: return code andmsg to cliant page javascript
    :rtype: HttpResponse object
    """
    data = {'code': [], 'msg': []}
    try:
        commander = RocketCommander()
    except CanNotGetRocketManager as err_msg:
        print(err_msg)
        data['code'].append(-2)
        data['msg'].append("no connect")
    else:
        data = commander.interpret(cmd)
    return HttpResponse(json.dumps(data), "application/json")


def snapshot(request):
    """snapshot page for /snapshot/"""
    template = loader.get_template('snapshot.html')
    context = {}
    return HttpResponse(template.render(context, request))


def snapshot2(request):
    """snapshot page for webcam2 /snapshot2/"""
    template = loader.get_template('snapshot2.html')
    context = {}
    return HttpResponse(template.render(context, request))
