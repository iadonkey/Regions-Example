import pyads
import pygame
import random
import math

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

UNIT_RADIUS = 15  # not used for rectangle size anymore, can keep for collision
COLLISION_COLOR = (218, 119, 109)
BACKGROUND_COLOR = (71, 91, 120)
GRAY = (245, 241, 238)
WHITE = (255, 255, 255)

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Multi Region Demo")
clock = pygame.time.Clock()

# --- Unit class ---
class Unit:
    def __init__(self, color, start_pos, axis, path_range, unit_speed, width=30, height=30):
        self.base_color = color
        self.color = color
        self.pos = list(start_pos)
        self.axis = axis
        self.path_range = path_range
        self.direction = 1
        self.unit_speed = unit_speed
        self.width = width
        self.height = height

    def update(self, x):
        self.pos[0] = x

    def draw(self, surface):
        unit_rect = pygame.Rect(int(self.pos[0]), int(self.pos[1]), self.width, self.height)
        pygame.draw.rect(surface, self.color, unit_rect)
        pygame.draw.rect(surface, WHITE, unit_rect, 2)

def check_collision(unit1, unit2):
    rect1 = pygame.Rect(unit1.pos[0], unit1.pos[1], unit1.width, unit1.height)
    rect2 = pygame.Rect(unit2.pos[0], unit2.pos[1], unit2.width, unit2.height)
    return rect1.colliderect(rect2)



# --- Create 1 horizontal unit ---
horizontal_unit1 = Unit(color=(218, 119, 109), start_pos=(0, 150), axis='x', path_range=(0, SCREEN_WIDTH), unit_speed=2,
                       width=40, height=40)

# --- Create 2 horizontal unit ---
horizontal_unit2 = Unit(color=(218, 119, 109), start_pos=(0, 230), axis='x', path_range=(0, SCREEN_WIDTH), unit_speed=2,
                       width=40, height=40)

units = [horizontal_unit1] + [horizontal_unit2]

# --- Draw grid background ---
def draw_grid(surface, spacing=100):
    for x in range(0, SCREEN_WIDTH, spacing):
        pygame.draw.line(surface, GRAY, (x,0), (x,SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, spacing):
        pygame.draw.line(surface, GRAY, (0,y), (SCREEN_WIDTH,y))

def draw_transparent_rect(surface, p1x, p1y, p2x, p2y, color, alpha):
    """
    Draw a transparent rectangle on `surface` using two opposite corners.

    surface : pygame.Surface
    p1, p2  : (x, y) tuples (opposite corners)
    color   : (r, g, b)
    alpha   : 0..255
    """
    x = min(p1x, p2x)
    y = min(p1y, p2y)
    w = abs(p1x - p2x)
    h = abs(p1y - p2y)

    if w == 0 or h == 0:
        return  # nothing to draw

    rect_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rect_surf.fill((*color, alpha))
    surface.blit(rect_surf, (x, y))

# --- Main loop ---
running = True
with pyads.Connection("127.0.0.1.1.1", 851, "127.0.0.1.1.1") as plc:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        horizontal_unit1.update(plc.read_by_name(f"ZGlobal.Com.Unit.Handling1.Publish.Equipment.AxisX.Base.ActualPosition", pyads.PLCTYPE_LREAL))
        horizontal_unit2.update(plc.read_by_name(f"ZGlobal.Com.Unit.Handling2.Publish.Equipment.AxisX.Base.ActualPosition", pyads.PLCTYPE_LREAL))
                
        # collision checks
        for i in range(len(units)):
            for j in range(i+1, len(units)):
                if check_collision(units[i], units[j]):
                    units[i].color = COLLISION_COLOR
                    units[j].color = COLLISION_COLOR
                else:
                    units[i].color = units[i].base_color
                    units[j].color = units[j].base_color    

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        
        for i in range(1, 4):
            print(f"ZGlobal.Com.SharedContext.Publish.Region{i}.Corner1.X")
            draw_transparent_rect(screen,
                plc.read_by_name(f"ZGlobal.Com.SharedContext.Publish.Region{i}.Corner1.X", pyads.PLCTYPE_LREAL),
                100,
                plc.read_by_name(f"ZGlobal.Com.SharedContext.Publish.Region{i}.Corner2.X", pyads.PLCTYPE_LREAL),
                300,
                                  
                (0, 255, 0), 120)        

        # Draw units
        for u in units:
            u.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
