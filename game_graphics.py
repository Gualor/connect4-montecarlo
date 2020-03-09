from connect4_mcts import GameBoard
import pygame
import random
import os


# CONSTANTS

BLUE = (0, 123, 255)
LIGHT_BLUE = (215, 252, 250)
DARK_BLUE = (0, 73, 151)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (238, 219, 4)
DARK_YELLOW = (138, 119, 0)
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)

WIN_SIZE = (W_WIDTH, W_HEIGHT) = (800, 600)
FPS = 30

# CLASSES


class GameGraphics:
    def __init__(self, win_size, surface):
        self.win_size = win_size
        self.surface = surface
        self.clouds = {}
        self.n_cloud = 4
        self.create_clouds()

    def update_clouds(self, speed):
        # Cloud moving animation
        for key in self.clouds.keys():
            self.clouds[key][0] -= speed/FPS
        # Remove out of screen clouds
        self.remove_clouds()
        # Create new clouds
        self.create_clouds()

    def create_clouds(self):
        # Add new clouds
        while len(self.clouds) < self.n_cloud:
            posx = random.randint(self.win_size[0], 2*self.win_size[0])
            posy = random.randint(0, 2*self.win_size[1])
            dist = 150
            name = 0
            # Cloud spacing
            spaced = True
            for pos in self.clouds.values():
                if abs(pos[1] - posy) < dist:
                    spaced = False
            if spaced:
                # Cloud naming
                while str(name) in self.clouds.keys():
                    name += 1
                # Add cloud
                self.clouds[str(name)] = [posx, posy]

    def remove_clouds(self):
        # Remove out of screen clouds
        remove = []
        toll = 200
        for key, val in self.clouds.items():
            if val[0] < 0 - toll:
                remove.append(key)
        for i in remove:
            del self.clouds[i]

    def draw_cloud(self, pos):
        # Draw single cloud given position
        radius = 30
        pos = (round(pos[0]), round(pos[1]))
        pygame.draw.circle(self.surface, BLACK, pos, radius)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+30, pos[1]+10), radius-10)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+60, pos[1]), radius)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+110, pos[1]), radius)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+30, pos[1]-30), radius)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+30, pos[1]+20), radius+10)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+70, pos[1]-20), radius+10)
        pygame.draw.circle(self.surface, BLACK, (pos[0]+80, pos[1]+30), radius)
        pygame.draw.circle(self.surface, WHITE, pos, radius)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+30, pos[1]+10), radius-10)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+60, pos[1]), radius)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+110, pos[1]), radius)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+30, pos[1]-30), radius)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+30, pos[1]+20), radius+10)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+70, pos[1]-20), radius+10)
        pygame.draw.circle(self.surface, WHITE, (pos[0]+80, pos[1]+30), radius)

    def draw_background(self, speed):
        # Draw background elements
        self.surface.fill(LIGHT_BLUE)
        self.update_clouds(speed=speed)
        for pos in self.clouds.values():
            self.draw_cloud(pos)

    def draw_board(self, board):
        # Draw game board and players' pieces
        radius = 30
        w_space = 41
        h_space = 13
        shift = 7
        # Draw frame shadow
        frame = pygame.Surface((752, 451))
        frame.fill(BLACK)
        frame.set_colorkey(WHITE)
        for i in range(7):
            for j in range(6):
                pos = (w_space + radius + i*(w_space + 2*radius), h_space + radius + j*(h_space + 2*radius))
                pygame.draw.circle(frame, WHITE, pos, radius)
        self.surface.blit(frame, (w_space/2+shift, 125-shift))
        outline = pygame.Surface(self.win_size)
        outline.fill(WHITE)
        outline.set_colorkey(WHITE)
        points1 = ((0, shift), (shift, 0), (752+shift, 0), (752, shift))
        points2 = ((752+shift, 0), (752+shift, 451), (752, 451+shift), (752, shift))
        pygame.draw.polygon(outline, BLACK, points1)
        pygame.draw.polygon(outline, DARK_BLUE, points2)
        self.surface.blit(outline, (20, 117))
        # Draw frame
        frame = pygame.Surface((752, 451))
        frame.fill(BLUE)
        frame.set_colorkey(WHITE)
        for i in range(7):
            for j in range(6):
                pos = (w_space + radius + i*(w_space + 2*radius), h_space + radius + j*(h_space + 2*radius))
                pygame.draw.circle(frame, WHITE, pos, radius)
        # Draw pieces
        for row in range(6):
            for col in range(7):
                if board[5-row, col] == 1:
                    pos = (w_space + radius + col*(w_space + 2*radius), h_space + radius + row*(h_space + 2*radius))
                    pygame.draw.circle(frame, RED, pos, radius)
                elif board[5-row, col] == 2:
                    pos = (w_space + radius + col*(w_space + 2*radius), h_space + radius + row*(h_space + 2*radius))
                    pygame.draw.circle(frame, YELLOW, pos, radius)
        # Blit surface to screen
        self.surface.blit(frame, (w_space/2, 125))

    def draw_select(self, column, turn):
        # Column selector
        radius = 30
        w_space = 41
        h_space = 13
        shift = 3
        # Draw colored piece based on player turn
        if turn == 1:
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (w_space + radius + (column-1)*(w_space + 2*radius), h_space + radius)
            pygame.draw.circle(surf, DARK_RED, pos, radius)
            self.surface.blit(surf, (w_space/2+shift, 18-shift))
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (w_space + radius + (column-1)*(w_space + 2*radius), h_space + radius)
            pygame.draw.circle(surf, RED, pos, radius)
            self.surface.blit(surf, (w_space/2, 18))
        elif turn == 2:
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (w_space + radius + (column-1)*(w_space + 2*radius), h_space + radius)
            pygame.draw.circle(surf, DARK_YELLOW, pos, radius)
            self.surface.blit(surf, (w_space/2+shift, 18-shift))
            surf = pygame.Surface((752, 451))
            surf.set_colorkey((0, 0, 0))
            pos = (w_space + radius + (column-1)*(w_space + 2*radius), h_space + radius)
            pygame.draw.circle(surf, YELLOW, pos, radius)
            self.surface.blit(surf, (w_space/2, 18))

    def gameover_screen(self, winner, select):
        shift = 3
        surf = pygame.Surface(self.win_size)
        font = pygame.font.SysFont("Futura", 50)
        surf.fill(WHITE)
        surf.set_colorkey(WHITE)
        # Draw menu window
        pygame.draw.rect(surf, BLUE, (100, 150, 600, 300))
        pygame.draw.rect(surf, YELLOW, (200, 380, 120, 40))
        pygame.draw.rect(surf, RED, (480, 380, 120, 40))
        # Draw window shadow
        pygame.draw.polygon(surf, BLACK, ((100, 150), (100+shift, 150-shift), (700+shift, 150-shift), (700+shift, 450-shift), (700, 450), (700, 150)))
        pygame.draw.polygon(surf, BLACK, ((200, 380), (200+shift, 380-shift), (320+shift, 380-shift), (320+shift, 420-shift), (320, 420), (320, 380)))
        pygame.draw.polygon(surf, BLACK, ((480, 380), (480+shift, 380-shift), (600+shift, 380-shift), (600+shift, 420-shift), (600, 420), (600, 380)))
        # Draw answear selector
        if select == 1:
            pygame.draw.rect(surf, WHITE, (200, 380, 120, 40), 3)
        elif select == 2:
            pygame.draw.rect(surf, WHITE, (480, 380, 120, 40), 3)
        # Draw separator line
        pygame.draw.rect(surf, WHITE, (150, 260, 500, 5))
        self.surface.blit(surf, (0, 0))
        # Draw text
        if winner == 1:
            champion = font.render("Monte Carlo is the winner!".format(winner), True, WHITE)
            self.surface.blit(champion, (180, 182))
        elif winner == 2:
            champion = font.render("Human won against the machine!".format(winner), True, WHITE)
            self.surface.blit(champion, (125, 182))
        else:
            champion = font.render("Human and machine tied!".format(winner), True, WHITE)
            self.surface.blit(champion, (185, 182))
        rematch = font.render("Rematch?", True, WHITE)
        yes = font.render("YES", True, WHITE)
        no = font.render("NO", True, WHITE)
        yes_s = font.render("YES", True, BLACK)
        no_s = font.render("NO", True, BLACK)
        self.surface.blit(rematch, (320, 310))
        self.surface.blit(yes_s, (225, 383))
        self.surface.blit(no_s, (517, 383))
        self.surface.blit(yes, (223, 385))
        self.surface.blit(no, (515, 385))


if __name__ == "__main__":

    # Initialize stuff
    os.system('cls')
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption('Connect 4 Montecarlo')
    window = pygame.display.set_mode(WIN_SIZE)
    clock = pygame.time.Clock()

    # Draw game graphics
    graphics = GameGraphics(win_size=WIN_SIZE, surface=window)

    # Begin new game
    while True:

        # Initialize game
        gameboard = GameBoard(cpu=1)
        winner = None
        select = 1

        # Game loop
        while True:

            # Check game over
            winner = gameboard.check_win()
            if winner is not None:
                pygame.time.wait(1500)
                break
            else:
                if list(gameboard.board.flatten()).count(0) == 0:
                    winner = 0
                    pygame.time.wait(1500)
                    break

            # Game controls
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    # Move column selection to the right
                    if event.key == pygame.K_RIGHT:
                        if select < 7:
                            select += 1
                    # Move column selection to the left
                    elif event.key == pygame.K_LEFT:
                        if select > 1:
                            select -= 1
                    # Enter column and execute move
                    elif event.key == pygame.K_RETURN:
                        if gameboard.board[5, select - 1] == 0:
                            gameboard.apply_move(column=select)

            # Draw game graphics
            graphics.draw_background(speed=100)
            graphics.draw_board(board=gameboard.board)
            graphics.draw_select(column=select, turn=gameboard.turn)

            # Update stuff
            clock.tick(FPS)
            pygame.event.pump()
            pygame.display.flip()

        # Game over / continue
        select = 1
        new_game = False
        while not new_game:

            # Menu controls
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    # Move column selection to the right
                    if event.key == pygame.K_RIGHT:
                        if select < 2:
                            select += 1
                    # Move column selection to the left
                    elif event.key == pygame.K_LEFT:
                        if select > 1:
                            select -= 1
                    # Enter column and execute move
                    elif event.key == pygame.K_RETURN:
                        # Start new game
                        if select == 1:
                            new_game = True
                        elif select == 2:
                            exit()

            # Draw game over screen
            graphics.draw_background(speed=100)
            graphics.gameover_screen(winner, select)

            # Update stuff
            clock.tick(FPS)
            pygame.event.pump()
            pygame.display.flip()
