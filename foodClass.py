import pygame, os
from mainConst import action, screen, pixel_font
from abs_path import abs_path

pygame.init()

clicked_feed = False
coin_sound = pygame.mixer.Sound(abs_path('sounds/coin.ogg'))


class FoodMenu:
    def __init__(self, x, y, width, height, panel_path, box_path, food_1_path, food_2_path, food_3_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.panel = pygame.transform.scale(pygame.image.load(panel_path), (self.width, self.height))
        self.panel_rect = self.panel.get_rect(center=(self.x, self.y))

        self.box_1 = pygame.transform.scale(pygame.image.load(box_path), (150, 150))
        self.box_2 = pygame.transform.scale(pygame.image.load(box_path), (150, 150))
        self.box_3 = pygame.transform.scale(pygame.image.load(box_path), (150, 150))

        self.normal_image = self.box_1

        self.box_1_rect = self.box_1.get_rect(center=(self.x - 250, self.y))
        self.box_2_rect = self.box_2.get_rect(center=(self.x, self.y))
        self.box_3_rect = self.box_3.get_rect(center=(self.x + 250, self.y))

        self.food_1 = pygame.transform.scale(pygame.image.load(food_1_path), (100, 100))
        self.food_2 = pygame.transform.scale(pygame.image.load(food_2_path), (75, 100))
        self.food_3 = pygame.transform.scale(pygame.image.load(food_3_path), (100, 100))

        self.food_1_rect = self.food_1.get_rect(center=(self.x - 250, self.y))
        self.food_2_rect = self.food_2.get_rect(center=(self.x, self.y - 10))
        self.food_3_rect = self.food_3.get_rect(center=(self.x + 250, self.y))

        self.exit = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/iconCross_beige.png')), (40, 40))
        self.exit_rect = self.exit.get_rect(center=(75, 65))

        self.prompt_font = pygame.font.Font(abs_path('font/technicality1.ttf'), 20)
        self.yes_btn = pygame.image.load(abs_path('images/sprites/buttonLong_brown.png'))
        self.no_btn = pygame.image.load(abs_path('images/sprites/buttonLong_brown.png'))
        self.yes_btn = pygame.transform.scale(self.yes_btn, (110, 42))
        self.no_btn = pygame.transform.scale(self.no_btn, (110, 42))
        self.yes_btn_rect = self.yes_btn.get_rect(center=(self.x - 90, self.y + 90))
        self.no_btn_rect = self.no_btn.get_rect(center=(self.x + 90, self.y + 90))
        self.yes_text = self.prompt_font.render('Yes', True, (255, 255, 255))
        self.no_text = self.prompt_font.render('No', True, (255, 255, 255))

    def blit_food_menu(self):
        if clicked_feed:
            screen.blit(self.panel, self.panel_rect)

            prompt = self.prompt_font.render('Would you like to play the minigame?', True, (255, 255, 255))
            prompt_rect = prompt.get_rect(center=(self.x, self.y - 40))
            screen.blit(prompt, prompt_rect)

            screen.blit(self.yes_btn, self.yes_btn_rect)
            screen.blit(self.no_btn, self.no_btn_rect)
            screen.blit(self.yes_text, self.yes_text.get_rect(center=self.yes_btn_rect.center))
            screen.blit(self.no_text, self.no_text.get_rect(center=self.no_btn_rect.center))

    def hover(self, x, y):
        if clicked_feed:
            if self.yes_btn_rect.collidepoint((x, y)):
                self.yes_btn = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonLong_blue.png')), (110, 42))
            else:
                self.yes_btn = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonLong_brown.png')), (110, 42))

            if self.no_btn_rect.collidepoint((x, y)):
                self.no_btn = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonLong_blue.png')), (110, 42))
            else:
                self.no_btn = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonLong_brown.png')), (110, 42))
            return

        if self.box_1_rect.collidepoint((x, y)):
            text = pixel_font.render('Prise: 5 Lg Effects: +3', True, (255, 255, 255))
            screen.blit(text, (20, 120))
            self.box_1 = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonSquare_blue.png')), (150, 150))
        else:
            self.box_1 = self.normal_image
        if self.box_2_rect.collidepoint((x, y)):
            text = pixel_font.render('Prise: 10 Lg Effects: +6', True, (255, 255, 255))
            screen.blit(text, (270, 120))
            self.box_2 = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonSquare_blue.png')), (150, 150))
        else:
            self.box_2 = self.normal_image
        if self.box_3_rect.collidepoint((x, y)):
            text = pixel_font.render('Prise: 15 Lg Effects: +10', True, (255, 255, 255))
            screen.blit(text, (480, 120))
            self.box_3 = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/buttonSquare_blue.png')), (150, 150))
        else:
            self.box_3 = self.normal_image

    def pressed(self, x, y, event):
        global clicked_feed

        if clicked_feed:
            if self.yes_btn_rect.collidepoint((x, y)) and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_feed = False
                return
            if self.no_btn_rect.collidepoint((x, y)) and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_feed = False
                return
            return

        if self.box_1_rect.collidepoint((x, y)) and event.type == pygame.MOUSEBUTTONDOWN:
            if action['satiety'] + 3 <= 100 and action['logiki'] - 5 >= 0:
                coin_sound.play()
                action['satiety'] += 3
                action['toilet'] -= 3
                action['logiki'] -= 5
        if self.box_2_rect.collidepoint((x, y)) and event.type == pygame.MOUSEBUTTONDOWN:
            if action['satiety'] + 6 <= 100 and action['logiki'] - 10 >= 0:
                coin_sound.play()
                action['satiety'] += 6
                action['toilet'] -= 6
                action['logiki'] -= 10
        if self.box_3_rect.collidepoint((x, y)) and event.type == pygame.MOUSEBUTTONDOWN:
            if action['satiety'] + 10 <= 100 and action['logiki'] - 15 >= 0:
                coin_sound.play()
                action['satiety'] += 10
                action['toilet'] -= 10
                action['logiki'] -= 15
