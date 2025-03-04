import pygame
import classes


pygame.init()
if __name__ == "__main__":
    grid_size = int(input("Zadej velikost pole: "))
    num_mines = int(input("Zadej počet min: "))
    game = classes.MineSweeperGame(grid_size, num_mines)
    game.run()
    pygame.quit()
