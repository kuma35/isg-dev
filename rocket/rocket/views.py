# -*- coding: utf-8 -*-
# Create your views here.
import re
from django.template import Context, loader
from django.http import HttpResponse
import json
from rocket.launcher.forms import CommandForm, SizeForm
from rocket.launcher.rocket_web import RocketCommander, CanNotGetRocketManager

def index(request) :
    msg = ""
    maxWidth = 1280
    maxHeight = 720
    minWidth  = 320
    nowWidth = 1280
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid(): # All validation rules pass
            nowWidth = int(form.cleaned_data['size'])
            #msg += "selected size %s"%(nowWidth)
        else :
            msg += "invalid data"
    else :
        form = SizeForm({'size':nowWidth}) # An unbound form
    if nowWidth > maxWidth :    # 文字列比較になっていたので数値比較になるようnowWidthをint()で型変換
        nowWidth = maxWidth
    elif nowWidth < minWidth :
        nowWidth = minWidth
    nowHeight = int(float(maxHeight) * (float(nowWidth) / float(maxWidth)))
    template = loader.get_template('launcher/index.html')
    #msg += "nowWidth=%d, nowHeight=%d"%(nowWidth, nowHeight)
    context = {
        'size_form' : form,
        'width' : nowWidth,
        'height': nowHeight,
        'msg':msg, }
    return HttpResponse(template.render(context, request))


def controlPad(request) :
    msg = ""
    if request.method == 'POST':
        form = CommandForm(request.POST)
        commandLine = ''
        if form.is_valid(): # All validation rules pass
            commandLine = form.cleaned_data['command']
            commander = None
            try :
                commander = RocketCommander()
            except CanNotGetRocketManager as e :
                print(e)
            else :
                result = commander.interpret(commandLine)
                msg += " ".join(result['msg'])
        else :
            msg += "request not valid."
    else :
        form = CommandForm() # An unbound form
    template = loader.get_template('launcher/controlPad.html')
    context = {
        'command_form' : form,
        'msg' : msg, }
    return HttpResponse(template.render(context, request))


def _getBrowser(userAgent) :
    reChrome = re.compile("Chrome")
    reFirefox = re.compile("Firefox")
    reOpera = re.compile("Opera")
    maChrome = reChrome.search(userAgent)
    if maChrome :
        return 'chrome'
    maFireFox = reFirefox.search(userAgent)
    if maFireFox :
        return 'firefox'
    maOpera = reOpera.search(userAgent)
    if maOpera :
        return 'opera'
    return 'other'


def liveStream(request) :
    msg = ""
    maxWidth = 1280
    maxHeight = 720
    minWidth  = 320
    nowWidth = 1280
    isMotionJpeg = False
    browserType = _getBrowser(request.META['HTTP_USER_AGENT'])
    msg += "useragent[%s],browserType=[%s]"%(request.META['HTTP_USER_AGENT'], browserType)
    #if browserType == 'chrome' or browserType == 'firefox' or browserType == 'opera' :
    if browserType == 'chrome' or browserType == 'firefox' :    # operaではmotion jpegは動かなかった。
        isMotionJpeg = True
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid(): # All validation rules pass
            nowWidth = int(form.cleaned_data['size'])
            #msg += "selected size %s"%(nowWidth)
        else :
            msg += "invalid data"
    else :
        form = SizeForm({'size':nowWidth}) # An unbound form
    if nowWidth > maxWidth :    # 文字列比較になっていたので数値比較になるようnowWidthをint()で型変換
        nowWidth = maxWidth
    elif nowWidth < minWidth :
        nowWidth = minWidth
    nowHeight = int(float(maxHeight) * (float(nowWidth) / float(maxWidth)))
    #t = loader.get_template('launcher/live.html')
    template = loader.get_template('launcher/live2.html')
    #msg += "nowWidth=%d, nowHeight=%d"%(nowWidth, nowHeight)
    context = {
        'size_form' : form,
        'width' : nowWidth,
        'height': nowHeight,
        'msg':msg,
        'is_motion_jpeg' : isMotionJpeg, }
    return HttpResponse(template.render(context, request))


def cursorPad(request) :
    template = loader.get_template('launcher/cursorPad.html')
    context = {}
    return HttpResponse(template.render(context, request))

def controlCommand(request, cmd="") :
    try :
        commander = RocketCommander()
    except CanNotGetRocketManager as e :
        print(e)
    else :
        data = commander.interpret(cmd)
    return HttpResponse(json.dumps(data), "application/json")

def snapshot(request) :
    template = loader.get_template('launcher/snapshot.html')
    context  = {}
    return HttpResponse(template.render(context, request))

def snapshot2(request) :
    template = loader.get_template('launcher/snapshot2.html')
    context = {}
    return HttpResponse(template.render(context, request))

