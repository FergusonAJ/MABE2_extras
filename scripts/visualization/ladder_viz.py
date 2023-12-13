import pygame

class LadderViz:
    def __init__(self):
        self.x_step = 10 
        self.y_step = 10

    def set_genome(self, genome):
        self.genome = genome
    
    def set_trace(self, trace_list):
        self.trace = trace_list

    def calculate_backtracks(self):
        backtracks = 0
        for i in range(1, len(self.trace)):
            if self.trace[i] <= self.trace[i-1]:
                backtracks += 1
        return backtracks

    def render(self):
        pygame.init()
        self.screen_width = len(self.genome) * self.x_step
        backtracks = self.calculate_backtracks()
        self.screen_height = backtracks * self.y_step
        self.screen = pygame.Surface((self.screen_width, self.screen_height))
        self.screen.fill((255,255,255))
        print('Image will be: '  + str(self.screen_width) + 'x' + str(self.screen_height))
        trace_idx = 0
        cur_idx = self.trace[trace_idx]
        y_idx = 0
        node_color = (50,50,50)
        alt_bg_color = (200,200,200)
        while True:
            pygame.draw.circle(self.screen, node_color, \
                    (int((cur_idx+0.5) * self.x_step), \
                        int((y_idx+0.5) * self.y_step)), 
                    self.x_step//2 - 1)
            old_idx = cur_idx
            trace_idx += 1
            if trace_idx >= len(self.trace):
                break
            cur_idx = self.trace[trace_idx]
            diff = cur_idx - old_idx
            if diff < 0:
                y_idx += 1
                if y_idx % 2 == 1:
                    pygame.draw.rect(self.screen, alt_bg_color, \
                            (0, self.y_step * (y_idx), self.screen_width, self.y_step))

    def write_matrix_to_file(self, filename):
        matrix = []
        backtracks = self.calculate_backtracks()
        for i in range(len(self.genome)):
            matrix.append([' '] * (backtracks + 1))
        trace_idx = 0
        inst_idx = self.trace[trace_idx]
        backtrack_idx = 0
        while True:
            matrix[inst_idx][backtrack_idx] = 'X'
            old_idx = inst_idx
            trace_idx += 1
            if trace_idx >= len(self.trace):
                break
            inst_idx = self.trace[trace_idx]
            diff = inst_idx - old_idx
            if diff < 0:
                backtrack_idx += 1
        with open(filename, 'w') as fp:
            for row in range(len(matrix)):
                for col in range(len(matrix[row])):
                    if col != 0:
                        fp.write(',')
                    fp.write(str(matrix[row][col]))
                fp.write('\n')

    def quit(self):
        pygame.quit()

    def save_to_file(self, filename):
        pygame.image.save(self.screen, filename)


if __name__ == '__main__':
    viz = LadderViz()
    trace = []
    with open('trace.txt', 'r') as fp:
        for line in fp:
            line = line.strip()
            if line == '':
                continue
            trace.append(int(line))
    if len(trace) > 2000:
        trace = trace[:2000]
    viz.set_trace(trace)
    print('Length of trace:', len(trace))
    genome = 'a' * (max(trace) + 1)
    print('Length of genome:', len(genome))
    viz.set_genome(genome)
    viz.render()
    viz.save_to_file('trace.png')
    viz.write_matrix_to_file('trace.csv')
    viz.quit()
