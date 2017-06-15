#Imports
import pytmx
import pygame as pg
from settings import *
from os import path

#Renders and Draws the Map
class TiledMap:
    #Load the Map
    def __init__(self, filename):
        #Load and enable transparancy
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    #Render the Map
    def render(self, surface):
        #add the map to ti
        ti = self.tmxdata.get_tile_image_by_gid

        #Load the folders
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')

        #Look at the objects
        for tile_object in self.tmxdata.objects:
            #Is it an overworld map?
            if tile_object.name == 'blue':
                #Make the background blue and use coin.png and overworld music
                surface.fill((0,170,255))
                self.coin = pg.image.load(path.join(img_folder, 'coin.png'))
                pg.mixer.music.load(path.join(snd_folder, 'Super Mario Bros (NES) Music - Overworld Theme.ogg'))

            #Is it an underground map?
            elif tile_object.name == 'black':
                #Make the background black and use coin2.png and underground music
                surface.fill((0,0,0))
                self.coin = pg.image.load(path.join(img_folder, 'coin2.png'))
                pg.mixer.music.load(path.join(snd_folder, 'Super Mario Bros (NES) Music - Underground Theme.ogg'))

        #Draws all the visible layers of the map
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,y * self.tmxdata.tileheight))

    #Draw the map
    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

#Makes the camera
class Camera:
    #Set Camera Variables
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    #Move the camera to the player
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    #Move the camera to the player
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    #Update the camera
    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom

        #Move the camera
        self.camera = pg.Rect(x, y, self.width, self.height)
