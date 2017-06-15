#imports
import pygame as pg
from settings import *
from time import *
#Vectors
vec = pg.math.Vector2

#Loads and clips the spritesheets
class Spritesheet:
    #Load the spritesheet
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    #Get and scale images for players from the spritesheet
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2 * 4, height // 2 * 4))
        return image

    #Get and scale images for blocks from the spritesheet
    def get_image2(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        if TILESIZE == 16:
            image = pg.transform.scale(image, (width, height))
        else:
            image = pg.transform.scale(image, (width * 2, height * 2))
        return image

#Class for both players
class Player(pg.sprite.Sprite):
    #Create Player and the variables
    def __init__(self, game, x, y, numplayer):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.numplayer = numplayer
        self.game = game
        self.jumping = False
        self.jumping2 = False
        self.canJump = True
        self.canJump2 = True
        self.finished = False
        self.stopped = False
        self.hitpole = False
        self.dir = 1
        self.last_update = 0
        self.current_frame = 0
        self.image = self.game.spritesheet.get_image(80, 1, 16, 32)
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.acc = vec(0, 0)
        if self.numplayer == 1:
            self.load_images()
        else:
            self.load_images2()
        self.rect = self.image.get_rect()

    #Load images for player 1
    def load_images(self):
        self.standing_frame = self.game.spritesheet.get_image(80, 1, 16, 32)
        self.standing_frame.set_colorkey((255, 127, 39))
        self.walk_frames_r = [self.game.spritesheet.get_image(97, 1, 16, 32),
                              self.game.spritesheet.get_image(114, 1, 16, 32),
                              self.game.spritesheet.get_image(131, 1, 16, 32)]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey((255, 127, 39))
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(165, 1, 16, 32)
        self.jump_frame.set_colorkey((255, 127, 39))
        self.jump_frame2 = []
        self.jump_frame2.append(pg.transform.flip(self.jump_frame, True, False))

    #Load images for player 2
    def load_images2(self):
        self.standing_frame = self.game.spritesheet.get_image(80, 66, 16, 32)
        self.standing_frame.set_colorkey((255, 127, 39))

        self.walk_frames_r = [self.game.spritesheet.get_image(97, 66, 16, 32),
                              self.game.spritesheet.get_image(114, 66, 16, 32),
                              self.game.spritesheet.get_image(131, 66, 16, 32)]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey((255, 127, 39))
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(165, 66, 16, 32)
        self.jump_frame.set_colorkey((255, 127, 39))
        self.jump_frame2 = []
        self.jump_frame2.append(pg.transform.flip(self.jump_frame, True, False))

    #Change player image based on current state
    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x < 0:
            self.dir = 2
        elif self.vel.x > 0:
            self.dir = 1
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if now - self.last_update > 60:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if self.numplayer == 1:
            if self.jumping == True:
                if self.dir == 2:
                    self.image = self.jump_frame2[0]
                elif self.dir == 1:
                    self.image = self.jump_frame

            if self.jumping == False and self.vel.x == 0:
                if self.dir == 1:
                    self.image = self.standing_frame
                elif self.dir == 2:
                    self.image = pg.transform.flip(self.standing_frame, True, False)

        if self.numplayer == 2:
            if self.jumping2 == True:
                if self.dir == 2:
                    self.image = self.jump_frame2[0]
                elif self.dir == 1:
                    self.image = self.jump_frame

            if self.jumping2 == False and self.vel.x == 0:
                if self.dir == 1:
                    self.image = self.standing_frame
                elif self.dir == 2:
                    self.image = pg.transform.flip(self.standing_frame, True, False)

        self.mask = pg.mask.from_surface(self.image)

    #Set player accelerations
    def get_keys(self):
        keys = pg.key.get_pressed()
        if self.numplayer == 1:
            #If the game isnt finished
            if not self.finished and not self.hitpole:

                #Move the player left
                if keys[pg.K_a]:
                    self.acc.x = -PLAYER_ACC

                #Move the player right
                if keys[pg.K_d]:
                    self.acc.x = PLAYER_ACC

                #If the player jumped, move the player up
                if self.game.jumped == True:
                    self.vel.y = 0
                    self.game.jumped = False
                    self.jumping = True
                    self.canJump = False
                    if self.game.hitenemy1 == True:
                        self.acc.y = (-PLAYER_JUMP / 4) * 3
                        self.game.hitenemy1 = False
                    else:
                        self.acc.y = -PLAYER_JUMP

            #If the player hit the bottom of the flagpole, move the player right
            elif self.finished and not self.stopped:
                self.acc.x = PLAYER_ACC

            #If the player is on the flagpole then move it down
            elif self.hitpole and not self.finished:
                self.vel.x = 0
                self.vel.y = 2

            else:
                #Go to the next level
                if self.game.levelend == True:
                    self.game.level += 1
                    self.game.new()

        if self.numplayer == 2:
            #If the game isnt finished
            if not self.finished and not self.hitpole:

                #Move the player left
                if keys[pg.K_LEFT]:
                    self.acc.x = -PLAYER_ACC

                #Move the player right
                if keys[pg.K_RIGHT]:
                    self.acc.x = PLAYER_ACC

                #If the player jumped, make it go up
                if self.game.jumped2 == True:
                    self.vel.y = 0
                    self.game.jumped2 = False
                    self.jumping2 = True
                    self.canJump2 = False
                    if self.game.hitenemy2 == True:
                        self.acc.y = (-PLAYER_JUMP / 4) * 3
                        self.game.hitenemy2 = False
                    else:
                        self.acc.y = -PLAYER_JUMP

            #Did the player get to the end of the flagpole
            elif self.finished and not self.stopped:
                #Move the player right
                self.acc.x = PLAYER_ACC

            #Is the player on the flagpole
            elif self.hitpole and not self.finished:
                #Move the player down
                self.vel.x = 0
                self.vel.y = 2

            else:
                #Go to the next level
                if self.game.levelend == True:
                    self.game.level += 1
                    self.game.new()

    #Check for collision with blocks
    def collide_with_walls(self, dir):
        if dir == 'x':
            #Test for collision
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            hits2 = pg.sprite.spritecollide(self, self.game.qblocks, False)

            #Did the player hit the floor. If so stop them from falling
            if hits or hits2:
                if self.vel.x > 0:
                    try:
                        self.pos.x = hits[0].rect.left - self.rect.width
                    except:
                        self.pos.x = hits2[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    try:
                        self.pos.x = hits[0].rect.right
                    except:
                        self.pos.x = hits2[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x

            #Next three are for detecting where the player is on the flagpole
            hits = pg.sprite.spritecollide(self, self.game.fblocks, False)
            if hits:
                self.finished = True

            hits = pg.sprite.spritecollide(self, self.game.ends, False)
            if hits:
                self.stopped = True

            hits = pg.sprite.spritecollide(self, self.game.poles, False)
            if hits:
                self.hitpole = True

            #Did the player enter a pipe
            hits = pg.sprite.spritecollide(self, self.game.pipes, False)
            if hits:
                self.game.sub = True
                self.game.new()
                self.game.sub = False

        if dir == 'y':
            #Test for collision
            hits = pg.sprite.spritecollide(self, self.game.qblocks, False)
            hits2 = pg.sprite.spritecollide(self, self.game.walls, False)

            #Did the player hit a coin block
            if hits and self.vel.y < 0:
                #Increase score and play sfx
                self.game.score += 1
                self.game.coin_sound.play()

            #If they hit a block stop the player
            if hits or hits2:
                if self.vel.y > 0:
                    try:
                        self.pos.y = hits[0].rect.top - self.rect.height
                    except:
                        self.pos.y = hits2[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    try:
                        self.pos.y = hits[0].rect.bottom
                    except:
                        self.pos.y = hits2[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

                #allow the player to jump
                if self.numplayer == 1:
                    self.canJump = True
                    self.jumping = False
                else:
                    self.canJump2 = True
                    self.jumping2 = False

    #Run collision, Move the player and run animations
    def update(self, game):
        #If neither player is dead animate the players
        if not self.game.dead:
            self.animate()
            if self.vel.x < 1 and self.vel.x > -1:
                self.vel.x = 0

            #Set the gravity
            self.acc = vec(0, PLAYER_GRAV)

            #Get player inputs
            self.get_keys()

            #If either player dies stop the player from moving
            if self.game.dead:
                self.vel.x = 0
                self.vel.y = 0
                self.acc.x = 0
                self.acc.y = 0

            #Change coordinates and add gravity and friction
            self.acc.x += self.vel.x * PLAYER_FRICTION
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            #Move and check for collision
            self.rect.x = self.pos.x
            self.collide_with_walls('x')
            self.rect.y = self.pos.y
            self.collide_with_walls('y')

#Class for obsticles
class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, tile):
        self.game = game
        #Add different obsticles to groups
        if tile == 'qblock':
            self.groups = game.qblocks
        elif tile == 'block':
            self.groups = game.walls
        elif tile == 'fblock':
            self.groups = game.fblocks
        elif tile == 'end':
            self.groups = game.ends
        elif tile == 'sub':
            self.groups = game.pipes
        elif tile == 'pole':
            self.groups = game.poles
        #Create invisible sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
