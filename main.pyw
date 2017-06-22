#Imports
import sys
from os import path
from subprocess import Popen
try:
    import pygame as pg
    import pytmx
except:
    game_folder = path.dirname(__file__)
    bat = Popen(path.join(game_folder, "requirements.bat"))
    sys.exit()
from os import path
from settings import *
from sprites import *
from tilemap import *
from enemies import *
from time import *

#Main game class
class Game:
    #Initialize pygame and set starting variables
    def __init__(self):
        #Initialize pygame and the mixer
        pg.mixer.pre_init(44100,0,9)
        pg.init()
        pg.mixer.init()
        #Set Screen Size
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN, 32)
        #Set Windows Title
        pg.display.set_caption(TITLE)
        #Set FPS
        self.clock = pg.time.Clock()
        #Set starting variables
        self.level = 1
        self.sub = False
        self.lives = 5

    #Load images and maps
    def load_data(self):
        #Loads folders
        game_folder = path.dirname(__file__)
        self.img_folder = path.join(game_folder, 'img')
        map_folder = path.join(game_folder, 'map')
        self.snd_folder = path.join(game_folder, 'snd')

        #Figures out what map to load
        if self.sub == True:
            MAP = 'map' + str(self.level) + 'sub.tmx'
        else:
            MAP = 'map' + str(self.level) + '.tmx'

        #Loads and renders the map
        self.map = TiledMap(path.join(map_folder, MAP))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        #Load the spritesheets
        self.spritesheet = Spritesheet(path.join(self.img_folder, SPRITESHEET))
        self.spritesheet4 = Spritesheet(path.join(self.img_folder, SPRITESHEET4))
        self.spritesheet5 = Spritesheet(path.join(self.img_folder, SPRITESHEET5))

        #Load effects
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_folder, 'Jump.wav'))
        self.squish_sound = pg.mixer.Sound(path.join(self.snd_folder, 'Squish.wav'))
        self.coin_sound = pg.mixer.Sound(path.join(self.snd_folder, 'Coin.wav'))

    #Start the level
    def new(self):
        #Variables
        self.load_data()
        self.show_level_screen()
        self.jumped = False
        self.jumping = False
        self.jumped2 = False
        self.jumping2 = False
        self.hitenemy1 = False
        self.hitenemy2 = False
        self.score = 0
        self.finishedmusic = False
        self.finishedlevelclearmusic = False
        self.levelend = False
        self.time = 0
        self.deadtime = 0
        self.dead = False
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.qblocks = pg.sprite.Group()
        self.fblocks = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.players = pg.sprite.Group()
        self.player1G = pg.sprite.Group()
        self.player2G = pg.sprite.Group()
        self.pipes = pg.sprite.Group()
        self.ends = pg.sprite.Group()
        self.poles = pg.sprite.Group()
        self.liveblocks = pg.sprite.Group()

        #Create players and enemies based on where they are in the map. Also make the blocks where they are found on the map.
        for tile_object in self.map.tmxdata.objects:
            #Is the object the player?
            if tile_object.name == 'player':
                #Create Player 1 and add it to the group
                self.player = Player(self, tile_object.x, tile_object.y, 1)
                self.players.add(self.player)
                self.player1G.add(self.player)
                if self.playernum == 2:
                    #If players == 2 then make player 2 next to player 1
                    self.player2 = Player(self, tile_object.x + 32, tile_object.y, 2)
                    self.players.add(self.player2)
                    self.player2G.add(self.player2)
            #If the object is a block make the obstacle
            if tile_object.name == 'block' or tile_object.name == 'qblock' or tile_object.name == 'end' or tile_object.name == 'fblock' or tile_object.name == 'sub' or tile_object.name == 'pole':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)
            #If the object is an enemy then make the enemy
            if tile_object.name == 'enemy':
                Enemy(self, tile_object.x, tile_object.y, True)
            if tile_object.name == 'enemy2':
                Enemy(self, tile_object.x, tile_object.y, False)
            if tile_object.name == 'lives':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)


        #Create the camera
        self.camera = Camera(self.map.width, self.map.height)

        #Play the music
        pg.mixer.music.play(-1, 0.0)

    #Game Loop
    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            #Run functions
            self.events()
            self.update()
            self.draw()

    #Quits the game
    def quit(self):
        #Stops music
        pg.mixer.music.stop()
        #Closes the window
        pg.quit()
        sys.exit()

    #Main update function
    def update(self):
        #Updates every sprite
        self.all_sprites.update(self)

        #Moves the camera
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        if self.playernum == 2:
            if self.player.pos.x > self.player2.pos.x:
                self.camera.update(self.player)
            else:
                self.camera.update(self.player2)
        else:
            self.camera.update(self.player)

        #Draws the coin and the score
        self.draw_text(str(self.score), 50, 50, 5, False)
        self.screen.blit(self.map.coin, (5,12))

        #Draws the number of lives
        self.draw_text(str(self.lives), 50, WIDTH/2, 30, True)

        #Play music when hitting the flagpole
        if self.player.hitpole == True or self.playernum == 2 and self.player2.hitpole == True:
            if not self.finishedmusic:
                self.finishedmusic = True
                pg.mixer.music.stop()
                pg.mixer.music.load(path.join(self.snd_folder, 'Flagpole.wav'))
                pg.mixer.music.play(-0, 0.0)

        #Play music when at the bottom of the flagpole
        if self.player.finished and not self.player.stopped or self.playernum == 2 and self.player2.finished and not self.player2.stopped:
            if not self.finishedlevelclearmusic:
                self.finishedlevelclearmusic = True
                pg.mixer.music.stop()
                pg.mixer.music.load(path.join(self.snd_folder, 'Super Mario Bros (NES) Music - Level Clear.ogg'))
                pg.mixer.music.play(-0, 0.0)

        #If player 1 has finished stop player 2 from existing
        if self.player.stopped:
            self.time += 1
            self.player.vel.x = 0
            self.player.vel.y = 0
            try:
                self.player2.kill()
            except:
                pass
            if self.time > 300:
                self.levelend = True

        #If player 2 has finished stop player 1 from existing
        if self.playernum == 2 and self.player2.stopped:
            self.time += 1
            self.player2.vel.x = 0
            self.player2.vel.y = 0
            self.player.kill()
            if self.time > 300:
                self.levelend = True

        #If player 1 is off the screen kill the player and remove a life
        if self.player.pos.y > HEIGHT * 2 and not self.dead:
            self.lives -= 1
            self.play_dead()
            self.dead = True

        #If player 2 is off the screen kill the player and remove a life
        if self.playernum == 2:
            if self.player2.pos.y > HEIGHT * 2 and not self.dead:
                self.lives -= 1
                self.play_dead()
                self.dead = True

        #Timer for how long you are dead
        if self.dead:
            self.deadtime += 1

        #When the music is over restart the level or show the game over screen
        if self.deadtime > 180:
            if self.lives == 0:
                self.show_go_screen()
            else:
                self.new()

    #Plays death music
    def play_dead(self):
        #Stops current music then plays death music
        pg.mixer.music.stop()
        pg.mixer.music.load(path.join(self.snd_folder, 'Die.wav'))
        pg.mixer.music.play(-0, 0.0)

    #Updates the screen
    def draw(self):
        #Sets the title to the current FPS
        pg.display.set_caption("{: .2f}".format(self.clock.get_fps()))

        #Apply the camera
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        #Refreshes the screen
        pg.display.flip()

    #Closes the game if close is pressed and checks if either player has jumped
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            #Was a key pressed?
            if event.type == pg.KEYDOWN:
                #Was the key ESCAPE
                if event.key == pg.K_ESCAPE:
                    #Quit the game
                    self.quit()

                #Was the key w
                if event.key == pg.K_w and self.player.vel.y == 0:
                    #Make the player jump
                    if self.player.canJump == True:
                        self.jumped = True
                        self.jump_sound.play()

                #Are there 2 players and was up pressed
                if self.playernum == 2:
                    if event.key == pg.K_UP and self.player2.vel.y == 0:
                        #Make Player 2 jump
                        if self.player.canJump2 == True:
                            self.jumped2 = True
                            self.jump_sound.play()

    #Shows the start screen
    def show_start_screen(self):
        #Set the background colour
        self.screen.fill(BGCOLOUR)

        #Draw info text
        self.draw_text(TITLE, 100, WIDTH / 2, HEIGHT / 2 - 50, True)
        self.draw_text("WASD and Arrow Keys to move", 40, WIDTH / 2, HEIGHT / 2 + 20, True)
        self.draw_text("1 = 1 Player, 2 = 2 Player", 40, WIDTH / 2, HEIGHT - 40, True)

        #Refresh the screen and wait for an input
        pg.display.flip()
        self.wait()

    #Shows the level screen
    def show_level_screen(self):
        #Set the screen to BLACK
        self.screen.fill(BLACK)

        #Draw the level number
        self.draw_text("Level " + str(self.level), 100, WIDTH / 2, HEIGHT / 2, True)

        #Refresh the screen, wait and then continue
        pg.display.flip()
        pg.time.wait(1000)
        pg.time.wait(0)

    #Wait for the user to press 1 or 2 for how many players
    def wait(self):
        #While waiting for an input
        waiting = True
        while waiting:
            #Set the clock
            self.clock.tick(FPS)

            #Get the events
            for event in pg.event.get():

                #Was close pressed?
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()

                #Was a key pressed
                if event.type == pg.KEYUP:
                    #Was 1 pressed?
                    if event.key == pg.K_1:
                        #Continue with 1 players
                        waiting = False
                        self.playernum = 1

                    #Was 1 pressed?
                    if event.key == pg.K_2:
                        #Continue with 2 players
                        waiting = False
                        self.playernum = 2

    #Shows the gameover screen and plays game over music
    def show_go_screen(self):
        #Stop the music and kill sprites
        pg.mixer.music.stop()
        for sprites in self.all_sprites:
            sprites.kill()

        #Fill the screen
        self.screen.fill(RED)

        #Draw the GAME OVER text
        self.draw_text("GAME OVER!", 100, WIDTH / 2, HEIGHT / 2, True)

        #Refresh the screen
        pg.display.flip()

        #Play the game over music
        pg.mixer.music.load(path.join(self.snd_folder, 'Super Mario Bros (NES) Music - Game Over 1.ogg'))
        pg.mixer.music.play(-0, 0.0)

        #Wait for the music to end then go to main menu
        pg.time.wait(4000)
        self.level = 1
        self.sub = False
        self.lives = 5
        self.show_start_screen()

    #Setup Text
    def text_objects(self, text, font):
        textSurface = font.render(text, True, WHITE)
        return textSurface, textSurface.get_rect()

    #Draw the text
    def draw_text(self, text, size, x, y, pos):
        #Set the font and size
        largeText = pg.font.Font('comic.ttf',size)
        TextSurf, TextRect = self.text_objects(text, largeText)

        #Set the text position
        if pos == True:
            TextRect.center = (x,y)
        else:
            TextRect.topleft = (x,y)

        #Draw the text
        self.screen.blit(TextSurf, TextRect)

#Make the window and show start screen
g = Game()
g.show_start_screen()
#Starting Loop
while True:
    g.new()
    g.run()
