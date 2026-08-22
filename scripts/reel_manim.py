from manim import *

config.frame_width = 1080
config.frame_height = 1920

class MandiReelPortrait(Scene):
    def construct(self):
        # Title
        title = Text("Kullu Mandi Prices", font="UI Display", color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # Price data (commodity + price) – you can replace these with your actual data
        data = [
            ("Apple", "-"),
            ("Pear", "-"),
            ("Plum", "-"),
            ("Peach", "-"),
            ("Tomato", "-"),
            ("Cabbage", "-"),
            ("Cauliflower", "-"),
            ("Potato", "-"),
            ("Onion", "-"),
            ("Carrot", "-"),
        ]

        # Create Text objects for each line
        texts = VGroup(*[
            Text(f"{name}: {price}", font="UI Mono", color=WHITE)
            for name, price in data
        ])
        # Stack them vertically with some spacing
        texts.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        # Center the group horizontally and position below title
        texts.to_edge(DOWN, buff=1.0)
        # Optional: add a semi-transparent background rectangle
        bg = Rectangle(
            width=config.frame_width - 1,
            height=config.frame_height - 2.5,
            fill_color=BLACK,
            fill_opacity=0.4,
            stroke_color=WHITE,
        )
        bg.move_to(ORIGIN)

        self.add(bg)
        self.play(Write(texts))
        self.wait(3)
