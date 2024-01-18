import pygame
from setting import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, colision_sprites,tree_sprites,interaction_sprites,soil_layer,toggle_shop):
        super().__init__(group)

        self.import_assets()
        self.status='down_idle'
        self.frame_index=0

        self.image=self.animations[self.status][self.frame_index]
        self.rect=self.image.get_rect(center=pos)
        self.z=LAYERS['main']

        #movment attributes
        self.direction=pygame.math.Vector2()
        self.pos=pygame.math.Vector2(self.rect.center)
        self.speed=3

        #collsion
        self.hitbox=self.rect.copy().inflate((-126,-70))
        self.collsion_sprite = colision_sprites


        #timers
        self.timer={
            'tool use': Timer(350,self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200),
        }

        #tools
        self.tools=['hoe','axe','water']
        self.tool_index=0
        self.selected_tool=self.tools[self.tool_index]

        #seeds
        self.seeds=['corn','tomato']
        self.seeds_index=0
        self.selected_seed=self.seeds[self.seeds_index]

        #inventory
        self.item_inventory={
            'wood': 30,
            'apple': 30,
            'corn': 30,
            'tomato': 30
        }

        self.seed_inventory={
            'corn': 5,
            'tomato': 5
        }

        self.money=200

        #interaction
        self.tree_sprites=tree_sprites
        self.interaction_sprites=interaction_sprites
        self.sleep=False
        self.soillayer=soil_layer
        self.toggle_shop=toggle_shop

        #sound
        self.water_sound=pygame.mixer.Sound('audio/water.mp3')
        self.water_sound.set_volume(0.3)

    def use_tool(self):
        if self.selected_tool=='hoe':
            self.soillayer.get_hit(self.target_pos)

        if self.selected_tool=='axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool=='water':
            self.soillayer.water(self.target_pos)
            self.water_sound.play()

    def get_target(self):
        self.target_pos=self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soillayer.plant_seed(self.target_pos,self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}

        for animation in self.animations.keys():
            full_path='graphics/character/' + animation
            self.animations[animation]=import_folder(full_path)

    def animate(self):
        self.frame_index+=0.05
        if self.frame_index>=len(self.animations[self.status]):
            self.frame_index=0
        self.image=self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timer['tool use'].active and not self.sleep:
        #direction
            if keys[pygame.K_w]:
                self.direction.y=-1
                self.status='up'
            elif keys[pygame.K_s]:
                self.direction.y=1
                self.status='down'
            else:
                self.direction.y=0

            if keys[pygame.K_a]:
                self.direction.x=-1
                self.status='left'
            elif keys[pygame.K_d]:
                self.direction.x=1
                self.status='right'
            else:
                self.direction.x=0

            #tool use
            if keys[pygame.K_SPACE]:
                #timer for the tool use
                self.timer['tool use'].actication()
                self.direction=pygame.math.Vector2()
                self.frame_index=0

            #change tool
            if keys[pygame.K_q] and not self.timer['tool switch'].active:
                self.timer['tool switch'].actication()
                self.tool_index+=1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool=self.tools[self.tool_index]

            #seed use
            if keys[pygame.K_LCTRL]:
                self.timer['seed use'].actication()
                self.direction=pygame.math.Vector2()
                self.frame_index=0
            #change seed
            if keys[pygame.K_e] and not self.timer['seed switch'].active:
                self.timer['seed switch'].actication()
                self.seeds_index+=1
                self.seeds_index=self.seeds_index if self.seeds_index < len(self.seeds) else 0
                self.selected_seed=self.seeds[self.seeds_index]
            #interaction bed
            if keys[pygame.K_RETURN]:
                collided_interaction_sprites=pygame.sprite.spritecollide(self,self.interaction_sprites,False)
                if collided_interaction_sprites:
                    if collided_interaction_sprites[0].name=='Trader':
                        self.toggle_shop()
                    if collided_interaction_sprites[0].name=='Bed':
                        self.status='left_idle'
                        self.sleep=True

    def get_status(self):
        #idle
        #if the player is not moving
        if self.direction.magnitude()==0:
            #add _idle to the status
            self.status=self.status.split('_')[0]+'_idle'

        #tool use
        if self.timer['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timer.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collsion_sprite.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: #moving right
                            self.hitbox.right=sprite.hitbox.left
                        if self.direction.x < 0: #moving left
                            self.hitbox.left=sprite.hitbox.right
                        self.rect.centerx=self.hitbox.centerx
                        self.pos.x=self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0: #moving down
                            self.hitbox.bottom=sprite.hitbox.top
                        if self.direction.y < 0: #moving left
                            self.hitbox.top=sprite.hitbox.bottom
                        self.rect.centery=self.hitbox.centery
                        self.pos.y=self.hitbox.centery

    def move(self):
        #normalizing a vector
        if self.direction.magnitude():
            self.direction=self.direction.normalize()

        #horiznotal move
        self.pos.x += self.direction.x * self.speed
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')


        #vertical move
        self.pos.y+=self.direction.y*self.speed
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery=self.hitbox.centery
        self.collision('vertical')

    def update(self):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target()

        self.move()
        self.animate()