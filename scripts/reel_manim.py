from manim import *

class MandiReel(Scene):
    def construct(self):
        # Title
        title = Text("Kullu Mandi Prices", font="UI Display", color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))

        # Price data
        data = [('Apple', '₹60.0'), ('Pear', '-'), ('Plum', '-'), ('Peach', '-'), ('Tomato', '-'), ('Cabbage', '-'), ('Cauliflower', '-'), ('Potato', '₹16.0'), ('Onion', '₹43.0'), ('Carrot', '₹35.0')]

        # Create a VGroup of Text objects, one per commodity
        texts = VGroup(*[Text(f"{name}: {price}", font="UI Mono") for name, price in data])
        texts.arrange(DOWN, aligned_edge=LEFT)
        texts.to_edge(DOWN)

        # Animate each text appearing
        for txt in texts:
            self.play(Write(txt))

        # Wait at the end
        self.wait(2)