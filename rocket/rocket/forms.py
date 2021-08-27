from django import forms


class CommandForm(forms.Form):
    command = forms.CharField(max_length=256)


class SizeForm(forms.Form):
    size = forms.ChoiceField(choices=[(1280, "1280x720"),
                                      (1024, "1024x576"),
                                      (640, "640x360"),
                                      (320, "320x180")])
