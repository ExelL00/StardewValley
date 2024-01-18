import pygame
from setting import *
from player import Player
from overlay import Overlay
from sprites import Generic,Water,WildFlower,Tree,Interaction,Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import Soillayer
from sky import Rain, Sky
from random import randint
from menu import Menu

class Level:
    def __init__(self):
        #get the display surface
        self.display_surface=pygame.display.get_surface()

        #sprite groups
        self.all_sprites=CameraGroup()
        self.collision_sprites=pygame.sprite.Group()
        self.tree_sprites=pygame.sprite.Group()
        self.interaction_sprites=pygame.sprite.Group()

        self.SoilLayer = Soillayer(self.all_sprites,self.collision_sprites)
        self.setup()
        self.overlay=Overlay(self.player)
        self.transition= Transition(self.reset,self.player)

        #sky
        self.rain=Rain(self.all_sprites)
        self.raining=randint(0,10)>7
        self.SoilLayer.raining=self.raining
        self.sky=Sky()

        #shop
        self.shop_active=False
        self.menu=Menu(self.player,self.toggle_shop)

        #sound
        self.succes=pygame.mixer.Sound('audio/success.wav')
        self.succes.set_volume(0.3)

        self.music=pygame.mixer.Sound('audio/music.mp3')
        self.music.set_volume(0.1)
        self.music.play(loops=-1)

    def setup(self):
        tmx_data=load_pygame('data/map.tmx')

        #House
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(pos = (x * TILE_SIZE,y * TILE_SIZE),
                        surf = surf ,
                        groups = self.all_sprites,
                        z =LAYERS['house bottom'])

        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(pos = (x * TILE_SIZE,y * TILE_SIZE),
                        surf = surf ,
                        groups = self.all_sprites)

        #Fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(pos = (x * TILE_SIZE,y * TILE_SIZE),
                        surf = surf ,
                        groups = [self.all_sprites, self.collision_sprites])

        #Water
        water_frames=import_folder('graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water(pos = (x * TILE_SIZE,y * TILE_SIZE),
                        frames = water_frames,
                        groups = self.all_sprites)

        #Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos = (obj.x,obj.y),
                 surf = obj.image,
                 groups = [self.all_sprites, self.collision_sprites,self.tree_sprites],
                 name = obj.name,
                 player_add=self.player_add)

        #Wildflower
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower(pos = (obj.x,obj.y),
                       surf = obj.image,
                       groups = [self.all_sprites, self.collision_sprites])

        #collision tilse

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic(pos = (x * TILE_SIZE, y * TILE_SIZE),
                    surf = pygame.Surface((TILE_SIZE,TILE_SIZE)),
                    groups = self.collision_sprites)

        #Player setup
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name=='Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    colision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites,
                    soil_layer=self.SoilLayer,
                    toggle_shop=self.toggle_shop)
            if obj.name=='Bed':
                Interaction(pos=(obj.x,obj.y),
                            size=(obj.width,obj.height),
                            groups=self.interaction_sprites,
                            name=obj.name)
            if obj.name=='Trader':
                Interaction(pos=(obj.x,obj.y),
                            size=(obj.width,obj.height),
                            groups=self.interaction_sprites,
                            name=obj.name)

        #hitbox_draw
        '''
        for sprite in self.collision_sprites:
            Generic(pos=(sprite.hitbox.x, sprite.hitbox.y),
                    surf=pygame.Surface((sprite.hitbox.width, sprite.hitbox.height)),
                    groups=self.all_sprites)
        '''
        #background
        Generic(pos=(0,0),
                surf=pygame.image.load('graphics/world/ground.png').convert_alpha(),
                groups=self.all_sprites,
                z=LAYERS['ground'])

    def player_add(self,item):
        self.player.item_inventory[item]+=1
        #sound
        self.succes.play()
        
    def toggle_shop(self):
        self.shop_active =  not self.shop_active

    def reset(self):
        #plants
        self.SoilLayer.update_plants()

        #Soil
        self.SoilLayer.remove_water()

        #randomize the rain
        self.raining = randint(0, 10) > 7
        self.SoilLayer.raining=self.raining
        if self.raining:
            self.SoilLayer.water_all()

        #apples on the trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        #sky
        self.sky.start_color=[255,255,255]

    def plant_colision(self):
        if self.SoilLayer.plant_sprites:
            for plant in self.SoilLayer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(pos=plant.rect.topleft,
                             surf=plant.image,
                             groups=self.all_sprites,
                             z=LAYERS['main'])
                    x=plant.rect.centerx//TILE_SIZE
                    y=plant.rect.centery//TILE_SIZE
                    self.SoilLayer.grid[y][x].remove('P')

    def run(self):
        #drawing logic
        self.all_sprites.custom_draw(self.player)

        #updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update()
            self.plant_colision()

        #weather
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display()

        #transition overlay
        if self.player.sleep:
            self.transition.play()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.dsiplay_surface=pygame.display.get_surface()
        self.offset=pygame.math.Vector2()

    def custom_draw(self,player):
        self.offset.x=player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y=player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if layer==sprite.z:
                    offset_rect=sprite.rect.copy()
                    offset_rect.center-=self.offset
                    self.dsiplay_surface.blit(sprite.image,offset_rect)







