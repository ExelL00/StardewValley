import pygame,sys
from setting import *
from level import Level

class Game():
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption('Stardew Valley')
        self.level=Level()
        self.game()
    def game(self):
        while True:
            self.event()
            self.refresh_screen()
    def event(self):
        for events in pygame.event.get():
            if events.type==pygame.QUIT:
                sys.exit(0)
    def refresh_screen(self):
        self.screen.fill('black')
        pygame.time.Clock().tick(120)
        self.level.run()
        pygame.display.update()
if __name__ == '__main__':
    Game()