
import pygame
import random

pygame.init()
pygame.mixer.init()

# Вікно
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fantasy RPG")
clock = pygame.time.Clock()

# Фони для локацій
backgrounds = [
    pygame.transform.scale(pygame.image.load(f"background{i}.png"), (WIDTH, HEIGHT))
    for i in range(1, 6)
]

# Музика для локацій
music_tracks = [f"music{i}.mp3" for i in range(1, 6)]
current_music = -1

def play_location_music(index):
    global current_music
    if index != current_music:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_tracks[index])
        pygame.mixer.music.play(-1)
        current_music = index

# Спрайт-лист для гравця
sprite_sheet = pygame.image.load("klipartz.com.png").convert_alpha()
sheet_w, sheet_h = sprite_sheet.get_size()
cols = rows = 4
frame_w = sheet_w // cols
frame_h = sheet_h // rows
TARGET = 48

# Анімація
ANIM_SPEED = 150  # мс на кадр
anim_idx = 0
anim_timer = 0

def get_frames(row):
    return [
        pygame.transform.scale(
            sprite_sheet.subsurface(pygame.Rect(c*frame_w, row*frame_h, frame_w, frame_h)),
            (TARGET, TARGET)
        )
        for c in range(cols)
    ]

# Напрямки
RIGHT, LEFT, UP, DOWN = 0, 1, 2, 3
frames = {
    RIGHT: get_frames(1),
    LEFT:  get_frames(2),
    UP:    get_frames(3),
    DOWN:  get_frames(0)
}

# Гравець
player = pygame.Rect(100, 100, TARGET, TARGET)
speed = 4
health = 100
max_health = 100
healing_stones = 0

# Локації та вороги
max_loc = 5
cur_loc = 1
per_loc = 5
kills = 0
enemy_pos = []
enemy_hp = []
for loc in range(1, max_loc+1):
    pos_list, hp_list = [], []
    if loc < max_loc:
        for _ in range(per_loc):
            pos_list.append(pygame.Rect(random.randint(100,700), random.randint(100,500), 64, 64))
            hp_list.append(100)
    enemy_pos.append(pos_list)
    enemy_hp.append(hp_list)

# Таймінг атаки
MIN_MS = 2000
MAX_MS = 3000
RANGE_MS = MAX_MS - MIN_MS
in_battle = False
start_t = 0
req = 0
holding = False
hold_timer = 0
message = ""
menu = ["Атака", "Втеча", "Лікуватися"]
menu_i = 0
cur_enemy = None

# Ворог атакує
enemy_attack_timer = 0
enemy_attack_interval = 3000

# Кінцівки
def show_ending(kills):
    endings = [
        "Ви не вбили жодного. Миротворець!",
        "Ваша подорож була короткою, але небезпечною.",
        "Ви мужньо боролися й залишили слід.",
        "Ваш меч забрав багато душ. Ви герой?",
        "Ви стали легендою... і монстром."
    ]
    if kills == 0:
        idx = 0
    elif kills < 5:
        idx = 1
    elif kills < 10:
        idx = 2
    elif kills < 15:
        idx = 3
    else:
        idx = 4
    screen.fill((0,0,0))
    font = pygame.font.SysFont(None, 48)
    text1 = font.render("КІНЕЦЬ ГРИ", True, (255,255,255))
    text2 = font.render(endings[idx], True, (200,200,200))
    screen.blit(text1, (WIDTH//2 - text1.get_width()//2, 200))
    screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 300))
    pygame.display.flip()
    pygame.time.wait(5000)

# Бій
def start_attack():
    global in_battle, start_t, req, holding, hold_timer, message, menu_i
    in_battle = True
    start_t = pygame.time.get_ticks()
    req = random.randint(MIN_MS, MAX_MS)
    holding = False
    hold_timer = 0
    message = f"Утримуйте Enter {req/1000:.2f} с"
    menu_i = 0

def finish_attack():
    global in_battle, message, kills, holding, hold_timer, cur_enemy, healing_stones
    if not holding:
        message = "Промах!"
    else:
        diff = abs(hold_timer - req)
        dmg = max(5, int(100 * (1 - diff/(RANGE_MS/2))))
        message = f"Урон: {dmg}"
        idx = enemy_pos[cur_loc-1].index(cur_enemy)
        enemy_hp[cur_loc-1][idx] -= dmg
        if enemy_hp[cur_loc-1][idx] <= 0:
            enemy_pos[cur_loc-1].pop(idx)
            enemy_hp[cur_loc-1].pop(idx)
            kills += 1
            message = "Ворог переможений!"
            if random.random() < 0.5:
                healing_stones += 1
                message += " Знайдено лікувальне каміння!"
    in_battle = False
    holding = False
    hold_timer = 0

def flee():
    global in_battle, message
    message = "Ви втекли!"
    in_battle = False

def show_start_menu():
    selected = 0
    options = ["Почати гру", "Вихід"]
    font_big = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 32)
    while True:
        screen.fill((0, 0, 0))
        title = font_big.render("Fantasy RPG", True, (255, 255, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        for i, line in enumerate([
            "Управління: W A S D - рух",
            "Enter - вибір / атака",
            "Esc - втеча",
            "Space - почати бій"
        ]):
            txt = font_small.render(line, True, (180, 180, 180))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 160 + i * 30))

        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            txt = font_big.render(opt, True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 350 + i * 70))

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_w, pygame.K_UP):
                    selected = (selected - 1) % len(options)
                elif e.key in (pygame.K_s, pygame.K_DOWN):
                    selected = (selected + 1) % len(options)
                elif e.key == pygame.K_RETURN:
                    if selected == 0:
                        return  # Почати гру
                    elif selected == 1:
                        pygame.quit()
                        exit()


def heal():
    global health, healing_stones, message
    if healing_stones > 0 and health < max_health:
        healing_stones -= 1
        health = min(max_health, health + 30)
        message = "Ви використали камінь!"
    else:
        message = "Нема чим лікуватися!"

# Основний цикл
show_start_menu()
running = True
while running:
    dt = clock.tick(60)
    screen.blit(backgrounds[cur_loc-1], (0, 0))
    play_location_music(cur_loc - 1)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if in_battle:
                if e.key in (pygame.K_w, pygame.K_UP): menu_i = (menu_i-1) % len(menu)
                elif e.key in (pygame.K_s, pygame.K_DOWN): menu_i = (menu_i+1) % len(menu)
                elif e.key in (pygame.K_a, pygame.K_LEFT): menu_i = (menu_i-1) % len(menu)
                elif e.key in (pygame.K_d, pygame.K_RIGHT): menu_i = (menu_i+1) % len(menu)
                elif e.key == pygame.K_RETURN:
                    if menu_i == 0 and not holding:
                        holding = True
                        hold_timer = 0
                    elif menu_i == 1:
                        flee()
                    elif menu_i == 2:
                        heal()
            else:
                if e.key == pygame.K_SPACE:
                    for r in enemy_pos[cur_loc-1]:
                        if player.colliderect(r):
                            start_attack()
                            cur_enemy = r
                            break
        elif e.type == pygame.KEYUP and in_battle and e.key == pygame.K_RETURN and holding:
            finish_attack()

    if holding:
        hold_timer += dt

    if in_battle and cur_enemy:
        enemy_attack_timer += dt
        if enemy_attack_timer >= enemy_attack_interval:
            damage = random.randint(5, 20)
            health -= damage
            message = f"Ворог атакує! Урон: {damage}"
            enemy_attack_timer = 0
            if health <= 0:
                screen.fill((0,0,0))
                font = pygame.font.SysFont(None, 48)
                msg = font.render("Ви загинули...", True, (255,0,0))
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(4000)
                running = False

    keys = pygame.key.get_pressed()
    moving = False
    dir = RIGHT
    if not in_battle:
        if keys[pygame.K_a]: player.x -= speed; dir = LEFT; moving = True
        if keys[pygame.K_d]: player.x += speed; dir = RIGHT; moving = True
        if keys[pygame.K_w]: player.y -= speed; dir = UP; moving = True
        if keys[pygame.K_s]: player.y += speed; dir = DOWN; moving = True
        if player.top < 0:
            if cur_loc == max_loc:
                show_ending(kills)
                running = False
                break
            cur_loc += 1
            player.bottom = HEIGHT
        if player.bottom > HEIGHT:
            cur_loc = max(1, cur_loc-1)
            player.top = 0

    if moving:
        anim_timer += dt
        if anim_timer > ANIM_SPEED:
            anim_timer = 0
            anim_idx = (anim_idx + 1) % cols
    else:
        anim_idx = 0

    screen.blit(frames[dir][anim_idx], player.topleft)
    for r in enemy_pos[cur_loc-1]:
        img = pygame.transform.scale(pygame.image.load(f"enemy{cur_loc}.png"), (64,64))
        screen.blit(img, r.topleft)

    font = pygame.font.SysFont(None, 36)
    if in_battle:
        pygame.draw.rect(screen, (0,0,0), (50, HEIGHT-150, WIDTH-100, 120))
        for i,opt in enumerate(menu):
            color = (255,255,0) if i==menu_i else (255,255,255)
            screen.blit(font.render(opt, True, color), (100, HEIGHT-140 + i*30))
        if holding:
            held_secs = hold_timer / 1000
            req_secs = req / 1000
            progress = min(1, held_secs / req_secs)
            bar_width = 300
            filled = int(progress * bar_width)
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = HEIGHT - 50
            pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_width, 20), 2)
            pygame.draw.rect(screen, (0,255,0), (bar_x, bar_y, filled, 20))
            timer_text = font.render(f"{held_secs:.2f} / {req_secs:.2f} сек", True, (255,255,255))
            screen.blit(timer_text, (bar_x, bar_y - 30))

    screen.blit(font.render(message, True, (255,255,255)), (20,20))
    screen.blit(font.render(f"HP: {health}", True, (255,0,0)), (WIDTH-150, 20))
    screen.blit(font.render(f"Камені: {healing_stones}", True, (0,255,0)), (WIDTH-300, 20))
    pygame.display.flip()

pygame.quit()
