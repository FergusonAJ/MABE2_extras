import pygame

pygame.init()

screen_width = 600
screen_height = 600
grid_width = 60
grid_height = 60
tile_width = screen_width // grid_width
tile_height = screen_height // grid_height

screen = pygame.display.set_mode((screen_width, screen_height))

filename = './pop_structure.txt'
pop_list = []
with open(filename, 'r') as fp:
    for line in fp:
        line.strip()
        line.strip('"')
        if 'pop' not in line:
            pop_list.append(line)

frame = 0
is_running = True
while is_running:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            is_running = False
        elif evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_ESCAPE or evt.key == pygame.K_q:
                is_running = False

    screen.fill((0,0,0))

    cur_x = 0
    cur_y = 0
    for i in range(grid_width * grid_height):
        cur_grid = pop_list[frame]
        if i >= len(cur_grid):
            break
        color = (255,255,255)
        if cur_grid[i] == 'X':
            color = (200,50,10)
        pygame.draw.rect(screen, color, 
                (cur_x * tile_width, cur_y * tile_height, tile_width, tile_height))
        cur_x += 1
        if cur_x >= grid_width:
            cur_y += 1
            cur_x = 0
    pygame.display.flip()

    frame += 1
    if frame >= len(pop_list):
        frame = 0


