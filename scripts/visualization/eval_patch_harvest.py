import pygame
import sys 
import math
import time
import os


class Agent:
    def __init__(self, x, y, facing):
        self.row_idx = y
        self.col_idx = x
        self.facing = facing
        self.score = 0
    
    def move(self):
        if self.facing == 0:   # Northwest
            self.col_idx -= 1
            self.row_idx -= 1
        elif self.facing == 1: # North
            self.row_idx -= 1
        elif self.facing == 2: # Northeast
            self.col_idx += 1
            self.row_idx -= 1
        elif self.facing == 3: # East
            self.col_idx += 1
        elif self.facing == 4: # Southeast
            self.col_idx += 1
            self.row_idx += 1
        elif self.facing == 5: # South
            self.row_idx += 1
        elif self.facing == 6: # Southwest
            self.col_idx -= 1
            self.row_idx += 1
        elif self.facing == 7: # West
            self.col_idx -= 1
    
    def move_back(self):
        if self.facing == 0:   # Northwest
            self.col_idx += 1
            self.row_idx += 1
        elif self.facing == 1: # North
            self.row_idx += 1
        elif self.facing == 2: # Northeast
            self.col_idx -= 1
            self.row_idx += 1
        elif self.facing == 3: # East
            self.col_idx -= 1
        elif self.facing == 4: # Southeast
            self.col_idx -= 1
            self.row_idx -= 1
        elif self.facing == 5: # South
            self.row_idx -= 1
        elif self.facing == 6: # Southwest
            self.col_idx += 1
            self.row_idx -= 1
        elif self.facing == 7: # West
            self.col_idx += 1

    def rotate_right(self):
        self.facing += 1
        self.facing = self.facing % 8

    def rotate_left(self):
        self.facing -= 1
        if self.facing < 0:
            self.facing += 8


class PatchHarvestAnimator:
    def __init__(self, map_filename, flip_y = False):
        self.map_filename = map_filename
        self.metadata = {}
        self.load_map()
        self.validate_metadata()
        self.setup_color_map()
        #self.agent = Agent(self.get_map_width() // 2, self.get_map_height() // 2, 1)
        #self.agent = Agent(34, 25, 3)
        if flip_y: 
            start_y = int(self.metadata['height']) - int(self.metadata['start_y']) - 1
        else:
            start_y = int(self.metadata['start_y'])
        self.agent = Agent(
                int(self.metadata['start_x']),
                start_y,
                int(self.metadata['start_facing']))
        self.start_pos = (int(self.metadata['start_x']), start_y)
        self.consume()
        self.trace_points = []
        self.add_trace()

    def read_metadata(self, s):
        print('metadata:', s)
        s = s[1:] # Remove leading $
        line_parts = s.split('=')
        self.metadata[line_parts[0].strip()] = line_parts[1].strip()
    
    def validate_metadata(self):
        if 'start_facing' not in self.metadata:
            print('Error! Map\'s metadata must include "start_facing"')
            exit()
        if 'start_x' not in self.metadata:
            print('Error! Map\'s metadata must include "start_x"')
            exit()
        if 'start_y' not in self.metadata:
            print('Error! Map\'s metadata must include "start_y"')
            exit()
        if 'width' not in self.metadata:
            print('Error! Map\'s metadata must include "width"')
            exit()
        if 'height' not in self.metadata:
            print('Error! Map\'s metadata must include "height"')
            exit()

    def load_map(self):
        self.map_data = []
        with open(map_filename, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line[0] == '$':
                    self.read_metadata(line)
                    continue
                tiles = []
                for c in line: 
                    tiles.append(c)
                self.map_data.append(tiles) 
                
    def setup_color_map(self):
        self.color_map = {}
        self.color_map['o'] = (100,100,100)
        self.color_map['E'] = (200,200,0)
        self.color_map['N'] = (0,150,200)
        self.color_map['.'] = (150,150,150)
        self.color_map['O'] = (200,50,0)
        self.color_map['L'] = (0,50,200)
        self.color_map['+'] = (255,255,255)
        self.color_map['X'] = (50,200,50)
        self.color_map['R'] = (200,200,0)
    
    def get_map_width(self):
        return len(self.map_data[0])

    def get_map_height(self):
        return len(self.map_data)

    def get_color(self, row_idx, col_idx):
        return self.color_map[self.map_data[row_idx][col_idx]]

    def consume(self):
        if self.map_data[self.agent.row_idx][self.agent.col_idx] in ('N', 'E'):
            self.agent.score += 1
            self.map_data[self.agent.row_idx][self.agent.col_idx] = '.'
            print('Score:', self.agent.score)

    def add_trace(self):
        self.trace_points.append((self.agent.col_idx, self.agent.row_idx))

    def move(self):
        self.agent.move()
        #self.agent.row_idx = max(min(self.agent.row_idx, self.get_map_height() - 1), 0)
        #self.agent.col_idx = max(min(self.agent.col_idx, self.get_map_width() - 1), 0)
        self.agent.row_idx = self.agent.row_idx % self.get_map_height()
        self.agent.col_idx = self.agent.col_idx % self.get_map_width()
        self.consume()
        self.add_trace()
    
    def move_back(self):
        self.agent.move_back()
        #self.agent.row_idx = max(min(self.agent.row_idx, self.get_map_height() - 1), 0)
        #self.agent.col_idx = max(min(self.agent.col_idx, self.get_map_width() - 1), 0)
        self.agent.row_idx = self.agent.row_idx % self.get_map_height()
        self.agent.col_idx = self.agent.col_idx % self.get_map_width()
        self.consume()
        self.add_trace()

    def rotate_right(self): 
        self.agent.rotate_right()
    
    def rotate_left(self): 
        self.agent.rotate_left()

    def render(self, screen):
        tile_width = screen.get_width() // self.get_map_width()
        tile_height = screen.get_height() // self.get_map_height()
        # Draw map
        for row_idx in range(self.get_map_height()):
            for col_idx in range(self.get_map_width()):
                col = self.get_color(row_idx, col_idx)
                pygame.draw.rect(screen, col,\
                        (col_idx * tile_width, row_idx * tile_height, \
                            tile_width, tile_height))
                #pygame.draw.rect(screen, col, \
                #        (col_idx * tile_width + 1, row_idx * tile_height + 1, \
                #            tile_width - 1, tile_height - 1))
        # Draw start position
        pygame.draw.circle(screen, (200,0,0), \
                ((self.start_pos[0] + 0.5) * tile_width, \
                    (self.start_pos[1] + 0.5) * tile_height), \
                3 * tile_width / 8)
        # Draw trace
        for i in range(1, len(self.trace_points)):
            x1, y1 = self.trace_points[i]
            x2, y2 = self.trace_points[i-1]
            x1 += 0.5
            y1 += 0.5
            x2 += 0.5
            y2 += 0.5
            color = (50 + (200 * i / len(self.trace_points)), 0, 0)
            if abs(x2 - x1) <= 1 and abs(y2 - y1) <= 1:
                pygame.draw.line(screen, color,
                        (x1 * tile_width, y1 * tile_height), 
                        (x2 * tile_width, y2 * tile_height), 
                        3)
        # Draw agent
        surf = pygame.Surface((tile_width, tile_height))
        surf.set_colorkey((0,0,0))
        pygame.draw.polygon(surf, (255,0,0), (\
                (tile_width / 2 + math.cos(math.pi * 0.75) * tile_width / 2, 
                    tile_height / 2 - math.sin(math.pi * 0.75) * tile_height / 2), 
                (tile_width / 2 + math.cos(math.pi * 1.5) * tile_width / 2, 
                    tile_height / 2 - math.sin(math.pi * 1.5) * tile_height / 2), 
                (tile_width, tile_height / 2)))
        surf = pygame.transform.rotate(surf, -45 * self.agent.facing)
        offset = 0
        if self.agent.facing % 2 == 1:
            offset = (math.sqrt(tile_width ** 2 + tile_height ** 2) - tile_width) / 2
        screen.blit(surf, \
                (self.agent.col_idx * tile_width - offset,\
                self.agent.row_idx * tile_height - offset))
              



def load_movement_file(filename):
    output_str = ''
    with open(filename, 'r') as fp:
        for line in fp:
            line = line.strip()
            if len(line) == 0:
                continue
            line_parts = line.split()
            if len(line_parts) < 2:
                continue
            if line_parts[1] == 'move':
                output_str += 'M'
            elif line_parts[1] == 'rot_right':
                output_str += 'R'
            elif line_parts[1] == 'rot_left':
                output_str += 'L'
    return output_str

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error! Expects at least one command line arg: the map filename!')
        exit()

    map_filename = sys.argv[1]
    movement_str = None
    if len(sys.argv) > 2:
        #movement_str = load_movement_file(sys.argv[2])
        movement_str = sys.argv[2]
    
    flip_map = False
    if '-f' in sys.argv:
        flip_map = True
        sys.argv.remove('-f')
    
    output_filename = None
    if len(sys.argv) > 3:
        output_filename = sys.argv[3]

    gif_dir = None
    if len(sys.argv) > 4:
        gif_dir = sys.argv[4]
        if not os.path.isdir(gif_dir):
            os.mkdir(gif_dir)


    animator = PatchHarvestAnimator(map_filename, flip_map)

    screen_width = 800
    screen_height = 800

    pygame.init()
    if output_filename is not None:
        screen = pygame.Surface((screen_width, screen_height))
    else:
        screen = pygame.display.set_mode((screen_width, screen_height))

    def process_move(idx):
        if idx < len(movement_str):
            if movement_str[idx] == 'R':
                animator.rotate_right()
            elif movement_str[idx] == 'L':
                animator.rotate_left()
            elif movement_str[idx] == 'M':
                animator.move()
            elif movement_str[idx] == 'B':
                animator.move_back()
    move_idx = 0
    playing = False
    time_delay = 0.01 
    done = False

    # Trace, output, and stop if needed
    if output_filename is not None:
        while move_idx < len(movement_str):
            process_move(move_idx)
            animator.render(screen)
            if gif_dir is not None:
                frame_filename = gif_dir + '/frame_' + str(move_idx).zfill(5) + '.png'
                pygame.image.save(screen, frame_filename)
            move_idx += 1
        pygame.image.save(screen, output_filename)
        print('Image saved to:', output_filename)
        pygame.quit()
        exit()

    while not done:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                done = True
            elif evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_ESCAPE or evt.key == pygame.K_q:
                    done = True
                elif evt.key == pygame.K_RIGHT:
                    animator.rotate_right()
                elif evt.key == pygame.K_LEFT:
                    animator.rotate_left()
                elif evt.key == pygame.K_UP:
                    animator.move()
                elif evt.key == pygame.K_SPACE and movement_str is not None:
                    process_move(move_idx)
                    move_idx += 1
                elif evt.key == pygame.K_p:
                    playing = not playing
        if playing:
            time.sleep(time_delay)
            process_move(move_idx)
            move_idx += 1
            print(animator.agent.col_idx, animator.agent.row_idx, animator.agent.facing)

        animator.render(screen)
        pygame.display.flip()

    pygame.quit()
