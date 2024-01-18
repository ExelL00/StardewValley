import pygame
from setting import *
from pytmx.util_pygame import load_pygame
from support import import_folder_disct,import_folder
from random import choice

class SoilTitle(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image=surf
        self.rect=self.image.get_rect(topleft=pos)
        self.z=LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image=surf
        self.rect=self.image.get_rect(topleft=pos)
        self.z=LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
    def __init__(self,plant_type,groups,soil,check_watered):
        super().__init__(groups)
        #setup
        self.plant_type=plant_type
        self.frames=import_folder(f'graphics/fruit/{plant_type}')
        self.soil=soil
        self.check_watered=check_watered

        #plant growing
        self.age=0
        self.max_age=len(self.frames)-1
        self.grow_speed=GROW_SPEED[plant_type]
        self.harvestable=False

        #sprite setup
        self.image=self.frames[self.age]
        self.y_offset=- 16 if plant_type=='corn' else -8
        self.rect=self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
        self.z=LAYERS['ground plant']
    def grow(self):
        if self.check_watered(self.rect.center):
            self.age+=self.grow_speed

            if int(self.age)>0:
                self.z=LAYERS['main']
                self.hitbox=self.rect.copy().inflate(-26,-self.rect.height * 0.4)

            if self.age>=self.max_age:
                self.age=self.max_age
                self.harvestable=True

            self.image=self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))

class Soillayer:
    def __init__(self,all_sprites,collision_sprites):

        #sprites groups
        self.all_spirtes=all_sprites
        self.collision_sprites=collision_sprites
        self.soil_sprites=pygame.sprite.Group()
        self.water_sprites=pygame.sprite.Group()
        self.plant_sprites=pygame.sprite.Group()

        #graphics
        self.soil_surfs=import_folder_disct('graphics/soil')
        self.water_surfs=import_folder('graphics/soil_water')


        self.create_soil_frid()
        self.create_hit_rects()

        #sound
        self.hoe_sound=pygame.mixer.Sound('audio/hoe.wav')
        self.hoe_sound.set_volume(0.1)

        self.plant_sound=pygame.mixer.Sound('audio/plant.wav')
        self.plant_sound.set_volume(0.2)
    def create_soil_frid(self):
        ground=pygame.image.load('graphics/world/ground.png')
        h_titles=ground.get_width()//TILE_SIZE
        v_titles=ground.get_height()//TILE_SIZE

        self.grid=[[[] for col in range(h_titles)] for row in range(v_titles)]
        for x, y, _ in load_pygame('data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects=[]
        for index_row,row in enumerate(self.grid):
            for index_cell, cell in enumerate(row):
                if 'F' in cell:
                    x= index_cell * TILE_SIZE
                    y= index_row * TILE_SIZE
                    rect=pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self,point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                #sound
                self.hoe_sound.play()

                x= rect.x//TILE_SIZE
                y= rect.y//TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self,target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):

                x= soil_sprite.rect.x//TILE_SIZE
                y= soil_sprite.rect.y//TILE_SIZE
                self.grid[y][x].append('W')

                pos= soil_sprite.rect.topleft
                surf = choice(self.water_surfs)
                WaterTile(pos=pos,
                          surf=surf,
                          groups=[self.all_spirtes,self.water_sprites])

    def water_all(self):
        for index_row,row in enumerate(self.grid):
            for index_col,cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x=index_col*TILE_SIZE
                    y=index_row*TILE_SIZE
                    WaterTile(pos=(x,y),
                          surf=choice(self.water_surfs),
                          groups=[self.all_spirtes,self.water_sprites])

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self,pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered='W' in cell
        return is_watered

    def plant_seed(self,target_pos,seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                #sound
                self.plant_sound.play()
                x=soil_sprite.rect.x//TILE_SIZE
                y=soil_sprite.rect.y//TILE_SIZE

                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed,[self.all_spirtes,self.plant_sprites,self.collision_sprites],soil_sprite,self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row,row in enumerate(self.grid):
            for index_cell, cell in enumerate(row):
                if 'X' in cell:
                    x=index_cell * TILE_SIZE
                    y=index_row * TILE_SIZE

                    #title options
                    t= 'X' in self.grid[index_row - 1][index_cell]
                    b= 'X' in self.grid[index_row + 1][index_cell]
                    r= 'X' in row[index_cell + 1]
                    l= 'X' in row[index_cell - 1]

                    soil_type='o'

                    #all sides
                    if all((t,b,r,l)): soil_type='x'

                    #horizonatal tiles only
                    if l and not any((t,r,b)): soil_type='r'
                    if r and not any((t,l,b)): soil_type='l'
                    if r and l and not any((t,b)): soil_type='lr'

                    #vertical tiles only
                    if t and not any((r,l,b)): soil_type='b'
                    if b and not any((r,l,t)): soil_type='t'
                    if t and b and not any((r,l)): soil_type='tb'

                    #corners
                    if l and b and not any((t,r)): soil_type = 'tr'
                    if r and b and not any((t,l)): soil_type = 'tl'
                    if l and t and not any((b,r)): soil_type = 'br'
                    if r and t and not any((b,l)): soil_type = 'bl'

                    #T shapes
                    if all((t,b,r)) and not l: soil_type='tbr'
                    if all((t,b,l)) and not r: soil_type='tbl'
                    if all((l,r,t)) and not b: soil_type='lrb'
                    if all((l,r,b)) and not t: soil_type='lrt'

                    SoilTitle(pos=(x,y),
                              surf=self.soil_surfs[soil_type],
                              groups=[self.all_spirtes,self.soil_sprites])

