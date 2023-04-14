try:
    import pygame as pg
except ImportError:
    import sys
    import subprocess

    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'pygame'])
        import pygame as pg

        print('ЗАРАБОТАЛО!!!')
    except Exception:
        print(Exception)
finally:
    import random
    import time

# COLOR SPACE
WHITE = (255, 255, 255)
HALF_WHITE = (181, 181, 181)
HALF_RED = (163, 0, 0)
WHITE_BLUE = (85, 105, 207)
BLACK = (0, 0, 0)
YELLOW = (222, 174, 0)
RED = (213, 50, 80)
GREEN = (3, 161, 3)
BLUE = (0, 21, 247)

# GAME SETTING
GAME_SPEED = 60
SHIP_SIZE = 15
SHIP_SHIFT = 4
ENEMY_SIZE = 20
CANON_COLD_DOWN = 2
ENEMIES_SPAWN = 15
WAVE_TIME = 30


def message(surface: pg.Surface, msg: str, color, p_x=80.0, p_y=240.0):
    msg = pg.font.SysFont("bahnschrift", 35).render(msg, True, color)
    message_box = msg.get_rect(topleft=(p_x, p_y))
    surface.blit(msg, message_box)
    return message_box


def your_score(surface: pg.Surface, score):
    value = pg.font.SysFont("comicsansms", 30).render('счёт: ' + str(score), True, YELLOW)
    surface.blit(value, [0, 0])


def our_ship(surface: pg.Surface, ship: pg.Rect):
    if ship.x < 0: ship.x = 0
    if ship.y < 0: ship.y = 0
    if ship.x + SHIP_SIZE > surface.get_size()[0]: ship.x = surface.get_size()[0] - SHIP_SIZE
    if ship.y + SHIP_SIZE > surface.get_size()[1]: ship.y = surface.get_size()[1] - SHIP_SIZE
    pg.draw.rect(surface, RED, ship)
    return ship


def enemy_ship(surface: pg.Surface, enemies: list, ship: pg.Rect, score: int, game_over=False):
    for e in enemies:
        e[0] -= 5
        pg.draw.rect(surface, GREEN, [e[0], e[1], ENEMY_SIZE * 1.5, ENEMY_SIZE])
        if e[0] < -ENEMY_SIZE:
            enemies.remove(e)
            score -= 1
        r_e = pg.Rect(e[0], e[1], ENEMY_SIZE, ENEMY_SIZE)
        if ship.colliderect(r_e):
            game_over = True
        else:
            game_over = False
    return enemies, game_over, score


def field_draw(surface, field, dis_w, dis_h):
    star_c = round(random.randrange(0, 2))
    c = 0
    while c != star_c:
        star_y = round(random.randrange(0, dis_h) / 3) * 3
        star_type = round(random.randrange(0, 100))
        field.append([dis_w + 10, star_y, star_type])
        c += 1
    for f in field:
        f[0] -= 10
        if f[0] < -20:
            del field[0]
    for f in field:
        if f[2] <= 50:
            pg.draw.rect(surface, WHITE, [f[0], f[1], 3, 3])
        elif 50 < f[2] <= 75:
            pg.draw.rect(surface, HALF_WHITE, [f[0], f[1], 3, 3])
        elif 75 < f[2] < 90:
            pg.draw.rect(surface, HALF_RED, [f[0], f[1], 3, 3])
        elif 90 < f[2]:
            pg.draw.rect(surface, WHITE_BLUE, [f[0], f[1], 3, 3])
    return field


def bullets(surface: pg.Surface, our: list, enemy: list, ship: pg.Rect, enemies: list, score: int):
    bullet_radius = 2
    if len(our) > 0:
        for o in our:
            pg.draw.circle(surface, RED, [o[0], o[1]], bullet_radius)
            if o[0] < surface.get_size()[0]:
                o[0] += 3
            else:
                our.remove(o)
            for e in enemies:
                r_e = pg.Rect(e[0], e[1], ENEMY_SIZE, ENEMY_SIZE)
                if r_e.collidepoint(o[0], o[1]):
                    enemies.remove(e)
                    score += 1

    if len(enemy) > 0:
        for e in enemy:
            e[0] -= 3
    return our, enemy, enemies, score


def game_loop(dis):
    clock = pg.time.Clock()
    ship = pg.Rect(10, dis.get_size()[1] / 2, SHIP_SIZE, SHIP_SIZE)
    game_over = False
    score = 0
    field = []
    enemies = []
    our_bullets = []
    enemy_bullets = []
    enemies_hold_down = ENEMIES_SPAWN
    wave_timer = WAVE_TIME
    canon_hold_down = CANON_COLD_DOWN  # in seconds
    pg.time.set_timer(pg.USEREVENT, 100)  # 100 millisecond
    game_started = False
    while not game_over:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = True

            if event.type == pg.USEREVENT:
                if canon_hold_down > 0:
                    canon_hold_down -= 1
                else:
                    canon_hold_down = CANON_COLD_DOWN
                    our_bullets.append([ship.right, ship.centery])

                if game_started:
                    if enemies_hold_down > 0:
                        enemies_hold_down -= 1
                    else:
                        enemies_hold_down = ENEMIES_SPAWN
                        enemies.append([
                            dis.get_size()[0] + 30,
                            round(random.randrange(0, int(dis.get_size()[1] / ENEMY_SIZE))) * ENEMY_SIZE
                        ])
                else:
                    wave_timer -= 1
                    if wave_timer == 0: game_started = True

        key = pg.key.get_pressed()
        if key[pg.K_LEFT]:
            ship.x += -SHIP_SHIFT
        if key[pg.K_RIGHT]:
            ship.x += +SHIP_SHIFT
        if key[pg.K_UP]:
            ship.y += -SHIP_SHIFT
        if key[pg.K_DOWN]:
            ship.y += +SHIP_SHIFT

        dis.fill(BLACK)  # background

        field = field_draw(dis, field, dis.get_size()[0], dis.get_size()[1])  # draw a stars
        ship = our_ship(dis, ship)  # draw the ship
        enemies, game_over, score = enemy_ship(dis, enemies, ship, score, game_over)  # spawn enemies
        our_bullets, enemy_bullets, enemies, score = bullets(dis, our_bullets, enemy_bullets, ship, enemies, score)  # bullet control
        your_score(dis, score)  # score
        pg.display.flip()  # update the surface with double buffering
        clock.tick(GAME_SPEED)
        if score < 0:
            game_over = True

    # while game_over:
    #     dis.fill(BLACK)
    #     message('ПОТРАЧЕНО', RED)
    #     message('Enter - продолжить, ESC - завершить', RED, 10, 2.0)
    #     pg.display.update()
    #     for event in pg.event.get():
    #         if event.type == pg.QUIT:
    #             gameover = True
    #             gameclose = False
    #         if event.type == pg.KEYDOWN:
    #             if event.key == pg.K_ESCAPE:
    #                 gameover = True
    #                 gameclose = False
    #             if event.key == pg.K_RETURN:
    #                 gameloop()
    pass


def main_menu():
    dis_w = 800
    dis_h = 600
    dis = pg.display.set_mode((dis_w, dis_h), vsync=True)
    pg.display.set_caption('SiSc Shooter')

    game_over = False
    while not game_over:
        dis.fill(BLACK)

        mb_start = message(dis, 'Начать игру', GREEN, dis_w / 10.0, dis_h / 2.5)
        mb_finish = message(dis, 'Выйти из игры', RED, dis_w / 10.0, dis_h / 2.0)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = True
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if mb_start.collidepoint(event.pos):
                    game_loop(dis)
                if mb_finish.collidepoint(event.pos):
                    game_over = True
            if (pg.key.get_pressed()[pg.K_SPACE]) or (pg.key.get_pressed()[pg.K_RETURN]):
                game_loop(dis)
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                game_over = True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pg.init()
    main_menu()
    pg.quit()
    quit()
