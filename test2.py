from kivy.properties import ListProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput


class Chooser(TextInput):
    choicesfile = StringProperty()
    choiceslist = ListProperty([])

    def __init__(self, **kwargs):
        self.choicesfile = kwargs.pop('choicesfile', '')  # each line of file is one possible choice
        self.choiceslist = kwargs.pop('choiceslist', [])  # list of choices
        super(Chooser, self).__init__(**kwargs)
        self.multiline = False
        self.halign = 'left'
        self.bind(choicesfile=self.load_choices)
        self.bind(text=self.on_text)
        self.load_choices()
        self.dropdown = None

    def open_dropdown(self, *args):
        if self.dropdown:
            self.dropdown.open(self)

    def load_choices(self):
        if self.choicesfile:
            with open(self.choicesfile) as fd:
                for line in fd:
                    self.choiceslist.append(line.strip('\n'))
        self.values = []

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if self.suggestion_text and keycode[0] == ord('\r'):  # enter selects current suggestion
            self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.text = self.values[0]
            if self.dropdown:
                self.dropdown.dismiss()
                self.dropdown = None
        else:
            super(Chooser, self).keyboard_on_key_down(window, keycode, text, modifiers)

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        values = []
        for addr in self.choiceslist:
            if addr.startswith(text):
                values.append(addr)
        self.values = values
        if len(values) > 0:
            if len(self.text) < len(self.values[0]):
                self.suggestion_text = self.values[0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for val in self.values:
                self.dropdown.add_widget(Button(text=val, size_hint_y=None, height=48, on_release=self.do_choose))
            self.dropdown.open(self)

    def do_choose(self, butt):
        self.text = butt.text
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.relativelayout import RelativeLayout

    class TestApp(App):
        def build(self):
            layout = RelativeLayout()
            choices = ['Abba', 'dabba', 'doo']
            chooser = Chooser(choiceslist=choices, hint_text='Enter one of Fred\'s words', size_hint=(0.5,None), height=30, pos_hint={'center_x':0.5, 'center_y':0.5})
            layout.add_widget(chooser)
            return layout


    TestApp().run()