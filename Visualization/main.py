import pyads
import pygame
import random
import math

# --- Configuration ---
SCREEN_WIDTH = 850
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
font = pygame.font.Font(None, 30)

# --- Unit class ---
class Unit:
    def __init__(self, name, color, start_pos, axis, path_range, unit_speed, width=30, height=30):
        self.base_color = color
        self.color = color
        self.pos = list(start_pos)
        self.axis = axis
        self.path_range = path_range
        self.direction = 1
        self.unit_speed = unit_speed
        self.width = width
        self.height = height
        self.text_surface = font.render(name, True, (255,255,255))

    def update(self, x):
        self.pos[0] = x

    def draw(self, surface):
        unit_rect = pygame.Rect(int(self.pos[0] - self.width * 0.5), int(self.pos[1] - self.height * 0.5), self.width, self.height)
        
        pygame.draw.rect(surface, self.color, unit_rect)
        pygame.draw.rect(surface, WHITE, unit_rect, 2)
        
        text_rect = self.text_surface.get_rect(center=self.pos)
        surface.blit(self.text_surface, text_rect)
        

def check_collision(unit1, unit2):
    rect1 = pygame.Rect(unit1.pos[0], unit1.pos[1], unit1.width, unit1.height)
    rect2 = pygame.Rect(unit2.pos[0], unit2.pos[1], unit2.width, unit2.height)
    return rect1.colliderect(rect2)



units = []
for i in range(4):
    unit = Unit(f"{i+1}", color=(218, 119, 109), start_pos=(0, 130 + (45*i)), 
                       axis='x', path_range=(0, SCREEN_WIDTH), unit_speed=2,
                       width=50, height=40)
    units.append(unit)

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
    
        for i, unit in enumerate(units):
            unit.update(plc.read_by_name(f"ZGlobal.Com.Unit.Handling{i+1}.Publish.Equipment.AxisX.Base.ActualPosition", pyads.PLCTYPE_LREAL))
            
            for j in range(i+1, len(units)):
                if check_collision(units[i], units[j]):
                    units[i].color = COLLISION_COLOR
                    units[j].color = COLLISION_COLOR
                else:
                    units[i].color = units[i].base_color
                    units[j].color = units[j].base_color
       

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        for i in range(1, 8):
            color = (255, 0, 0) if plc.read_by_name(f"ZGlobal.Com.SharedContext.Publish.Region{i}.IsLocked", pyads.PLCTYPE_BOOL) else (0, 255, 0)
            draw_transparent_rect(screen,
                plc.read_by_name(f"ZGlobal.Com.SharedContext.Publish.Region{i}.Corner1.X", pyads.PLCTYPE_LREAL),
                100,
                plc.read_by_name(f"ZGlobal.Com.SharedContext.Publish.Region{i}.Corner2.X", pyads.PLCTYPE_LREAL),
                300,               
                color, 120)
            
        for i in range(len(units)):                   
            target_position = plc.read_by_name(f"ZGlobal.Com.Unit.Handling{i+1}.Publish.TargetPosition", pyads.PLCTYPE_LREAL)
            pygame.draw.line(screen, GRAY, units[i].pos, (target_position, units[i].pos[1]), 2)            
            
            

        # Draw units
        for u in units:
            u.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
