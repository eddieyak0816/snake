import pygame
import random

# Game settings
BOARD_SIZE = (20, 20)  # 20x20 grid
CELL_SIZE = 25
PLAY_AREA_SIZE = (BOARD_SIZE[0] * CELL_SIZE, BOARD_SIZE[1] * CELL_SIZE)
INFO_BAR_HEIGHT = 120
SCREEN_SIZE = (PLAY_AREA_SIZE[0], PLAY_AREA_SIZE[1] + INFO_BAR_HEIGHT)
FPS = 10

import colorsys
# Preset color options
PRESET_BG_COLORS = [
    (30, 30, 60), (30, 60, 30), (60, 30, 30), (0, 0, 0), (255, 255, 255), (100, 0, 100), (0, 100, 100)
]
PRESET_SNAKE_COLORS = [
    (255, 255, 0), (0, 255, 255), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)
]
BOARD_COLORS = [PRESET_BG_COLORS[0], PRESET_BG_COLORS[1], PRESET_BG_COLORS[2]]
SNAKE_BASE_COLORS = [PRESET_SNAKE_COLORS[0], PRESET_SNAKE_COLORS[1], PRESET_SNAKE_COLORS[2]]

# Apple colors
APPLE_COLOR = (255, 0, 0)
GLOWING_COLOR = (255, 255, 100)
TRANSPARENT_COLOR = (255, 0, 0, 80)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Multi-Board Snake')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.snake_color_transition = None  # (from_color, to_color, step)
        self.in_color_menu = False
        self.color_menu_board = 0
        self.color_menu_type = 'snake'  # 'snake' or 'bg'
        self.color_menu_snake_idx = [0, 1, 2]
        self.color_menu_bg_idx = [0, 1, 2]
        self.in_color_picker = False
        self.color_picker_value = ''
        self.in_color_grid = False
        self.color_grid_cursor = [0, 0]
        self.color_grid = self.generate_color_grid()
        self.game_over = False
        self.reset()
    def generate_color_grid(self):
        # Generate a grid of 18x12 colors (216 colors, like Paint)
        grid = []
        for y in range(12):
            row = []
            for x in range(18):
                if y < 2:
                    # Grayscale row
                    v = int(255 * x / 17)
                    row.append((v, v, v))
                else:
                    h = x / 18.0
                    s = 1.0
                    v = 0.5 + 0.5 * (y-2) / 9.0
                    r, g, b = colorsys.hsv_to_rgb(h, s, v)
                    row.append((int(r*255), int(g*255), int(b*255)))
            grid.append(row)
        return grid
        self.reset()

    def reset(self):
        self.snake = [[10, 10]]
        self.direction = (0, -1)
        self.length = 3
        self.score = 0
        self.current_board = 1  # 0, 1, 2
        self.apple_board = random.randint(0, 2)
        self.apple_pos = self.random_apple_pos()
        self.game_over = False
        self.snake_color_transition = None

    def random_apple_pos(self):
        while True:
            pos = [random.randint(0, BOARD_SIZE[0]-1), random.randint(0, BOARD_SIZE[1]-1)]
            if pos not in self.snake:
                return pos

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.in_color_grid:
                    # Color grid controls
                    if event.key == pygame.K_LEFT:
                        self.color_grid_cursor[0] = (self.color_grid_cursor[0] - 1) % 18
                    elif event.key == pygame.K_RIGHT:
                        self.color_grid_cursor[0] = (self.color_grid_cursor[0] + 1) % 18
                    elif event.key == pygame.K_UP:
                        self.color_grid_cursor[1] = (self.color_grid_cursor[1] - 1) % 12
                    elif event.key == pygame.K_DOWN:
                        self.color_grid_cursor[1] = (self.color_grid_cursor[1] + 1) % 12
                    elif event.key == pygame.K_RETURN:
                        color = self.color_grid[self.color_grid_cursor[1]][self.color_grid_cursor[0]]
                        if self.color_menu_type == 'snake':
                            SNAKE_BASE_COLORS[self.color_menu_board] = color
                            self.color_menu_snake_idx[self.color_menu_board] = -1  # -1 means custom
                        else:
                            BOARD_COLORS[self.color_menu_board] = color
                            self.color_menu_bg_idx[self.color_menu_board] = -1
                        self.in_color_grid = False
                    elif event.key == pygame.K_ESCAPE:
                        self.in_color_grid = False
                elif self.in_color_picker:
                    # Color picker controls
                    if event.key == pygame.K_RETURN:
                        try:
                            rgb = tuple(int(x) for x in self.color_picker_value.split(','))
                            if len(rgb) == 3 and all(0 <= v <= 255 for v in rgb):
                                if self.color_menu_type == 'snake':
                                    SNAKE_BASE_COLORS[self.color_menu_board] = rgb
                                else:
                                    BOARD_COLORS[self.color_menu_board] = rgb
                                self.in_color_picker = False
                                self.color_picker_value = ''
                        except Exception:
                            self.color_picker_value = ''
                    elif event.key == pygame.K_ESCAPE:
                        self.in_color_picker = False
                        self.color_picker_value = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.color_picker_value = self.color_picker_value[:-1]
                    else:
                        if event.unicode.isdigit() or event.unicode == ',':
                            self.color_picker_value += event.unicode
                elif self.in_color_menu:
                    # Color menu controls
                    if event.key == pygame.K_1:
                        self.color_menu_board = 0
                    elif event.key == pygame.K_2:
                        self.color_menu_board = 1
                    elif event.key == pygame.K_3:
                        self.color_menu_board = 2
                    elif event.key == pygame.K_s:
                        self.color_menu_type = 'snake' if self.color_menu_type == 'bg' else 'bg'
                    elif event.key == pygame.K_LEFT:
                        if self.color_menu_type == 'snake':
                            self.color_menu_snake_idx[self.color_menu_board] = (self.color_menu_snake_idx[self.color_menu_board] - 1) % len(PRESET_SNAKE_COLORS)
                        else:
                            self.color_menu_bg_idx[self.color_menu_board] = (self.color_menu_bg_idx[self.color_menu_board] - 1) % len(PRESET_BG_COLORS)
                    elif event.key == pygame.K_RIGHT:
                        if self.color_menu_type == 'snake':
                            self.color_menu_snake_idx[self.color_menu_board] = (self.color_menu_snake_idx[self.color_menu_board] + 1) % len(PRESET_SNAKE_COLORS)
                        else:
                            self.color_menu_bg_idx[self.color_menu_board] = (self.color_menu_bg_idx[self.color_menu_board] + 1) % len(PRESET_BG_COLORS)
                    elif event.key == pygame.K_p:
                        self.in_color_grid = True
                        self.color_grid_cursor = [0, 0]
                    elif event.key == pygame.K_RETURN:
                        # Apply changes
                        for i in range(3):
                            SNAKE_BASE_COLORS[i] = PRESET_SNAKE_COLORS[self.color_menu_snake_idx[i]]
                            BOARD_COLORS[i] = PRESET_BG_COLORS[self.color_menu_bg_idx[i]]
                        self.in_color_menu = False
                    elif event.key == pygame.K_ESCAPE:
                        self.in_color_menu = False
                else:
                    if event.key == pygame.K_UP:
                        if self.direction != (0, 1):
                            self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        if self.direction != (0, -1):
                            self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        if self.direction != (1, 0):
                            self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        if self.direction != (-1, 0):
                            self.direction = (1, 0)
                    elif event.key == pygame.K_w:
                        if self.current_board > 0:
                            from_color = self.get_snake_color()
                            self.current_board -= 1
                            to_color = self.get_snake_color()
                            self.snake_color_transition = (from_color, to_color, 0)
                    elif event.key == pygame.K_s:
                        if self.current_board < 2:
                            from_color = self.get_snake_color()
                            self.current_board += 1
                            to_color = self.get_snake_color()
                            self.snake_color_transition = (from_color, to_color, 0)
                    elif event.key == pygame.K_c:
                        self.in_color_menu = True
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
        # Mouse click support for color menu (open grid only on click down, not hold)
        if self.in_color_menu:
            mouse_pressed = pygame.mouse.get_pressed()[0]
            if mouse_pressed and not hasattr(self, 'mouse_was_down'):
                self.mouse_was_down = True
                mx, my = pygame.mouse.get_pos()
                bg_rect = pygame.Rect(SCREEN_SIZE[0]//2-120, 270, 60, 60)
                snake_rect = pygame.Rect(SCREEN_SIZE[0]//2-40, 270, 60, 60)
                if bg_rect.collidepoint(mx, my):
                    self.color_menu_type = 'bg'
                    self.in_color_grid = True
                    self.color_grid_cursor = [0, 0]
                elif snake_rect.collidepoint(mx, my):
                    self.color_menu_type = 'snake'
                    self.in_color_grid = True
                    self.color_grid_cursor = [0, 0]
            elif not mouse_pressed:
                if hasattr(self, 'mouse_was_down'):
                    delattr(self, 'mouse_was_down')
        # Mouse click support for color grid selection
        if self.in_color_grid:
            mouse_pressed = pygame.mouse.get_pressed()[0]
            if mouse_pressed and not hasattr(self, 'mouse_grid_was_down'):
                self.mouse_grid_was_down = True
                mx, my = pygame.mouse.get_pos()
                grid_x = SCREEN_SIZE[0]//2-180
                grid_y = 100
                cell_size = 24
                for y, row in enumerate(self.color_grid):
                    for x, color in enumerate(row):
                        rect = pygame.Rect(grid_x + x*cell_size, grid_y + y*cell_size, cell_size, cell_size)
                        if rect.collidepoint(mx, my):
                            self.color_grid_cursor = [x, y]
                            # Save and apply the selected color immediately
                            color = self.color_grid[y][x]
                            if self.color_menu_type == 'snake':
                                SNAKE_BASE_COLORS[self.color_menu_board] = color
                                self.color_menu_snake_idx[self.color_menu_board] = -1
                            else:
                                BOARD_COLORS[self.color_menu_board] = color
                                self.color_menu_bg_idx[self.color_menu_board] = -1
                            self.in_color_grid = False
                            break
            elif not mouse_pressed:
                if hasattr(self, 'mouse_grid_was_down'):
                    delattr(self, 'mouse_grid_was_down')
        return True
    def get_snake_color(self):
        # Returns the base color for the current board
        return SNAKE_BASE_COLORS[self.current_board]

    def get_gradient_colors(self, base_color, length):
        # Returns a list of colors from dark (head) to light (tail)
        r, g, b = base_color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        colors = []
        for i in range(length):
            # Head is darkest, tail is lightest
            factor = 0.5 + 0.5 * (i / max(1, length-1))  # 0.5 to 1.0
            new_v = min(1.0, v * factor)
            new_s = min(1.0, s * (0.8 + 0.2 * (i / max(1, length-1))))
            new_h = h + 0.05 * (i / max(1, length-1))  # slight hue shift
            r2, g2, b2 = colorsys.hsv_to_rgb(new_h, new_s, new_v)
            colors.append((int(r2*255), int(g2*255), int(b2*255)))
        return colors

    def get_transition_color(self):
        # Handles the two-step color transition
        if not self.snake_color_transition:
            return self.get_snake_color()
        from_color, to_color, step = self.snake_color_transition
        if step == 0:
            # Intermediate color: average
            mid_color = tuple((f+t)//2 for f, t in zip(from_color, to_color))
            self.snake_color_transition = (from_color, to_color, 1)
            return mid_color
        else:
            # Final color
            self.snake_color_transition = None
            return to_color

    def update(self):
        if self.game_over:
            return
        head = [self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1]]
        # Check wall collision
        if not (0 <= head[0] < BOARD_SIZE[0] and 0 <= head[1] < BOARD_SIZE[1]):
            self.game_over = True
            return
        # Check self collision
        if head in self.snake:
            self.game_over = True
            return
        self.snake.insert(0, head)
        if self.current_board == self.apple_board and head == self.apple_pos:
            self.length += 1
            self.score += 1
            self.apple_board = random.randint(0, 2)
            self.apple_pos = self.random_apple_pos()
        if len(self.snake) > self.length:
            self.snake.pop()

    def draw_board(self):
        # Draw play area
        self.screen.fill((30, 30, 30))
        play_area_rect = pygame.Rect(0, INFO_BAR_HEIGHT, PLAY_AREA_SIZE[0], PLAY_AREA_SIZE[1])
        pygame.draw.rect(self.screen, BOARD_COLORS[self.current_board], play_area_rect)
        # Determine snake color (with transition)
        base_color = self.get_transition_color()
        gradient_colors = self.get_gradient_colors(base_color, len(self.snake))
        # Draw snake with gradient
        for idx, segment in enumerate(self.snake):
            pygame.draw.rect(
                self.screen,
                gradient_colors[idx],
                (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE + INFO_BAR_HEIGHT, CELL_SIZE, CELL_SIZE)
            )
        # Draw apple
        apple_rect = (self.apple_pos[0]*CELL_SIZE, self.apple_pos[1]*CELL_SIZE + INFO_BAR_HEIGHT, CELL_SIZE, CELL_SIZE)
        if self.apple_board == self.current_board:
            color = APPLE_COLOR
        elif self.apple_board < self.current_board:
            color = GLOWING_COLOR
        else:
            color = TRANSPARENT_COLOR
        if color == TRANSPARENT_COLOR:
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill(color)
            self.screen.blit(surf, (apple_rect[0], apple_rect[1]))
        else:
            pygame.draw.ellipse(
                self.screen,
                color,
                apple_rect
            )
        # Draw info bar (score, board, instructions)
        info_y = 10
        score_text = self.font.render(f'Score: {self.score}', True, (255,255,255))
        self.screen.blit(score_text, (10, info_y))
        board_text = self.font.render(f'Board: {self.current_board+1}', True, (255,255,255))
        self.screen.blit(board_text, (180, info_y))
        color_instr1 = self.font.render('Press C to change colors for snake/background', True, (200,200,200))
        self.screen.blit(color_instr1, (350, info_y))
        color_instr2 = self.font.render('Use W/S to switch boards', True, (200,200,200))
        self.screen.blit(color_instr2, (350, info_y+30))
        if self.game_over:
            over_text = self.font.render('Game Over! Press R to restart.', True, (255,0,0))
            self.screen.blit(over_text, (10, info_y+60))
        # Draw color menu overlay
        if self.in_color_menu:
            self.draw_color_menu()
        if self.in_color_grid:
            self.draw_color_grid()
    def draw_color_grid(self):
        # Draws the color grid overlay
        overlay = pygame.Surface(SCREEN_SIZE)
        overlay.set_alpha(230)
        overlay.fill((20, 20, 20))
        self.screen.blit(overlay, (0, 0))
        title = self.font.render('Select a color (Arrow keys, Enter, Esc)', True, (255,255,255))
        self.screen.blit(title, (SCREEN_SIZE[0]//2-180, 60))
        grid_x = SCREEN_SIZE[0]//2-180
        grid_y = 100
        cell_size = 24
        for y, row in enumerate(self.color_grid):
            for x, color in enumerate(row):
                rect = pygame.Rect(grid_x + x*cell_size, grid_y + y*cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, rect)
                if [x, y] == self.color_grid_cursor:
                    pygame.draw.rect(self.screen, (255,255,255), rect, 2)
        info = self.font.render('Enter: select, Esc: cancel', True, (200,200,200))
        self.screen.blit(info, (SCREEN_SIZE[0]//2-180, grid_y + 12*cell_size + 10))

    def draw_color_menu(self):
        # Draws the color selection overlay
        overlay = pygame.Surface(SCREEN_SIZE)
        overlay.set_alpha(220)
        overlay.fill((40, 40, 40))
        self.screen.blit(overlay, (0, 0))
        title = self.font.render('Color Selection Menu', True, (255,255,255))
        self.screen.blit(title, (SCREEN_SIZE[0]//2-120, 30))
        info1 = self.font.render('Press 1/2/3 to select board', True, (200,200,200))
        self.screen.blit(info1, (SCREEN_SIZE[0]//2-120, 70))
        info2 = self.font.render('Arrow keys to change color', True, (200,200,200))
        self.screen.blit(info2, (SCREEN_SIZE[0]//2-120, 100))
        info3 = self.font.render('S to switch snake/background', True, (200,200,200))
        self.screen.blit(info3, (SCREEN_SIZE[0]//2-120, 130))
        info4 = self.font.render('Enter to confirm, Esc to cancel', True, (200,200,200))
        self.screen.blit(info4, (SCREEN_SIZE[0]//2-120, 160))
        # Show current selection
        sel_board = self.color_menu_board
        sel_type = self.color_menu_type
        sel_snake_idx = self.color_menu_snake_idx[sel_board]
        sel_bg_idx = self.color_menu_bg_idx[sel_board]
        # Use custom color if selected from grid
        if sel_snake_idx == -1:
            sel_snake_color = SNAKE_BASE_COLORS[sel_board]
        else:
            sel_snake_color = PRESET_SNAKE_COLORS[sel_snake_idx]
        if sel_bg_idx == -1:
            sel_bg_color = BOARD_COLORS[sel_board]
        else:
            sel_bg_color = PRESET_BG_COLORS[sel_bg_idx]
        board_text = self.font.render(f'Board: {sel_board+1}', True, (255,255,255))
        self.screen.blit(board_text, (SCREEN_SIZE[0]//2-120, 200))
        type_text = self.font.render(f'Editing: {sel_type.capitalize()} Color', True, (255,255,255))
        self.screen.blit(type_text, (SCREEN_SIZE[0]//2-120, 230))
        # Show color boxes
        pygame.draw.rect(self.screen, sel_bg_color, (SCREEN_SIZE[0]//2-120, 270, 60, 60))
        self.screen.blit(self.font.render('BG', True, (0,0,0)), (SCREEN_SIZE[0]//2-120+15, 270+15))
        pygame.draw.rect(self.screen, sel_snake_color, (SCREEN_SIZE[0]//2-40, 270, 60, 60))
        self.screen.blit(self.font.render('Snake', True, (0,0,0)), (SCREEN_SIZE[0]//2-40+5, 270+15))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_input()
            self.update()
            self.draw_board()
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    SnakeGame().run()
