import pygame
from setting import *

class Overlay:
    def __init__(self, player):
        #general setup
        self.display_surface=pygame.display.get_surface()
        self.player=player

        #imports
        self.tools_surf={tool:pygame.image.load('graphics/overlay/'+tool+'.png').convert_alpha() for tool in player.tools}
        self.seeds_surf={seed:pygame.image.load('graphics/overlay/'+seed+'.png').convert_alpha() for seed in player.seeds}
    def display(self):
        #tools
        tools_surface=self.tools_surf[self.player.selected_tool]
        tools_rect=tools_surface.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tools_surface,tools_rect)

        #seeds
        seeds_surface = self.seeds_surf[self.player.selected_seed]
        seeds_rect=seeds_surface.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seeds_surface,seeds_rect)