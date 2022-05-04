import pygame
import os
import random

# window proportions
WIN_HEIGHT = 800
WIN_WIDTH = 500

# dragon model when flapping
DRAKE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("img", "dragon_up.png")), (120, 100)), # load image and scale it to 100x80
    pygame.transform.scale(pygame.image.load(os.path.join("img", "dragon_base.png")), (120, 100)),
    pygame.transform.scale(pygame.image.load(os.path.join("img", "dragon_down.png")), (120, 100))]

# world models
GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "ground.png")))
SKY_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "sky.png")))
BG_IMG = pygame.image.load(os.path.join("img", "bg.png"))
    

class Drake:
    IMGS = DRAKE_IMGS 
    MAX_ROTATION = 25 # max rotation up in degrees
    ROT_VEL = 20 # rotation velocity
    ANIMATION_TIME = 5 # frames for 1 flap animation
    
    # initialize dragon
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0 # current rotation in degrees
        self.tick_count = 0 # frames counter
        self.vel = 0 # velocity of movement
        self.height = self.y
        self.img_count = 0 # tracking flap animation
        self.img = self.IMGS[0] # current image
        
    # flap dragon method 
    def flap(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
        
    # move dragon method
    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2 # move based on velocity
        
        # not moving down too fast
        if d >= 16:
            d = 16
            
        # move up faster
        if d < 0:
            d -= 2
            
        self.y += d
        
        # set rotation when moving up
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION         
        else: # set rotation when moving down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
                
    # draw flapping dragon method
    def draw(self, win):
        self.img_count += 1
        
        # check what img to draw based on counter
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # not flaping when moving down
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
            
        rotated_img = pygame.transform.rotate(self.img, self.tilt) # rotate image around center
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)
        
    # dragon collisions method
    def get_mask(self):
        return pygame.mask.from_surface(self.img) # make two dimensional list from not transparent pixels of dragon in the box

    
class Base:
    VEL = 5 # velocity of base movement
    
    # initialize base
    def __init__(self, y):
        self.y = y
        self.x1 = 0 # starting position of 1st image
        
    # move base method 
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        # checking if 1st img is passed the screen
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH # drawing it at the end
        
        # ckecking if 2nd img is passed the screen  
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH # drawing it at the end 
     
    # draw base method
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
          

class Background(Base):
    WIDTH = BG_IMG.get_width()
    IMG = BG_IMG
    
    # initialize background
    def __init__(self):
        self.y = 0
        self.x1 = 0 # starting position of 1st image
        self.x2 = self.WIDTH # starting position of 2nd image
        
    # inherit move method
    def move(self):
        return super().move()
    
    # inherit draw method
    def draw(self, win):
        return super().draw(win)
             
            
class Ground(Base):  
    WIDTH = GROUND_IMG.get_width()
    IMG = GROUND_IMG

    # inherit initialization and add starting position of 2nd image
    def __init__(self, y):
        super().__init__(y)
        self.x2 = self.WIDTH # starting position of 2nd image

    # inherit move method
    def move(self):
        return super().move()
    
    # inherit draw method
    def draw(self, win):
        return super().draw(win)
    
    
class Sky(Base):
    WIDTH = SKY_IMG.get_width()
    IMG = SKY_IMG
    
    # inherit initialization and add starting position of 2nd image
    def __init__(self, y):
        super().__init__(y)
        self.x2 = self.WIDTH # starting position of 2nd image
    
    # inherit move method
    def move(self):
        return super().move()
    
    # inherit draw method
    def draw(self, win):
        return super().draw(win)
    
    
# initialize window with background and dragon on top of it
def draw_window(win, background, drake, ground, sky):
        background.draw(win) # background
        ground.draw(win) # bottom of the screen
        sky.draw(win) # top of the screen
        drake.draw(win) # dragon
        pygame.display.update()    
    
    
# main function
def main():
    drake = Drake(150, 350) # create Drake object
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # create window object
    background = Background()
    ground = Ground(WIN_HEIGHT - 4)
    sky = Sky(0)
    clock = pygame.time.Clock() # create clock to measure time
    
    score = 0
    
    # running game loop
    run = True
    while run:
        clock.tick(30) # refresh time
        for event in pygame.event.get():
            # exit game by clicking X
            if event.type == pygame.QUIT:
                run = False
         
        # drake.move()
        background.move()
        ground.move()
        sky.move()
        draw_window(win, background, drake, ground, sky) # refresh window
        
    pygame.quit()
    quit()


# run main function
main()