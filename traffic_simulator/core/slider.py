import pygame

class Slider:
    def __init__(self, pos:tuple, size:tuple, initial_val:float, min:int, max:int) -> None:
        self.pos = pos
        self.size = size

        self.slider_left_pos = self.pos[0] - (size[0]//2)
        self.slider_right_pos = self.pos[0] + (size[0]//2)
        self.slider_top_pos = self.pos[1] - (size[1]//2)

        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos-self.slider_left_pos)*initial_val

        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])

    def render(self, app):
        pygame.draw.rect(app, "darkgray", self.container_rect)
        pygame.draw.rect(app, "black", self.button_rect)

    def move_slider(self, mouse_pos):
        new_x = mouse_pos[0]
        new_x = max(self.slider_left_pos, min(new_x, self.slider_right_pos)) ## --Espacio maximo y minimo para moverse
        self.button_rect.centerx = new_x

    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos
        button_val = self.button_rect.centerx - self.slider_left_pos

        return (button_val/val_range)*(self.max-self.min)+self.min