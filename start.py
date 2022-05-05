import pygame
import os
import neat
import random
pygame.font.init() # initialize fonts

# window proportions
WIN_HEIGHT = 800
WIN_WIDTH = 500

# dragon model when flapping
DRAKE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("img", "dragon_up.png")), (120, 100)), # load dragon images and scale them to 120x100
    pygame.transform.scale(pygame.image.load(os.path.join("img", "dragon_base.png")), (120, 100)),
    pygame.transform.scale(pygame.image.load(os.path.join("img", "dragon_down.png")), (120, 100))]

# world models
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")))
GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "ground.png")))
SKY_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "sky.png")))
BG_IMG = pygame.image.load(os.path.join("img", "bg.png"))

# fonts
SCORE_FONT = pygame.font.SysFont("agencyfb", 60) # 60px font for score
END_SCORE_FONT = pygame.font.SysFont("agencyfb", 100) # 200px font for end of game text

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

    
class Pipe:
    GAP = 200 # space between pipes
    VEL = 5 # velocity of movement towards dragon    
    
    # initialize pipe
    def __init__(self, x):
        self.x = x
        self.height = 0
        
        self.top = 0 # start of top pipe 
        self.bottom = 0 # start of bottom pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # top pipe img is flipped 180deg
        self.PIPE_BOTTOM = PIPE_IMG # bottom pipe is same as image
        
        self.passed = False # have this pipe been passed by dragon
        self.set_height() 
        
    #  randomly placing pipes method
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height() # top pipe position
        self.bottom = self.height + self.GAP # bottom pipe position
        
    # move pipes method
    def move(self):
        self.x -= self.VEL
        
    # draw pipes method
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top)) 
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
    # collision checking method
    def collide(self, drake):
        drake_mask = drake.get_mask() # getting mask from dragon 
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) # getting mask from top pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # getting mask from bottom pipe
        
        top_offset = (self.x - drake.x, self.top - round(drake.y)) # space between top pipe and dragon
        bottom_offset = (self.x - drake.x, self.bottom - round(drake.y)) # space between bottom pipe and dragon
        
        top_collision = drake_mask.overlap(top_mask, top_offset) # check if pixels of drake overlaps pixels of top pipe
        bottom_collision = drake_mask.overlap(bottom_mask, bottom_offset) # check if pixels of drake overlaps pixels of bottom pipe
        
        # checking if one of collisions is not None
        if top_collision or bottom_collision:
            return True
        else:
            return False
    
    
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
def draw_window(win, background, drake, pipes, ground, sky, score, end):
    background.draw(win) # background
    ground.draw(win) # bottom of the screen
    sky.draw(win) # top of the screen
        
    # pipes
    for pipe in pipes:
        pipe.draw(win)
        
    text = SCORE_FONT.render(str(score), True, (255, 255, 255)) # score, white text
    win.blit(text, (WIN_WIDTH - 15 - text.get_width(), 10))  # 10 from top, 15 + text_width from right
    
    if end:
        end_text = SCORE_FONT.render("Story ends here", True, (255, 255, 255)) # the end text
        win.blit(end_text, (WIN_WIDTH / 2 - end_text.get_width() / 2, WIN_HEIGHT / 2 - end_text.get_height())) # centered text
    else:
        drake.draw(win) # dragon
        
    pygame.display.update()      
    
    
# main function
def main():
    drake = Drake(150, 350) # create Drake object
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # create window object
    background = Background()
    pipes = [Pipe(800)]
    ground = Ground(WIN_HEIGHT - 4)
    sky = Sky(0)
    clock = pygame.time.Clock() # create clock to measure time
    
    score = 0
    end = False
    
    # running game loop
    run = True
    while run:
        clock.tick(30) # refresh time
        for event in pygame.event.get():
            # exit game by clicking X
            if event.type == pygame.QUIT:
                run = False
        
        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            # chckeing if pipe collided with dragon
            if pipe.collide(drake):
                end = True       
            
            #checking if pipe left the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)
            
            # checking if dragon passed pipe
            if not pipe.passed and pipe.x < drake.x:
                pipe.passed = True
                add_pipe = True # draw new pipe
    
            pipe.move()
            
        # checking if new pipe should be added
        if add_pipe and not end:
            score += 1
            pipes.append(Pipe(600))
            
        # remove passed pipes
        for rem in remove_pipes:
            pipes.remove(rem)
        
        # check if dragon hit bottom or top of the screen
        if drake.y + drake.img.get_height() > ground.y or drake.y - drake.img.get_height() < sky.y:
            end = True 
            
        background.move()
        ground.move()
        sky.move()
        draw_window(win, background, drake, pipes, ground, sky, score, end) # refresh window
        
    pygame.quit()
    quit()


# run main function
main()