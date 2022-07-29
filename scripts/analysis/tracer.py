import pygame
import sys

class AvidaTracer:
    def __init__(self, w, h, is_fullscreen, font_name, font_size, font_color = (255,255,255)):
        self.screen_width = w
        self.screen_height = h
        self.is_fullscreen = is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height),
                    pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_color = font_color
        self.org_idx = 0
        self.org_step = 0

    def run(self):
        self.is_running = True
        self.is_paused = True
        while self.is_running:
            self.update()
            self.render()
            self.clock.tick(60)

    def update(self):
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                self.is_running = False
            elif evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_ESCAPE or evt.key == pygame.K_q:
                    self.is_running = False
                elif evt.key == pygame.K_RIGHT or evt.key == pygame.K_d:
                    self.org_step += 1
                    if self.org_step >= len(self.org_states[self.org_idx]):
                        self.org_step = 0
                elif evt.key == pygame.K_LEFT or evt.key == pygame.K_a:
                    self.org_step -= 1
                    if self.org_step < 0:
                        self.org_step = len(self.org_states[self.org_idx]) - 1
                elif evt.key == pygame.K_UP or evt.key == pygame.K_w:
                    self.org_idx -= 1
                    if self.org_idx < 0:
                        self.org_idx = len(self.org_states) - 1 
                    self.org_step = 0
                elif evt.key == pygame.K_DOWN or evt.key == pygame.K_s:
                    self.org_idx += 1
                    if self.org_idx >= len(self.org_states):
                        self.org_idx = 0
                    self.org_step = 0
                elif evt.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused
        if not self.is_paused:
            self.org_step += 1
            if self.org_step >= len(self.org_states[self.org_idx]):
                self.org_step = 0


    def render(self):
        self.screen.fill((0,0,0))

        self.genome.render(self.screen, self.org_states[self.org_idx][self.org_step])
        
        x = 50
        y = 300
        org_idx_surf = self.font.render('Org idx: ' + str(self.org_idx), 
                True, self.font_color)
        self.screen.blit(org_idx_surf, (x, y))
        y += 30
        org_step_surf = self.font.render('Org step: ' + str(self.org_step), 
                True, self.font_color)
        self.screen.blit(org_step_surf, (x, y))
        y += 60

        x,y = self.render_heads(x, y)
        y += 30
        x,y = self.render_registers(x, y)

        pygame.display.flip()

    def render_heads(self, x, y):
        state = self.org_states[self.org_idx][self.org_step]
        for head in ('IP', 'RH', 'WH', 'FH'):
            surf = self.font.render(head + ': ' + str(state.heads[head]), 
                    True, self.font_color)
            self.screen.blit(surf, (x, y))
            y += 30
        return (x, y)
    
    def render_registers(self, x, y):
        state = self.org_states[self.org_idx][self.org_step]
        for idx in range(len(state.regs)):
            surf = self.font.render('Reg ' + str(idx) + ': ' + str(state.regs[idx]), 
                    True, self.font_color)
            self.screen.blit(surf, (x, y))
            y += 30
        return (x, y)

    
    def set_genome(self, filename, font, x, y, dx, dy, w, h, angle):
        inst_list = []
        with open(filename, 'r') as fp:
            for line in fp:
                line = line.strip()
                if line != '': 
                    inst_list.append(line)
        self.genome = Genome(inst_list, font, x, y, dx, dy, w, h, angle)

    def parse_mabe_trace(self, filename):
        self.org_states = []
        org_idx = None
        heads = {}
        regs = []
        with open(filename, 'r') as fp:
            for line in fp:
                line = line.strip()
                if len(line) == 0: # Ignore empty lines
                    continue
                line_parts = line.split()
                # Lines that start with [X], where X is a number
                if line_parts[0][0] == '[' and line_parts[0][-1] == ']' \
                        and line_parts[0][1:-1].isnumeric():
                    # Org index line
                    if len(line_parts) == 1:
                        # If we have existing data, save it!
                        if org_idx is not None:
                            while len(self.org_states) <= org_idx:
                                self.org_states.append([])
                            self.org_states[org_idx].append(OrgState(org_idx, heads, regs))
                        # Reset org
                        org_idx = int(line_parts[0][1:-1])
                        heads = {}
                        regs = []
                    # Register line
                    else: 
                        reg_idx = int(line_parts[0][1:-1])
                        while len(regs) <= reg_idx:
                            regs.append(0)
                        regs[reg_idx] = int(line_parts[1]) 
                # Heads line
                elif line_parts[0] == 'IP:':
                    idx = 0
                    while True:
                        if line_parts[idx][-1] == ':' and line_parts[idx][0] != '(' and \
                                idx < len(line_parts) - 1:
                            head_name = line_parts[idx][:-1]
                            head_value = line_parts[idx + 1]
                            # Account for old style (lacks a space)
                            if '(' in head_value:
                                char_idx = head_value.find('(')
                                head_value = head_value[:char_idx]
                            heads[head_name] = int(head_value)
                            idx += 2
                        else:
                            break

            # Save the final org! 
            if org_idx is not None:
                while len(self.org_states) <= org_idx:
                    self.org_states.append([])
                self.org_states[org_idx].append(OrgState(org_idx, heads, regs))
    
    def parse_avida_trace(self, filename):
        self.org_states = []
        org_idx = None
        heads = {}
        regs = []
        with open(filename, 'r') as fp:
            for line in fp:
                line = line.strip()
                if len(line) == 0: # Ignore empty lines
                    continue
                line_parts = line.split()

                # New org line
                if len(line_parts) == 1 and line_parts[0] == 'U:-1':
                    # If we have existing data, save it!
                    if org_idx is not None:
                        while len(self.org_states) <= org_idx:
                            self.org_states.append([])
                        self.org_states[org_idx].append(OrgState(org_idx, heads, regs))
                    # Reset org
                    org_idx = 0
                    heads = {}
                    regs = []
                # CPU line
                if line_parts[0] == 'CPU':
                    for line_part in line_parts:
                        # Instruction pointer
                        if len(line_part) > 3 and line_part[:3] == 'IP:':
                            heads['IP'] = int(line_part[3:])
                        # Registers
                        elif len(line_part) > 3 and line_part[1:3] == 'X:':
                            reg_char = line_part[0]
                            reg_idx = ord(reg_char) - ord('A')
                            reg_val = int(line_part[3:])
                            while len(regs) <= reg_idx:
                                regs.append(0)
                            regs[reg_idx] = reg_val 
                # Heads line
                elif line_parts[0][:7] == 'R-Head:':
                    idx = 0
                    for line_part in line_parts:
                        if len(line_part) >= 8:
                            if line_part[:6] == 'R-Head':
                                heads['RH'] = int(line_part[7:])
                            elif line_part[:6] == 'W-Head':
                                heads['WH'] = int(line_part[7:])
                            elif line_part[:6] == 'F-Head':
                                heads['FH'] = int(line_part[7:])

            # Save the final org! 
            if org_idx is not None:
                while len(self.org_states) <= org_idx:
                    self.org_states.append([])
                self.org_states[org_idx].append(OrgState(org_idx, heads, regs))
    
    def compare_org_trace(self, other, org_idx):
        for step in range(len(self.org_states[org_idx])):
            if step >= len(other.org_states[org_idx]):
                print('Reached end of steps in other trace at step:', step)
                return step
            self_state = self.org_states[org_idx][step]
            other_state = other.org_states[org_idx][step]
            for reg_idx in range(6):#range(len(self.org_states[org_idx][step])):
                if self_state.regs[reg_idx] != other_state.regs[reg_idx]:
                    print('Mismatch in register', reg_idx, 'at step:', step)
                    return step
            for head_name in self_state.heads.keys():
                if head_name not in other_state.heads.keys():
                    print('Head', head_name, 'missing in second trace at step:', step)
                    return step
                if self_state.heads[head_name] != other_state.heads[head_name]:
                    print('Mismatch in head', head_name, 'at step:', step)
                    return step
        print('No differences found!')



class Genome:
    def __init__(self, inst_list, font, x, y, dx, dy, w, h, angle):
        self.inst_list = inst_list
        self.font = font
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.inst_width = w
        self.inst_height = h
        self.angle = angle

    def render(self, surf, state): 
        x = self.x 
        y = self.y
        idx = 0
        for inst in self.inst_list:
            inst_str = str(idx) + '. ' + inst
            if idx >= 0 and idx < 10: 
                inst_str = '0' + inst_str
            inst_surf = self.font.render(inst_str, True, (255,255,255))
            inst_surf = pygame.transform.rotate(inst_surf, self.angle)
            inst_rect = inst_surf.get_rect()
            inst_rect.bottomleft = (x,y)
            surf.blit(inst_surf, inst_rect)
            x += self.dx
            y += self.dy
            idx += 1
        pygame.draw.circle(surf, (250,50,0), 
                (self.x + self.dx * (state.heads['IP'] + 0.5), self.y + 5), 5)

class OrgState:
    def __init__(self, idx, heads, regs):
        self.idx = idx
        self.heads = heads
        self.regs = regs


def print_help():
    print('')
    print('First argument must be the filename of the organism\'s genome.')
    print('  Each line of the file should contain the name of one instruction')
    print('  Character string genomes not currently supported.')
    print('')
    print('Other possible arguments:')
    print('  -a FILENAME or --avida FILENAME : Load an organism trace output from Avida2')
    print('  -m FILENAME or --mabe FILENAME  : Load an organism trace output from MABE2')
    print('  -t INDEX or --trace INDEX: Run an interactive visualization of a trace that has been loaded')
    print('  -c INDEX INDEX or --compare INDEX INDEX : Compare two traces that have been loaded')
    print('  -h or --help : Show this help message')
    print('')
    print('Note: indices start at 0.')



if __name__ == '__main__':
    pygame.init()
    is_fullscreen = False

    if len(sys.argv) < 2:
        print('Expects at least one command line argument: the organism\'s genome')
        print('Pass -h or --help for more information')
        exit()
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print_help()
        exit()
    genome_filename = sys.argv[1]

    tracer_list = []
    inst_font = pygame.font.SysFont('arial', 13)

    arg_idx = 2
    while arg_idx < len(sys.argv):
        print('[' + str(arg_idx) + ']', sys.argv[arg_idx])
        if sys.argv[arg_idx] == '-a' or sys.argv[arg_idx] == '--avida':
            if arg_idx == len(sys.argv) - 1:
                print('Error! You must pass the Avida organism\'s trace filename after -a!')
                exit()
            trace_filename = sys.argv[arg_idx + 1]
            tracer = AvidaTracer(1920, 1080, is_fullscreen, 'arial', 24)
            tracer.set_genome(genome_filename, inst_font, 0, 200, 14, 0, 200, 14, 90)
            tracer.parse_avida_trace(trace_filename)
            tracer_list.append(tracer)
            arg_idx += 1
            print('Loaded Avida trace as tracer #' + 
                    str(len(tracer_list) - 1) + ': ' + trace_filename)
        elif sys.argv[arg_idx] == '-m' or sys.argv[arg_idx] == '--mabe':
            if arg_idx == len(sys.argv) - 1:
                print('Error! You must pass the MABE2 organism\'s trace filename after -m!')
                exit()
            trace_filename = sys.argv[arg_idx + 1]
            tracer = AvidaTracer(1920, 1080, is_fullscreen, 'arial', 24)
            tracer.set_genome(genome_filename, inst_font, 0, 200, 14, 0, 200, 14, 90)
            tracer.parse_mabe_trace(trace_filename)
            tracer_list.append(tracer)
            arg_idx += 1
            print('Loaded MABE2 trace as tracer #' + 
                    str(len(tracer_list) - 1) + ': ' + trace_filename)
        elif sys.argv[arg_idx] == '-t' or sys.argv[arg_idx] == '--trace':
            if arg_idx == len(sys.argv) - 1:
                print('Error! You must pass tracer index after -m!')
                exit()
            tracer_idx = int(sys.argv[arg_idx + 1])
            if tracer_idx >= len(tracer_list):
                print('Invalid tracer index! We only know of', len(tracer_list), '(indices start at 0)')
                print('You passed:', tracer_idx)
                exit()
            tracer_list[tracer_idx].run()
            arg_idx += 1
        elif sys.argv[arg_idx] == '-c' or sys.argv[arg_idx] == '--compare':
            if arg_idx >= len(sys.argv) - 2:
                print('Error! You must pass two tracer indices after -c!')
                exit()
            a_idx = int(sys.argv[arg_idx + 1])
            b_idx = int(sys.argv[arg_idx + 2])
            if a_idx >= len(tracer_list) or b_idx >= len(tracer_list):
                print('Invalid tracer index! We only know of', len(tracer_list), '(indices start at 0)')
                print('You passed:', a_idx, 'and', b_idx)
                exit()
            tracer_list[a_idx].compare_org_trace(tracer_list[b_idx], 0)
            arg_idx += 2
        elif sys.argv[arg_idx] == '-h' or sys.argv[arg_idx] == '--help':
            print_help()
            exit()
        else:
            print('Error! Unknown argument:', sys.argv[arg_idx])
            print('Run with -h or --help to see possible args')
            exit()

        arg_idx += 1
