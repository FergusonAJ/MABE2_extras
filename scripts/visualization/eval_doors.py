import pygame
import sys

if len(sys.argv) != 4:
    print('')
    print('Error! Expects exactly 3 command line arguments:')
    print('  1. the number of doors in the experiment')
    print('  2. the input filename')
    print('  3. the output filename')
    exit()

num_doors = int(sys.argv[1] )
input_filename = sys.argv[2] 
output_filename = sys.argv[3] 

max_width = 1024

data = []
with open(input_filename, 'r') as fp:
    for line in fp:
        line = line.strip()
        if line == '':
            continue
        line_parts = line.split()
        if len(line_parts) < 2 or line_parts[0] != '[DOORS]':
            continue
        info_parts = line_parts[1].split(',')
        door_taken = int(info_parts[0])
        door_needed = int(info_parts[1])
        data.append([door_taken, door_needed])

rect_width = 4
rect_height = 4
surf_width = rect_width * len(data)
if surf_width > max_width:
    surf_width = max_width
surf_height = rect_height * num_doors 

pygame.init()

surf = pygame.Surface((surf_width, surf_height))
for idx in range(len(data)):
    x = idx * rect_width
    if x >= surf_width: 
        break
    door_taken, door_needed = data[idx]
    for i in range(num_doors):
        pygame.draw.rect(surf, (50,50,50), 
                (x + (rect_width // 4), i * rect_height + (rect_height // 4),
                    rect_width // 2, rect_height // 2))
    if door_taken == door_needed:
        pygame.draw.rect(surf, (100,225,50), 
                (x, door_taken * rect_height, rect_width, rect_height))
    else:
        pygame.draw.rect(surf, (225,100,25), 
                (x, door_taken * rect_height, rect_width, rect_height))
        pygame.draw.rect(surf, (50,100,225), 
                (x, door_needed * rect_height, rect_width, rect_height))


pygame.image.save(surf, output_filename)

