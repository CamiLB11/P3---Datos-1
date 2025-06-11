import pygame

class Ciudad:
    def __init__(self, image_path, position):
        self.position = position
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft = position)
        self.pressed = False

    def draw(self, window):
        window.blit(self.image, self.rect)

    def get_pos(self):
        return self.position
    
    def is_pressed(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed and not self.pressed:
                self.pressed = True
                return True
            if not mouse_pressed:
                self.pressed = False
        return False