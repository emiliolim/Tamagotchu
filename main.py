import random
import os
import time
import pygame
import foodClass
import panelClass
import playClass
import statisticsClass
from buttonClass import Button
from mainConst import action, tamagotchiJump, pixel_font
from abs_path import abs_path
from save_manager import SAVE_SLOT_COUNT, get_save_slot_summary, load_slot, save_slot

pygame.init()
pygame.time.set_timer(pygame.USEREVENT, 2000)
day = 90000
daysCount = 0
daysEvent = pygame.USEREVENT + 1
pygame.time.set_timer(daysEvent, day)

screen_width = 800
screen_height = 500
FPS = 45
timeout = 15
animCount = 0
text_timer = 0
night_timer = 0
endMenu = False
endGame = False
isSleep = False
cantClear = False
cantHelp = False

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tamagotchi')
pygame.display.set_icon(pygame.image.load(abs_path('images/sprites/logika.ico')))
clock = pygame.time.Clock()
start_time = None
game_time = None

cursor = pygame.image.load(abs_path('images/sprites/cursorHand_blue.png'))
pygame.mouse.set_visible(False)
background_menu = [pygame.transform.scale(pygame.image.load(abs_path('images/backgrounds/gifMenu-0.png')), (screen_width, screen_height)),
                   pygame.transform.scale(pygame.image.load(abs_path('images/backgrounds/gifMenu-1.png')), (screen_width, screen_height))]
background = pygame.transform.scale(pygame.image.load(abs_path('images/backgrounds/background.jpg')), (screen_width, screen_height))
gameover_img = pygame.transform.scale(pygame.image.load(abs_path('images/backgrounds/gameover_1.png')), (screen_width, screen_height))
sleep_image = pygame.transform.scale(pygame.image.load(abs_path('images/sprites//sleep.png')), (50, 50))
day_image = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/day.png')), (50, 50))
night_image = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/night.png')), (50, 50))
gameover_text = pixel_font.render('If you want play one more time, you have to restart game', True, (75, 255, 255))


def reset_game_state():
    global daysCount
    action['satiety'] = 100
    action['toilet'] = 100
    action['happy'] = 100
    action['health'] = 100
    action['logiki'] = 50
    daysCount = 0


def save_current_game(slot_index, slot_name=None):
    if slot_index is None:
        return
    save_slot(slot_index, action.copy(), slot_name or f'Save {slot_index}', days_lived=daysCount)


def load_game_slot(slot_index):
    global daysCount
    slot_data = load_slot(slot_index)
    action.update(slot_data.get('game_data', {}))
    daysCount = int(slot_data.get('days_lived', 0))
    return slot_data


def fit_text(font, text, max_width):
    if text is None:
        text = ''
    if font.size(text)[0] <= max_width:
        return text
    clipped = text
    while clipped and font.size(clipped + '...')[0] > max_width:
        clipped = clipped[:-1]
    return clipped + '...'


def save_selection_screen():
    slot_font = pygame.font.Font(abs_path('font/technicality1.ttf'), 18)
    avatar = pygame.transform.scale(pygame.image.load(abs_path('images/sprites/logika.png')), (52, 52))
    slot_buttons = []
    for index in range(1, SAVE_SLOT_COUNT + 1):
        slot_buttons.append((index, Button(400, 120 + (index - 1) * 120, 300, 120,
                                         abs_path('images/sprites/buttonLong_brown.png'), '')))
    back_btn = Button(400, 446, 180, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Back')

    while True:
        screen.blit(background_menu[0], (0, 0))
        title = pixel_font.render('Choose a save slot', True, (255, 255, 255))
        screen.blit(title, (220, 20))

        for slot_index, button in slot_buttons:
            button.blit_btn()
            summary = get_save_slot_summary(slot_index)
            content_rect = button.rect.inflate(-26, -16)
            right_marker = pygame.Rect(button.rect.right - 64, button.rect.centery - 26, 52, 52)

            if summary['used']:
                slot_name = fit_text(slot_font, summary['name'], content_rect.width - 80)
                name_text = slot_font.render(slot_name, True, (255, 255, 255))
                screen.blit(name_text, (content_rect.x + 10, content_rect.y + 6))

                days_text = slot_font.render(f'Days: {summary["days_lived"]}', True, (255, 255, 255))
                screen.blit(days_text, (content_rect.x + 10, content_rect.y + 28))

                last_save = summary['last_saved_at'] or 'No save yet'
                last_save_label = slot_font.render('Last save:', True, (255, 255, 255))
                screen.blit(last_save_label, (content_rect.x + 10, content_rect.y + 50))
                last_save_text = slot_font.render(fit_text(slot_font, last_save, content_rect.width - 130), True, (255, 255, 255))
                screen.blit(last_save_text, (content_rect.x + 10, content_rect.y + 72))
                screen.blit(avatar, (right_marker.x, right_marker.y))
            else:
                empty_text = slot_font.render('Empty Slot', True, (255, 255, 255))
                screen.blit(empty_text, (content_rect.x + 10, content_rect.y + 22))
                new_text = slot_font.render('New game', True, (255, 255, 255))
                screen.blit(new_text, (content_rect.x + 10, content_rect.y + 46))

                plus_circle = pygame.Surface((42, 42), pygame.SRCALPHA)
                pygame.draw.circle(plus_circle, (255, 255, 255, 220), (21, 21), 21, 2)
                plus_color = (255, 255, 255)
                pygame.draw.line(plus_circle, plus_color, (21, 8), (21, 34), 3)
                pygame.draw.line(plus_circle, plus_color, (8, 21), (34, 21), 3)
                screen.blit(plus_circle, (right_marker.x + 5, right_marker.y + 5))

        back_btn.blit_btn()

        pos_x, pos_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                pygame.quit()
                return None
            if back_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                button_sound.play()
                return None
            for slot_index, button in slot_buttons:
                if button.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    button_sound.play()
                    if get_save_slot_summary(slot_index)['used']:
                        load_game_slot(slot_index)
                        return slot_index
                    reset_game_state()
                    save_current_game(slot_index, f'Save {slot_index}')
                    return slot_index

        back_btn.hover(pos_x, pos_y)
        for _, button in slot_buttons:
            button.hover(pos_x, pos_y)

        if pygame.mouse.get_focused():
            screen.blit(cursor, (pos_x, pos_y))

        clock.tick(FPS)
        pygame.display.update()




def tamagotchiAnimation(x, y):
    global animCount
    if not isSleep:
        if animCount + 1 >= len(tamagotchiJump) * 6:
            animCount = 0
            screen.blit(tamagotchiJump[0], (x, y))
        else:
            screen.blit(tamagotchiJump[animCount // 6], (x, y))
            animCount += 1

        screen.blit(day_image, (735, 70))
    else:
        screen.blit(tamagotchiJump[0], (x, y))


def scoreTick():
    global start_time, timeout
    t_time = time.time() - start_time
    if t_time > timeout:
        action['satiety'] -= 3
        action['toilet'] -= 2
        action['happy'] -= 3
        action['health'] -= random.randint(0, 5)
        start_time = time.time()


def clearAfter():
    global cantClear
    if action['toilet'] + 16 <= 100:
        action['toilet'] += 16
        toilet_sound = pygame.mixer.Sound(abs_path('sounds/toilet.ogg'))
        toilet_sound.play()
    else:
        cantClear = True


def medicine():
    global cantHelp
    if action['logiki'] - 3 >= 0:
        if action['health'] + 10 <= 100:
            action['health'] += 10
            action['logiki'] -= 3
            medicine_sound = pygame.mixer.Sound(abs_path('sounds/medicine.ogg'))
            medicine_sound.play()
        else:
            cantHelp = True


def gameOver():
    return action['satiety'] <= 0 or action['toilet'] <= 0 or action['happy'] <= 0 or action['health'] <= 0


def spawn_coin(group):
    return playClass.Coin(random.randint(40, 760), random.randint(3, 5), abs_path('images/sprites/coin.png'), group)

coins = pygame.sprite.Group()

help_menu = panelClass.Panel(400, 250, 750, 450, abs_path('images/sprites/panel_brown.png'), ' You have to keep the indicators normal.',
                             'If at least one of them is equal to zero, you will lose.', 'Good Luck!')

logika_label = Button(70, 60, 100, 100, abs_path('images/sprites/logika.png'))
start_btn = Button(140, 150, 200, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Start')
rule_btn = Button(140, 250, 200, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Help')
exit_btn = Button(140, 350, 200, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Exit')


info_satiety = Button(20, 30, 25, 50, abs_path('images/sprites/lightning.png'))
info_toilet = Button(150, 30, 50, 50, abs_path('images/sprites/toilet.png'))
info_happy = Button(270, 30, 50, 50, abs_path('images/sprites/smile.png'))
info_health = Button(30, 90, 60, 60, abs_path('images/sprites/health.png'))

btn_statistic = Button(400, 200, 220, 55, abs_path('images/sprites/buttonLong_brown.png'), 'Statistics')
btn_satiety = Button(85, 467, 150, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Feed')
btn_toilet = Button(285, 467, 150, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Clear')
btn_play = Button(515, 467, 150, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Play')
btn_health = Button(715, 467, 150, 50, abs_path('images/sprites/buttonLong_brown.png'), 'Medicine')
exit_game_btn = Button(400, 280, 220, 55, abs_path('images/sprites/buttonLong_brown.png'), 'Exit')
menu_btn = Button(760, 20, 70, 38, abs_path('images/sprites/buttonLong_brown.png'), '')

food = foodClass.FoodMenu(400, 250, 750, 450, abs_path('images/sprites/panel_brown.png'),
                          abs_path('images/sprites/buttonSquare_beige_pressed.png'),
                          abs_path('images/sprites/food_1.png'), abs_path('images/sprites/food_2.png'), abs_path('images/sprites/food_3.png'))

play = playClass.Play()
basket = playClass.Basket()


button_sound = pygame.mixer.Sound(abs_path('sounds/button.ogg'))
button_sound.set_volume(0.05)


def game(slot_index=None):
    global endGame, isSleep, daysCount, night_timer, text_timer, cantClear, cantHelp, game_time, start_time
    endGame = False
    isSleep = False
    start_time = time.time()
    last_save_time = time.time()
    slot_name = None
    exit_prompt_open = False
    menu_open = False
    save_animation_active = False
    save_animation_start = 0.0
    save_animation_phase = 0
    if slot_index is not None:
        slot_data = load_slot(slot_index)
        slot_name = slot_data.get('save_name') or f'Save {slot_index}'
        action.update(slot_data.get('game_data', {}))
        daysCount = int(slot_data.get('days_lived', 0))

    yes_btn = Button(330, 290, 110, 42, abs_path('images/sprites/buttonLong_brown.png'), 'Yes')
    no_btn = Button(470, 290, 110, 42, abs_path('images/sprites/buttonLong_brown.png'), 'No')
    menu_close_btn = Button(566, 130, 30, 30, abs_path('images/sprites/buttonLong_brown.png'), 'X')
    menu_close_btn.btn_text = pygame.font.Font(abs_path('font/technicality1.ttf'), 18).render('X', True, (255, 255, 255))
    menu_close_btn.btn_text_rect = menu_close_btn.btn_text.get_rect(center=menu_close_btn.rect.center)
    restart_btn = Button(300, 390, 150, 44, abs_path('images/sprites/buttonLong_brown.png'), 'Restart')
    exit_to_menu_btn = Button(500, 390, 150, 44, abs_path('images/sprites/buttonLong_brown.png'), 'Exit')
    restart_btn.btn_text = pygame.font.Font(abs_path('font/technicality1.ttf'), 18).render('Restart', True, (255, 255, 255))
    restart_btn.btn_text_rect = restart_btn.btn_text.get_rect(center=restart_btn.rect.center)
    exit_to_menu_btn.btn_text = pygame.font.Font(abs_path('font/technicality1.ttf'), 18).render('Exit', True, (255, 255, 255))
    exit_to_menu_btn.btn_text_rect = exit_to_menu_btn.btn_text.get_rect(center=exit_to_menu_btn.rect.center)
    dialog_font = pygame.font.Font(abs_path('font/technicality1.ttf'), 20)
    game_over_title_font = pygame.font.Font(abs_path('font/technicality1.ttf'), 48)
    game_over_text_font = pygame.font.Font(abs_path('font/technicality1.ttf'), 20)
    save_font = pygame.font.Font(abs_path('font/technicality1.ttf'), 18)

    pygame.mixer.music.load(abs_path('sounds/backgroundMusic.ogg'))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)

    while not endGame:
        screen.blit(background, (0, 0))
        info_satiety.blit_btn()
        satiety_text = pixel_font.render(str(action['satiety']), False, (255, 255, 255))
        screen.blit(satiety_text, (40, 15))
        info_toilet.blit_btn()
        toilet_text = pixel_font.render(str(action['toilet']), False, (255, 255, 255))
        screen.blit(toilet_text, (180, 15))
        info_happy.blit_btn()
        smile_text = pixel_font.render(str(action['happy']), False, (255, 255, 255))
        screen.blit(smile_text, (300, 15))
        health_text = pixel_font.render(str(action['health']), False, (255, 255, 255))
        screen.blit(health_text, (70, 75))
        info_health.blit_btn()

        tamagotchiAnimation(330, 340)

        statistics = statisticsClass.Statistics(400, 250, 750, 450, abs_path('images/sprites/panel_brown.png'),
                                                str(action['logiki']) + ' Lg', 'Name: Tamagotchi', f'Days: {daysCount}')
        btn_satiety.blit_btn()
        btn_toilet.blit_btn()
        btn_play.blit_btn()
        btn_health.blit_btn()

        pos_x, pos_y = pygame.mouse.get_pos()
        game_over_active = (action['satiety'] <= 0 or action['toilet'] <= 0 or action['happy'] <= 0 or action['health'] <= 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                endGame = True
                pygame.quit()
            if event.type == daysEvent:
                isSleep = True
            if slot_index is not None and time.time() - last_save_time >= 15:
                save_current_game(slot_index, slot_name)
                last_save_time = time.time()

            if game_over_active:
                if restart_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    button_sound.play()
                    reset_game_state()
                    if slot_index is not None:
                        save_current_game(slot_index, f'Save {slot_index}')
                    start_time = time.time()
                    last_save_time = time.time()
                    game_over_active = False
                if exit_to_menu_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    button_sound.play()
                    endGame = True
                    return
                continue

            if menu_open:
                if exit_game_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    exit_prompt_open = True
                    menu_open = False
                    button_sound.play()
                    continue
                if btn_statistic.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    statisticsClass.clicked_statistics = True
                    menu_open = False
                    button_sound.play()
                if menu_close_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    menu_open = False
                    button_sound.play()
                if menu_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    menu_open = False
                    button_sound.play()
            elif not exit_prompt_open:
                if menu_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    menu_open = True
                    button_sound.play()
                if not isSleep:
                    if btn_satiety.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                        foodClass.clicked_feed = True
                        button_sound.play()
                    if action['logiki'] >= 0:
                        food.pressed(pos_x, pos_y, event)
                    if btn_toilet.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                        clearAfter()
                    if btn_play.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                        game_time = time.time()
                        playClass.clicked_play = True
                        button_sound.play()
                        pygame.mixer.music.unload()
                        pygame.mixer.music.load(abs_path('sounds/game.ogg'))
                        pygame.mixer.music.set_volume(0.7)
                        pygame.mixer.music.play()
                    if event.type == pygame.USEREVENT:
                        if playClass.clicked_play:
                            spawn_coin(coins)
                    if btn_health.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                        medicine()
            if exit_prompt_open:
                if yes_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    save_animation_active = True
                    save_animation_start = time.time()
                    save_animation_phase = 0
                    exit_prompt_open = False
                    button_sound.play()
                if no_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                    exit_prompt_open = False
                    button_sound.play()

            if save_animation_active:
                save_animation_phase += 1
                if time.time() - save_animation_start >= 1.0:
                    if slot_index is not None:
                        save_current_game(slot_index, slot_name)
                    endGame = True

            if statistics.exit_rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                statisticsClass.clicked_statistics = False
                button_sound.play()
            if food.exit_rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                foodClass.clicked_feed = False
                button_sound.play()
            if play.exit_rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                playClass.clicked_play = False
                playClass.scoreCount = 0
                playClass.timeCount = 60
                playClass.seconds = 1
                button_sound.play()
                pygame.mixer.music.unload()
                pygame.mixer.music.load(abs_path('sounds/backgroundMusic.ogg'))
                pygame.mixer.music.play(loops=-1)

        btn_satiety.hover(pos_x, pos_y)
        btn_toilet.hover(pos_x, pos_y)
        btn_play.hover(pos_x, pos_y)
        btn_health.hover(pos_x, pos_y)
        menu_btn.hover(pos_x, pos_y)
        menu_btn.blit_btn()
        pygame.draw.rect(screen, (255, 255, 255), (menu_btn.rect.centerx - 18, menu_btn.rect.centery - 11, 36, 4))
        pygame.draw.rect(screen, (255, 255, 255), (menu_btn.rect.centerx - 18, menu_btn.rect.centery - 1, 36, 4))
        pygame.draw.rect(screen, (255, 255, 255), (menu_btn.rect.centerx - 18, menu_btn.rect.centery + 9, 36, 4))

        if menu_open:
            menu_panel = pygame.Rect(190, 120, 420, 230)
            pygame.draw.rect(screen, (80, 50, 30), menu_panel)
            pygame.draw.rect(screen, (120, 90, 60), menu_panel.inflate(-12, -12))
            btn_statistic.hover(pos_x, pos_y)
            exit_game_btn.hover(pos_x, pos_y)
            btn_statistic.blit_btn()
            exit_game_btn.blit_btn()
            menu_close_btn.rect.topleft = (menu_panel.right - 38, menu_panel.top + 10)
            menu_close_btn.btn_text_rect = menu_close_btn.btn_text.get_rect(center=menu_close_btn.rect.center)
            menu_close_btn.hover(pos_x, pos_y)
            menu_close_btn.blit_btn()

        if game_over_active:
            pygame.mixer.music.stop()
            screen.blit(gameover_img, (0, 0))
            message = game_over_text_font.render(
                'Your tamogotchi died. Would you like to restart game or exit to menu?',
                True,
                (255, 255, 255)
            )
            screen.blit(message, message.get_rect(center=(400, 330)))
            restart_btn.rect.center = (300, 390)
            exit_to_menu_btn.rect.center = (500, 390)
            restart_btn.btn_text_rect = restart_btn.btn_text.get_rect(center=restart_btn.rect.center)
            exit_to_menu_btn.btn_text_rect = exit_to_menu_btn.btn_text.get_rect(center=exit_to_menu_btn.rect.center)
            restart_btn.hover(pos_x, pos_y)
            exit_to_menu_btn.hover(pos_x, pos_y)
            restart_btn.blit_btn()
            exit_to_menu_btn.blit_btn()

        if save_animation_active:
            save_panel = pygame.Rect(220, 170, 360, 140)
            pygame.draw.rect(screen, (80, 50, 30), save_panel)
            pygame.draw.rect(screen, (120, 90, 60), save_panel.inflate(-12, -12))
            save_text = save_font.render('Saving...', True, (255, 255, 255))
            save_text_rect = save_text.get_rect(center=(400, 205))
            screen.blit(save_text, save_text_rect)
            for i in range(8):
                angle = (save_animation_phase * 8 + i * 45) * 3.14159 / 180
                x = 400 + 20 * __import__('math').cos(angle)
                y = 250 + 20 * __import__('math').sin(angle)
                pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 4)

        if exit_prompt_open:
            prompt_panel = pygame.Rect(150, 150, 500, 200)
            pygame.draw.rect(screen, (80, 50, 30), prompt_panel)
            pygame.draw.rect(screen, (120, 90, 60), prompt_panel.inflate(-12, -12))
            prompt_text = dialog_font.render('Would you like to save and exit?', True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(400, 190))
            screen.blit(prompt_text, prompt_rect)
            yes_btn.blit_btn()
            no_btn.blit_btn()
            yes_btn.hover(pos_x, pos_y)
            no_btn.hover(pos_x, pos_y)

        if isSleep:
            screen.blit(night_image, (735, 70))
            screen.blit(sleep_image, (430, 350))
            if night_timer > 700:
                isSleep = False
                night_timer = 0
                daysCount += 1
                if slot_index is not None:
                    save_current_game(slot_index, slot_name)
            night_timer += 1

        if cantClear:
            text = pixel_font.render('Not now...', True, (255, 255, 255))
            screen.blit(text, (230, 400))
            if text_timer > 75:
                cantClear = False
                text_timer = 0
            text_timer += 1

        if cantHelp:
            text = pixel_font.render('Not now...', True, (255, 255, 255))
            screen.blit(text, (660, 400))
            if text_timer > 75:
                cantHelp = False
                text_timer = 0
            text_timer += 1

        if statisticsClass.clicked_statistics:
            statistics.blit_statistics()
        if foodClass.clicked_feed:
            food.blit_food_menu()
            food.hover(pos_x, pos_y)
        if playClass.clicked_play:
            play.blit_play()
            basket.blit_basket()
            play.check_time(game_time)
            coins.draw(screen)
            coins.update(screen_height)
            if pygame.sprite.spritecollide(basket, coins, True):
                playClass.scoreCount += 1

        keys = pygame.key.get_pressed()
        play.control(keys)
        basket.control(keys)

        gameOver()

        if pygame.mouse.get_focused():
            screen.blit(cursor, (pos_x, pos_y))

        scoreTick()
        clock.tick(FPS)
        pygame.display.update()


def menu():
    global endMenu, animCount, start_time
    pygame.mixer.music.load(abs_path('sounds/menu.ogg'))
    pygame.mixer.music.play(loops=-1)
    while not endMenu:
        if animCount + 1 >= len(background_menu) * 9:
            animCount = 0
            screen.blit(background_menu[0], (0, 0))
        else:
            screen.blit(background_menu[animCount // 9], (0, 0))
            animCount += 1

        logika_label.blit_btn()
        start_btn.blit_btn()
        rule_btn.blit_btn()
        exit_btn.blit_btn()

        pos_x, pos_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                endMenu = True
                pygame.quit()
            if start_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                button_sound.play()
                selected_slot = save_selection_screen()
                if selected_slot is not None:
                    endMenu = False
                    game(selected_slot)
            if rule_btn.rect.collidepoint(pos_x, pos_y) and event.type == pygame.MOUSEBUTTONDOWN:
                button_sound.play()
                panelClass.clicked_help = True
            if help_menu.exit_rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                button_sound.play()
                panelClass.clicked_help = False
            if exit_btn.rect.collidepoint((pos_x, pos_y)) and event.type == pygame.MOUSEBUTTONDOWN:
                button_sound.play()
                pygame.mouse.set_visible(True)
                endMenu = True
                pygame.quit()

        start_btn.hover(pos_x, pos_y)
        rule_btn.hover(pos_x, pos_y)
        exit_btn.hover(pos_x, pos_y)

        if panelClass.clicked_help:
            help_menu.blit_panel()

        if pygame.mouse.get_focused():
            screen.blit(cursor, (pos_x, pos_y))

        clock.tick(FPS)
        pygame.display.update()
        
if __name__ == '__main__':       
    menu()
