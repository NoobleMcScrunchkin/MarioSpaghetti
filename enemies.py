#Imports
import pygame as pg
from settings import *
#Vectors
vec = pg.math.Vector2

#Enemy Code
class Enemy(pg.sprite.Sprite):
    #Create the Enemy and add it to enemies group
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.dir = 1
        self.xdir = 1
        self.last_update = 0
        self.current_frame = 0
        self.image = self.game.spritesheet.get_image(14, 61, 16, 28)

        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.acc = vec(0, 0)

        self.load_images()
        self.rect = self.image.get_rect()

    #Load Enemy images
    def load_images(self):
        self.standing_frame = self.game.spritesheet5.get_image(0, 16, 16, 16)
        self.standing_frame.set_colorkey((255, 127, 39))

        self.walk_frames_l = [self.game.spritesheet5.get_image(0, 16, 16, 16),
                              self.game.spritesheet5.get_image(16, 16, 16, 16)]
        self.walk_frames_r = []
        for frame in self.walk_frames_l:
            frame.set_colorkey((255, 127, 39))
            self.walk_frames_r.append(pg.transform.flip(frame, True, False))

    #Do the walking animation for the Enemy
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
            if now - self.last_update > 120:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        self.mask = pg.mask.from_surface(self.image)

    #Check for collisions with walls and players
    def collide_with_walls(self, dir):
        if dir == 'y':
            #Did the enemy hit the floor
            hits = pg.sprite.spritecollide(self, self.game.walls, False)

            #Stop the enemy moving downwards
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

            #Did the enemy hit the player
            hits = pg.sprite.spritecollide(self, self.game.player1G, False)

            #Is the player also moving down?
            if hits and self.game.player.vel.y > 0:
                #Play a sfx and make the player jump
                self.game.squish_sound.play()
                self.game.jumped = True
                self.kill()

            #Did the enemy hit player 2
            hits = pg.sprite.spritecollide(self, self.game.player2G, False)

            #Is the player also moving down?
            if hits and self.game.player2.vel.y > 0:
                #Play a sfx and make the player jump
                self.game.squish_sound.play()
                self.game.jumped2 = True
                self.kill()


        if dir == 'x':
            #Did the enemy hit a wall
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            hits2 = pg.sprite.spritecollide(self, self.game.qblocks, False)

            #Stop the enemy when it hits a wall
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

                #Change the direction
                if self.xdir == 1:
                    self.xdir = 0
                else:
                    self.xdir = 1

            #Did player 1 hit the enemy
            hits = pg.sprite.spritecollide(self, self.game.player1G, False)
            if hits and self.game.player.vel.y == 0:
                #Kill the player
                self.game.play_dead()
                self.game.dead = True
                self.game.lives -= 1

            #Did player 2 hit the enemy
            hits = pg.sprite.spritecollide(self, self.game.player2G, False)
            if hits and self.game.player2.vel.y == 0:
                #Kill the player
                self.game.play_dead()
                self.game.dead = True
                self.game.lives -= 1

    #check wall collisions and move the enemy
    def update(self, game):
        if not self.game.dead:
            #Animate the enemy
            self.animate()

            #Stop the enemy if it is barely moving
            if self.vel.x < 1 and self.vel.x > -1:
                self.vel.x = 0

            #Set the gravity
            self.acc = vec(0, PLAYER_GRAV)

            #Move the enemy left or right
            if self.xdir == 1:
                self.acc.x = PLAYER_ACC / 1.25
            else:
                self.acc.x = -PLAYER_ACC / 1.25

            #Change the position and add friction
            self.acc.x += self.vel.x * PLAYER_FRICTION
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            #Move the player and chek for check for collision
            self.rect.x = self.pos.x
            self.collide_with_walls('x')
            self.rect.y = self.pos.y
            self.collide_with_walls('y')

            #If the enemy falls off a cliff kill it
            if self.pos.y > HEIGHT * 2:
                self.kill()
