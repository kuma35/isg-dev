# -*- coding: utf-8 -*-
# Create your views here.
import re
from django.template import Context, loader
from django.http import HttpResponse
import json
from rocket.forms import CommandForm, SizeForm
from rocket.rocket_web import RocketCommander, CanNotGetRocketManager


def index(request):
    msg = ""
    maxWidth = 1280
    maxHeight = 720
    minWidth = 320
    nowWidth = 1280
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid():  # All validation rules pass
            nowWidth = int(form.cleaned_data['size'])
            # msg += "selected size %s"%(nowWidth)
        else:
            msg += "invalid data"
    else:
        form = SizeForm({'size': nowWidth})  # An unbound form
    if nowWidth > maxWidth:
        # 文字列比較になっていたので数値比較になるよう
        # nowWidthをint()で型変換
        nowWidth = maxWidth
    elif nowWidth < minWidth:
        nowWidth = minWidth
    nowHeight = int(float(maxHeight) * (float(nowWidth) / float(maxWidth)))
    template = loader.get_template('index.html')
    # msg += "nowWidth=%d, nowHeight=%d"%(nowWidth, nowHeight)
    context = {
        'size_form': form,
        'width': nowWidth,
        'height': nowHeight,
        'msg': msg, }
    return HttpResponse(template.render(context, request))


def controlPad(request):
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
    msg = ""
    maxWidth = 1280
    maxHeight = 720
    minWidth = 320
    nowWidth = 1280
    isMotionJpeg = False
    browserType = _getBrowser(request.META['HTTP_USER_AGENT'])
    msg += "useragent[%s],browserType=[%s]"%(request.META['HTTP_USER_AGENT'], browserType)
    # if browserType == 'chrome' or
    #    browserType == 'firefox' or
    #    browserType == 'opera':
    if browserType == 'chrome' or browserType == 'firefox':
        # operaではmotion jpegは動かなかった。
        isMotionJpeg = True
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid():  # All validation rules pass
            nowWidth = int(form.cleaned_data['size'])
            # msg += "selected size %s"%(nowWidth)
        else:
            msg += "invalid data"
    else:
        form = SizeForm({'size': nowWidth})  # An unbound form
    if nowWidth > maxWidth:
        # 文字列比較になっていたので数値比較になるよう
        # nowWidthをint()で型変換
        nowWidth = maxWidth
    elif nowWidth < minWidth:
        nowWidth = minWidth
    nowHeight = int(float(maxHeight) * (float(nowWidth) / float(maxWidth)))
    # t = loader.get_template('live.html')
    template = loader.get_template('live2.html')
    # msg += "nowWidth=%d, nowHeight=%d"%(nowWidth, nowHeight)
    context = {
        'size_form': form,
        'width': nowWidth,
        'height': nowHeight,
        'msg': msg,
        'is_motion_jpeg': isMotionJpeg, }
    return HttpResponse(template.render(context, request))


def cursorPad(request):
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
    template = loader.get_template('snapshot.html')
    context = {}
    return HttpResponse(template.render(context, request))


def snapshot2(request):
    template = loader.get_template('snapshot2.html')
    context = {}
    return HttpResponse(template.render(context, request))
