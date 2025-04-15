from sfml import sf

class VirtualScreen:
    def __init__(self):
        self.vertices = sf.VertexArray()
        self.screen_size = (0, 0)
        self.pixel_size = 0.0

    def create(self, width: int, height: int, pixel_size: float, color: sf.Color):
        self.vertices = sf.VertexArray(sf.PrimitiveType.TRIANGLES, width * height * 6)
        self.screen_size = (width, height)
        self.pixel_size = pixel_size

        for x in range(width):
            for y in range(height):
                index = (x * self.screen_size[1] + y) * 6
                coord2d = sf.Vector2f(x * self.pixel_size, y * self.pixel_size)

                # Triangle 1
                self.vertices[index + 0].position = coord2d
                self.vertices[index + 0].color = color

                self.vertices[index + 1].position = coord2d + sf.Vector2f(pixel_size, 0)
                self.vertices[index + 1].color = color

                self.vertices[index + 2].position = coord2d + sf.Vector2f(pixel_size, pixel_size)
                self.vertices[index + 2].color = color

                # Triangle 2
                self.vertices[index + 3].position = coord2d + sf.Vector2f(pixel_size, pixel_size)
                self.vertices[index + 3].color = color

                self.vertices[index + 4].position = coord2d + sf.Vector2f(0, pixel_size)
                self.vertices[index + 4].color = color

                self.vertices[index + 5].position = coord2d
                self.vertices[index + 5].color = color

    def set_pixel(self, x: int, y: int, color: sf.Color):
        index = (x * self.screen_size[1] + y) * 6
        if index + 5 >= len(self.vertices):
            return

        coord2d = sf.Vector2f(x * self.pixel_size, y * self.pixel_size)

        for i in range(6):
            self.vertices[index + i].color = color

    def draw(self, target: sf.RenderTarget, states: sf.RenderStates):
        target.draw(self.vertices, states)