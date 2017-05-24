from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy import graphics
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
 
class VisualizationApp(App):
    def build(self):
        layout = RelativeLayout()
        layout.add_widget(Blob())
        return layout


class Blob(Scatter):
    size_hint = None, None
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (50, 50))
        super().__init__(**kwargs)
        #self.bind(pos=self.update_canvas)
        #self.bind(size=self.update_canvas)
        #self.update_canvas()

        r = self.size[0] / 2

        with self.canvas.before:
            graphics.Color(0.5, 0.5, 0.5)
            self.bg_ellipse = graphics.Ellipse(pos=(-r, -r), size=self.size)

        self.add_widget(Label(text='abcde',
                              x=-r, y=-r, size=self.size,
                              color=(0, 0, 0, 0.7),
                              valign='center', halign='center',
                              font_name='LiberationMono-Bold',
                              ))


    def collide_point(self, x, y):
        r = self.size[0]/2
        x +=  - self.pos[0]
        y +=  - self.pos[1]
        print(x, y, self.size)
        return x**2 + y**2 < r ** 2

VisualizationApp().run()
