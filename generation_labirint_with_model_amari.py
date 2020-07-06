import math
import numpy
import pygame
from scipy.misc import imsave
from scipy.ndimage.filters import gaussian_filter
class AmariModel(object):
    def __init__(self, size):
        self.h = -0.1
        self.k = 0.05
        self.K = 0.125
        self.m = 0.025
        self.M = 0.065
        self.stimulus = -self.h * numpy.random.random(size)
        self.activity = numpy.zeros(size) + self.h
        self.excitement = numpy.zeros(size)
        self.inhibition = numpy.zeros(size)
    def stimulate(self):
        self.activity[:, :] = self.activity > 0
        sigma = 1 / math.sqrt(2 * self.k)
        gaussian_filter(self.activity, sigma, 0, self.excitement, "wrap")
        self.excitement *= self.K * math.pi / self.k
        sigma = 1 / math.sqrt(2 * self.m)
        gaussian_filter(self.activity, sigma, 0, self.inhibition, "wrap")
        self.inhibition *= self.M * math.pi / self.m
        self.activity[:, :] = self.h
        self.activity[:, :] += self.excitement
        self.activity[:, :] -= self.inhibition
        self.activity[:, :] += self.stimulus
class AmariMazeGenerator(object):
    def __init__(self, size):
        self.model = AmariModel(size)
        pygame.init()
        self.display = pygame.display.set_mode(size, 0)
        pygame.display.set_caption("Amari Maze Generator")
    def run(self):
        pixels = pygame.surfarray.pixels3d(self.display)
        index = 0
        running = True
        while running:
            self.model.stimulate()
            pixels[:, :, :] = (255 * (self.model.activity > 0))[:, :, None]
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:
                        imsave("{0:04d}.png".format(index), pixels[:, :, 0])
                        index = index + 1
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    position = pygame.mouse.get_pos()
                    self.model.activity[position] = 1
        pygame.quit()
def main():
    generator = AmariMazeGenerator((512, 512))
    generator.run()
if __name__ == "__main__":
    main()