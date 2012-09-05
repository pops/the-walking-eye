#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys, os
import pygame
from pygame.locals import *

from functions import *

UNITE = 20

class Underfoot(pygame.sprite.Sprite):
    def __init__(self, width):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, width, 1)
        
        self.img = pygame.Surface((width, 1)).convert()
        self.img.fill(Color("#FF0000"))
        
    def is_collide(self, platform):
        coll = False
        for p in platform:
            if pygame.sprite.collide_rect(self, p):
                coll = True
        return coll
        
        
class Someone(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.onground = False
        self.xvec = 0 # horizontal
        self.yvec = 0 # vertical
        
    def tiles_to_check(self, tiletable):
        x, y = int(self.rect.center[0]/UNITE), int(self.rect.center[1]/UNITE)
        walltiles = []
        cloudtiles = []
        doortiles = []
        laddertiles = []
        for d in (tiletable[y][x], 
                   tiletable[y+1][x], 
                   tiletable[y][x+1], 
                   tiletable[y-1][x], 
                   tiletable[y][x-1], 
                   tiletable[y+1][x+1], 
                   tiletable[y-1][x-1], 
                   tiletable[y+1][x-1], 
                   tiletable[y-1][x+1]):
            if d.wall:
                walltiles.append(d)
            if d.cloud:
                cloudtiles.append(d)
            if d.ladder:
                laddertiles.append(d)
            if d.door:
                doortiles.append(d)
        return walltiles, cloudtiles, laddertiles, doortiles
        
    def is_onground(self, platform, platformcloud, yvec):
        if self.yvec < 0:
            return False
        self.underfoot.rect.topleft = (self.rect.left, self.rect.bottom)
        if self.is_collide(platform):
            return False
        if self.underfoot.is_collide(platform):
            return True
        for p in platformcloud:
            if not pygame.sprite.collide_rect(self, p) and pygame.sprite.collide_rect(self.underfoot, p):
                return True
        return False
        
    def is_collide(self, platform):
        for p in platform:
            if pygame.sprite.collide_rect(self, p):
                return True
        return False
        
        
class Badguy(Someone):
    def __init__(self, x, y, direction):
        Someone.__init__(self)
        self.rimg, self.rect = loadimg("mechant.png", True)
        self.limg = pygame.transform.flip(self.rimg, True, False)
        self.image = self.rimg
        self.rect.topleft = (x, y)
        self.xvec = direction
        self.underfoot = Underfoot(self.rect.width)
        
    def update(self, tiletable):
        """move hero and adjust if collision
        """
        walltiles, cloudtiles,  doortiles = self.tiles_to_check(tiletable)
        self.onground = self.is_onground(walltiles, cloudtiles, self.yvec)
        
        if self.onground == False:
            self.yvec += 1
        else:
            self.yvec = 0
        
            
        if self.xvec > 0:
            self.img = self.rimg
        elif self.xvec < 0:
            self.img = self.limg
        
        # check horizontal move
        self.rect = self.rect.move(self.xvec, 0)
        if self.xvec > 0:
            if self.is_collide(walltiles):
                self.rect = self.rect.move(-2, 0)
                self.xvec = -1
        elif self.xvec < 0:
            if self.is_collide(walltiles):
                self.rect = self.rect.move(2, 0)
                self.xvec = 1
        
        # check vertical move
        # check moving down
        if self.yvec > 0:
            for i in range(self.yvec):
                if not self.is_onground(walltiles, cloudtiles, self.yvec):
                    self.rect = self.rect.move(0, 1)
                else: break
        # check moving up
        elif self.yvec < 0:
            for i in range(-self.yvec):
                if not self.is_collide(walltiles):
                    self.rect = self.rect.move(0, -1)
                else: 
                    self.yvec = 0 # cogne au plafond
                    self.rect = self.rect.move(0, 1)
                    break
        
class Hero(Someone):
    def __init__(self):
        Someone.__init__(self)
        self.rimg, self.rect = loadimg("hero.png", True)
        self.limg = pygame.transform.flip(self.rimg, True, False)
        self.img = self.rimg
        self.underfoot = Underfoot(self.rect.width)
        self.onground = False
        self.onladder = False
        self.inladder = False
        self.hang = False
        
    def update(self, key, tiletable):
        """move hero and adjust if collision
        """
        walltiles, cloudtiles, laddertiles, doortiles = self.tiles_to_check(tiletable)
        self.onground = self.is_onground(walltiles, cloudtiles, self.yvec)
        self.inladder = self.is_collide(laddertiles)
        
        self.xvec = 0
        if self.onground == False:
            self.yvec += 1
        else:
            self.yvec = 0
        if key["jump"] and (self.onground or self.hang):
            self.yvec = -10
            self.hang = False
        
        if key["up"] and self.inladder:
            self.yvec = -2
            self.hang = True
        elif self.hang and self.inladder and not key["jump"]:
            self.yvec = 0
            
        if not self.inladder:
            hang = False
        
        if key["right"]:
            self.xvec += 2
        if key["left"]:
            self.xvec -= 2
            
        if self.xvec > 0:
            self.img = self.rimg
        elif self.xvec < 0:
            self.img = self.limg
        
        # check horizontal move
        if self.xvec != 0:
            self.rect = self.rect.move(self.xvec, 0)
            if self.xvec > 0:
                for i in range(self.xvec/2):
                    if self.is_collide(walltiles):
                        self.rect = self.rect.move(-2, 0)
                    else: break
            elif self.xvec < 0:
                for i in range(-self.xvec/2):
                    if self.is_collide(walltiles):
                        self.rect = self.rect.move(2, 0)
                    else: break
        
        # check vertical move
        # check moving down
        if self.yvec > 0:
            for i in range(self.yvec):
                if not self.is_onground(walltiles, cloudtiles, self.yvec):
                    self.rect = self.rect.move(0, 1)
                else: break
        # check moving up
        elif self.yvec < 0:
            for i in range(-self.yvec):
                if not self.is_collide(walltiles):
                    self.rect = self.rect.move(0, -1)
                else: 
                    self.yvec = 0 # cogne au plafond
                    self.rect = self.rect.move(0, 1)
                    break
        # check doors
        for d in doortiles:
            if pygame.sprite.collide_rect(self, d):
                return d
        return False
            
                