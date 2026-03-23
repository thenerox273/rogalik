import pygame, random, os, math


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skeleton Dungeon")
clock = pygame.time.Clock()

PLAYER_SIZE = 32
BOX_SIZE = 48
SWORD_WIDTH, SWORD_HEIGHT = 60, 15
EXCALIBUR_WIDTH, EXCALIBUR_HEIGHT = 110, 30
ROOM_W, ROOM_H = 700, 500
OX, OY = (WIDTH - ROOM_W) // 2, (HEIGHT - ROOM_H) // 2


LEFT, RIGHT = OX + 25, OX + ROOM_W - 25
TOP, BOTTOM = OY + 25, OY + ROOM_H - 25


def start_background_music(filename):
    if os.path.exists(filename):
        try:
            pygame.mixer.music.load(filename)

            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            print(f"Аудио: {filename} успешно запущено.")
        except pygame.error as e:
            print(f"Ошибка воспроизведения музыки: {e}")
    else:
        print(f"Предупреждение: Файл {filename} не найден в папке проекта.")



start_background_music("CriticalTheme.mp3")

def load(name, size=None):
    if os.path.exists(name):
        try:
            img = pygame.image.load(name).convert_alpha()
            if size:
                return pygame.transform.scale(img, size)
            return img
        except:
            pass


    fallback_surface = pygame.Surface(size if size else (32, 32))
    fallback_surface.fill((255, 0, 255))
    return fallback_surface



skeleton_idle = load("Idle.png")
skeleton_attack = load("attack.png")
skeleton_walk = load("walk.png")

player_frames = [
    load("main1.png", (22, 42)),
    load("main2.png", (24, 42))
]

ranged_frames = [
    load("ranged_1.png", (32, 32)),
    load("ranged_2.png", (32, 32))
]

room_img = load("room.png", (700, 500))
door_img = load("door.png", (60, 100))
sword_img = load("sword.png", (SWORD_WIDTH, SWORD_HEIGHT))
excalibur_img = load("excalibur.png", (EXCALIBUR_WIDTH, EXCALIBUR_HEIGHT))
staff_img = load("firestaff.png", (14, 60))
portal_img = load("portal.png", (50, 70))
pressE = load("pressEbutton.png", (32, 32))
box_img = load("box.png", (48, 48))
fireball_img = load("fireball.png", (16, 16))
closed_chest = load("closedchest.png", (48, 48))
open_chest = load("openchest.png", (48, 48))
Bigslime_img = load("Bigslime.png", (96, 64))
small_pot = load("smallhealthpotion.png", (8, 16))
big_pot = load("healthpotion.png", (16, 16))
font = pygame.font.SysFont("arial", 18, bold=True)



class Particle:

    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 20
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.life // 5)


class Player:

    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.hp = 10
        self.dir = 'right'
        self.weapon = 'sword'
        self.cd = 0
        self.atk_timer = 0
        self.shake = 0
        self.speed = 4
        self.anim_timer = 0
        self.frame = 0
        self.moving = False

    def rect(self):
        return pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)

    def move(self, keys, boxes):
        ox, oy = self.x, self.y
        self.moving = False
        if keys[pygame.K_w]:
            self.y -= self.speed;
            self.dir = 'up';
            self.moving = True
        elif keys[pygame.K_s]:
            self.y += self.speed;
            self.dir = 'down';
            self.moving = True

        if keys[pygame.K_a]:
            self.x -= self.speed;
            self.dir = 'left';
            self.moving = True
        elif keys[pygame.K_d]:
            self.x += self.speed;
            self.dir = 'right';
            self.moving = True


        if self.x < LEFT or self.x + PLAYER_SIZE > RIGHT or self.y < TOP or self.y + PLAYER_SIZE > BOTTOM:
            self.x, self.y = ox, oy

        for b in boxes:
            if self.rect().colliderect(b):
                self.x, self.y = ox, oy

        if self.moving:
            self.anim_timer += 1
            if self.anim_timer > 10:
                self.frame = (self.frame + 1) % 2
                self.anim_timer = 0
        else:
            self.frame = 0


class Enemy:

    def __init__(self, t, x, y):
        self.t, self.x, self.y = t, x, y
        self.hp = 8 if t == 'big' else 4
        self.kx, self.ky = 0, 0
        self.shoot_cd = random.randint(60, 120)
        self.w, self.h = (96, 64) if t == 'big' else (35, 44) if t == 'melee' else (32, 32)
        self.anim_timer = 0
        self.frame = 0
        self.flip = False
        self.state = 'idle'
        self.atk_cooldown = 0
        self.is_moving = False

    def rect(self):
        r = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.t == 'melee': return r.inflate(-12, -4)
        return r

    def update(self, player, bullets, boxes, enemies):
        self.anim_timer += 1
        if self.atk_cooldown > 0: self.atk_cooldown -= 1

        self.flip = player.x > self.x

        for other in enemies:
            if other != self:
                if self.rect().colliderect(other.rect()):
                    dist = math.hypot(self.x - other.x, self.y - other.y)
                    if dist == 0: dist = 1
                    self.x += (self.x - other.x) / dist * 1.5
                    self.y += (self.y - other.y) / dist * 1.5


        if self.t == 'ranged':
            if self.anim_timer > 10:
                self.frame = (self.frame + 1) % 2
                self.anim_timer = 0
        elif self.t == 'melee':
            if self.atk_cooldown > 45:
                self.state = 'attack'
            elif abs(self.kx) > 0.2 or abs(self.ky) > 0.2 or self.is_moving:
                self.state = 'walk' if (self.anim_timer // 12) % 2 == 0 else 'idle'
            else:
                self.state = 'idle'


        ox, oy = self.x, self.y
        if abs(self.kx) > 0.1 or abs(self.ky) > 0.1:
            self.x += self.kx
            self.y += self.ky
            if self.x < LEFT or self.x + self.w > RIGHT or any(self.rect().colliderect(b) for b in boxes):
                self.x = ox
            if self.y < TOP or self.y + self.h > BOTTOM or any(self.rect().colliderect(b) for b in boxes):
                self.y = oy
            self.kx *= 0.8;
            self.ky *= 0.8
            return

        dx, dy = player.x - self.x, player.y - self.y
        dist = math.hypot(dx, dy)
        spd = 0.8 if self.t == 'big' else 1.4
        self.is_moving = False

        if self.t in ['melee', 'big']:
            if dist > 10:
                self.is_moving = True
                nx, ny = self.x + (dx / dist * spd), self.y + (dy / dist * spd)
                old_x, old_y = self.x, self.y
                self.x = nx
                if self.x < LEFT or self.x + self.w > RIGHT or any(self.rect().colliderect(b) for b in boxes):
                    self.x = old_x
                self.y = ny
                if self.y < TOP or self.y + self.h > BOTTOM or any(self.rect().colliderect(b) for b in boxes):
                    self.y = old_y


            if self.rect().colliderect(player.rect()) and self.atk_cooldown == 0:
                player.hp -= 1
                player.shake = 8
                self.kx, self.ky = -dx / dist * 14, -dy / dist * 14
                self.atk_cooldown = 65

        elif self.t == 'ranged':
            if dist < 220:
                old_rx, old_ry = self.x, self.y
                self.x -= (dx / dist * 1.2)
                self.y -= (dy / dist * 1.2)
                if self.x < LEFT or self.x + self.w > RIGHT or any(self.rect().colliderect(b) for b in boxes):
                    self.x = old_rx
                if self.y < TOP or self.y + self.h > BOTTOM or any(self.rect().colliderect(b) for b in boxes):
                    self.y = old_ry

            self.shoot_cd -= 1
            if self.shoot_cd <= 0:
                bullets.append(
                    {'pos': [self.x + 16, self.y + 16], 'vel': [dx / dist * 4.5, dy / dist * 4.5], 'owner': 'enemy',
                     'trail': []})
                self.shoot_cd = 130


class Room:

    def __init__(self, rtype, level):
        self.type = rtype
        self.enemies, self.boxes, self.bullets, self.loots, self.particles = [], [], [], [], []
        self.cleared = rtype in ['start', 'chest', 'portal']
        self.opened = False
        self.chest_rect = pygame.Rect(WIDTH // 2 - 24, HEIGHT // 2 - 24, 48, 48)

        if rtype == 'enemy':
            for _ in range(random.randint(2, 4)):
                for _ in range(30):
                    nb = pygame.Rect(random.randint(LEFT + 100, RIGHT - 140), random.randint(TOP + 100, BOTTOM - 140),
                                     BOX_SIZE, BOX_SIZE)
                    if not any(nb.inflate(50, 50).colliderect(b) for b in self.boxes):
                        self.boxes.append(nb);
                        break

            power = 3 + level
            while power > 0:
                et = random.choices(['melee', 'ranged', 'big'], [55, 30, 15])[0]
                cost = {'melee': 1, 'ranged': 2, 'big': 3}[et]
                if power >= cost:
                    ex, ey = random.randint(LEFT + 60, RIGHT - 100), random.randint(TOP + 60, BOTTOM - 100)
                    en = Enemy(et, ex, ey)
                    if not any(en.rect().colliderect(b) for b in self.boxes):
                        self.enemies.append(en);
                        power -= cost
                else:
                    break


class Game:

    def __init__(self):
        self.player = Player()
        self.level = 1
        self.gen_map()

    def gen_map(self):
        n = 5 + random.randint(0, 2)
        self.map, self.pos = {(0, 0): Room('start', self.level)}, (0, 0)
        positions, curr = [(0, 0)], [0, 0]

        for _ in range(n):
            d = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            np = (curr[0] + d[0], curr[1] + d[1])
            if np not in self.map:
                self.map[np] = None
                positions.append(np)
                curr = list(np)

        portal = max(positions, key=lambda p: abs(p[0]) + abs(p[1]))
        self.map[portal] = Room('portal', self.level)
        positions.remove(portal)
        if (0, 0) in positions: positions.remove((0, 0))

        chest = random.choice(positions)
        self.map[chest] = Room('chest', self.level)
        positions.remove(chest)

        for p in positions:
            self.map[p] = Room('enemy', self.level)

    def update(self):
        if self.player.hp <= 0:
            if pygame.key.get_pressed()[pygame.K_r]: self.__init__()
            return

        r = self.map[self.pos]
        keys = pygame.key.get_pressed()
        self.player.move(keys, r.boxes)

        if self.player.cd > 0: self.player.cd -= 1
        if self.player.atk_timer > 0: self.player.atk_timer -= 1
        if self.player.shake > 0: self.player.shake -= 1

        if keys[pygame.K_SPACE] and self.player.cd == 0:
            if self.player.weapon != 'staff':
                dmg = 3.5 if self.player.weapon == 'excalibur' else 1.2
                self.player.cd, self.player.atk_timer = (20, 14) if dmg > 2 else (24, 11)
                atk_r = self.get_atk_rect()
                for e in r.enemies:
                    if atk_r.colliderect(e.rect()):
                        e.hp -= dmg
                        dist = math.hypot(e.x - self.player.x, e.y - self.player.y)
                        e.kx, e.ky = (e.x - self.player.x) / max(1, dist) * 16, (e.y - self.player.y) / max(1,
                                                                                                            dist) * 16
            else:
                self.player.cd = 28
                vx = 7.5 if self.player.dir == 'right' else -7.5 if self.player.dir == 'left' else 0
                vy = 7.5 if self.player.dir == 'down' else -7.5 if self.player.dir == 'up' else 0
                if vx == 0 and vy == 0: vx = 7.5
                r.bullets.append(
                    {'pos': [self.player.x + 12, self.player.y + 12], 'vel': [vx, vy], 'owner': 'player', 'trail': []})


        for e in r.enemies: e.update(self.player, r.bullets, r.boxes, r.enemies)
        r.enemies = [e for e in r.enemies if e.hp > 0]
        for p in r.particles: p.update()
        r.particles = [p for p in r.particles if p.life > 0]

        if not r.enemies and r.type == 'enemy': r.cleared = True

        for b in r.bullets[:]:
            b['trail'].append(list(b['pos']))
            if len(b['trail']) > 6: b['trail'].pop(0)
            b['pos'][0] += b['vel'][0]
            b['pos'][1] += b['vel'][1]
            br = pygame.Rect(b['pos'][0], b['pos'][1], 16, 16)


            hit_box = False
            for box in r.boxes:
                if br.colliderect(box):
                    hit_box = True;
                    break

            if hit_box:
                for _ in range(5): r.particles.append(Particle(b['pos'][0], b['pos'][1], (255, 100, 0)))
                r.bullets.remove(b);
                continue

            if b['owner'] == 'enemy' and br.colliderect(self.player.rect()):
                self.player.hp -= 1;
                self.player.shake = 10;
                r.bullets.remove(b)
            elif b['owner'] == 'player':
                for e in r.enemies:
                    if br.colliderect(e.rect()):
                        e.hp -= 1.1;
                        e.kx, e.ky = b['vel'][0] * 1.3, b['vel'][1] * 1.3
                        if b in r.bullets: r.bullets.remove(b); break

            if b in r.bullets and not (LEFT - 50 < b['pos'][0] < RIGHT + 50 and TOP - 50 < b['pos'][1] < BOTTOM + 50):
                r.bullets.remove(b)

        if keys[pygame.K_e]:
            if r.type == 'chest' and not r.opened and self.player.rect().colliderect(r.chest_rect):
                r.opened = True
                t = random.choices(['excalibur', 'staff', 'big_pot', 'small_pot'], [0.1, 0.2, 0.3, 0.4])[0]
                r.loots.append(
                    {'rect': pygame.Rect(r.chest_rect.centerx - 16, r.chest_rect.bottom + 10, 32, 32), 'type': t})

            for l in r.loots[:]:
                if self.player.rect().colliderect(l['rect']):
                    if 'pot' in l['type']:
                        self.player.hp = min(10, self.player.hp + (6 if l['type'] == 'big_pot' else 3))
                        r.loots.remove(l)
                    else:
                        self.player.weapon, l['type'] = l['type'], self.player.weapon
                        break

            if r.type == 'portal' and self.player.rect().colliderect(
                    pygame.Rect(WIDTH // 2 - 25, HEIGHT // 2 - 35, 50, 70)):
                self.level += 1;
                self.gen_map();
                self.player.x, self.player.y = WIDTH // 2, HEIGHT // 2

        if r.cleared:
            cx, cy = WIDTH // 2, HEIGHT // 2
            for dx, dy, side, nx, ny in [(-1, 0, 'l', RIGHT - 80, cy - 16), (1, 0, 'r', LEFT + 50, cy - 16),
                                         (0, -1, 'u', cx - 16, BOTTOM - 80), (0, 1, 'd', cx - 16, TOP + 50)]:
                if (self.pos[0] + dx, self.pos[1] + dy) in self.map:
                    gate = pygame.Rect(LEFT - 45 if side == 'l' else RIGHT - 5 if side == 'r' else cx - 50,
                                       cy - 50 if side in 'lr' else TOP - 45 if side == 'u' else BOTTOM - 5,
                                       50 if side in 'lr' else 100, 100 if side in 'lr' else 50)
                    if self.player.rect().colliderect(gate):
                        self.pos = (self.pos[0] + dx, self.pos[1] + dy)
                        self.player.x, self.player.y = nx, ny;
                        break

    def get_atk_rect(self):
        c = self.player.rect().center
        w, h = (EXCALIBUR_WIDTH, EXCALIBUR_HEIGHT) if self.player.weapon == 'excalibur' else (SWORD_WIDTH, SWORD_HEIGHT)
        if self.player.dir == 'right': return pygame.Rect(c[0] + 10, c[1] - h // 2, w, h)
        if self.player.dir == 'left': return pygame.Rect(c[0] - 10 - w, c[1] - h // 2, w, h)
        if self.player.dir == 'up': return pygame.Rect(c[0] - h // 2, c[1] - 10 - w, h, w)
        return pygame.Rect(c[0] - h // 2, c[1] + 10, h, w)

    def draw(self):
        if self.player.hp <= 0:
            screen.fill((20, 5, 5))
            screen.blit(font.render("ВЫ ПАЛИ В БОЮ. НАЖМИТЕ R ДЛЯ ВОЗРОЖДЕНИЯ", 1, (255, 50, 50)),
                        (WIDTH // 2 - 180, HEIGHT // 2))
            pygame.display.flip();
            return

        canv = pygame.Surface((WIDTH, HEIGHT))
        canv.blit(room_img, (OX, OY))
        r = self.map[self.pos]
        for b in r.boxes: canv.blit(box_img, b)
        for p in r.particles: p.draw(canv)

        for e in r.enemies:
            if e.t == 'big':
                canv.blit(Bigslime_img, (e.x, e.y))
            elif e.t == 'ranged':
                canv.blit(ranged_frames[e.frame], (e.x, e.y))
            elif e.t == 'melee':
                img = skeleton_idle
                if e.state == 'attack':
                    img = skeleton_attack
                elif e.state == 'walk':
                    img = skeleton_walk
                if e.flip: img = pygame.transform.flip(img, 1, 0)
                canv.blit(img, (e.x + (35 - img.get_width()) // 2, e.y))
            pygame.draw.rect(canv, (255, 0, 0), (e.x, e.y - 10, int(e.w * (e.hp / (8 if e.t == 'big' else 4))), 5))

        for b in r.bullets:
            for i, p in enumerate(b['trail']):
                pygame.draw.circle(canv, (255, 150, 0) if b['owner'] == 'player' else (180, 50, 255),
                                   (int(p[0] + 8), int(p[1] + 8)), i + 1)
            canv.blit(fireball_img, b['pos'])


        if r.type == 'chest': canv.blit(open_chest if r.opened else closed_chest, r.chest_rect)
        if r.type == 'portal': canv.blit(portal_img, (WIDTH // 2 - 25, HEIGHT // 2 - 35))


        for l in r.loots:
            img = small_pot if l['type'] == 'small_pot' else big_pot
            if 'pot' not in l['type']:
                img = pygame.transform.scale(
                    excalibur_img if l['type'] == 'excalibur' else staff_img if l['type'] == 'staff' else sword_img,
                    (32, 16) if l['type'] != 'staff' else (10, 32))
            canv.blit(img, l['rect'])
            if self.player.rect().colliderect(l['rect'].inflate(20, 20)):
                canv.blit(pressE, (l['rect'].x, l['rect'].y - 30))


        if r.cleared:
            cx, cy = WIDTH // 2, HEIGHT // 2
            if (self.pos[0] - 1, self.pos[1]) in self.map: canv.blit(door_img, (LEFT - 45, cy - 50))
            if (self.pos[0] + 1, self.pos[1]) in self.map: canv.blit(pygame.transform.flip(door_img, 1, 0),
                                                                     (RIGHT - 15, cy - 50))
            if (self.pos[0], self.pos[1] - 1) in self.map: canv.blit(pygame.transform.rotate(door_img, -90),
                                                                     (cx - 50, TOP - 45))
            if (self.pos[0], self.pos[1] + 1) in self.map: canv.blit(pygame.transform.rotate(door_img, 90),
                                                                     (cx - 50, BOTTOM - 15))

        if self.player.weapon in ['sword', 'excalibur'] and self.player.atk_timer > 0:
            wimg = excalibur_img if self.player.weapon == 'excalibur' else sword_img
            if self.player.dir == 'left':
                wimg = pygame.transform.flip(wimg, 1, 0)
            elif self.player.dir == 'up':
                wimg = pygame.transform.rotate(wimg, 90)
            elif self.player.dir == 'down':
                wimg = pygame.transform.rotate(wimg, -90)
            canv.blit(wimg, self.get_atk_rect())
        elif self.player.weapon == 'staff':
            canv.blit(staff_img, (self.player.x + 22, self.player.y - 35))


        img = player_frames[self.player.frame]


        if self.player.dir == 'left':
            img = player_frames[self.player.frame]
        elif self.player.dir == 'right':
            img = pygame.transform.flip(player_frames[self.player.frame], True, False)
        canv.blit(img, (self.player.x, self.player.y))
        pygame.draw.rect(canv, (50, 50, 50), (18, 18, 154, 19))
        pygame.draw.rect(canv, (200, 0, 0), (20, 20, self.player.hp * 15, 15))
        screen.blit(font.render(f"LEVEL: {self.level} | ROOM: {self.pos}", 1, (255, 255, 255)), (20, 45))

        mx, my, ms = WIDTH - 120, 20, 12
        for p in self.map:
            c = (255, 255, 255) if p == self.pos else (0, 200, 100) if self.map[p].cleared else (100, 0, 0)
            pygame.draw.rect(canv, c, (mx + p[0] * ms, my + p[1] * ms, ms - 2, ms - 2))

        shake_offset = (random.randint(-self.player.shake, self.player.shake),
                        random.randint(-self.player.shake, self.player.shake))
        screen.fill((0, 0, 0))
        screen.blit(canv, shake_offset)
        pygame.display.flip()

def menu():
    music_on = True

    play_btn = pygame.Rect(WIDTH//2 - 100, 260, 200, 50)
    music_btn = pygame.Rect(WIDTH//2 - 100, 330, 200, 50)
    exit_btn = pygame.Rect(WIDTH//2 - 100, 400, 200, 50)

    while True:
        screen.fill((15, 15, 20))

        mouse = pygame.mouse.get_pos()
        title = pygame.font.SysFont("arial", 40, bold=True)
        screen.blit(title.render("Skeleton Dungeon", True, (255,255,255)), (WIDTH//2 - 190, 150))

        def draw_btn(rect, text):
            color = (80, 80, 90) if rect.collidepoint(mouse) else (60, 60, 70)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            screen.blit(font.render(text, True, (255,255,255)), (rect.x + 50, rect.y + 15))

        draw_btn(play_btn, "PLAY")
        draw_btn(music_btn, f"MUSIC: {'ON' if music_on else 'OFF'}")
        draw_btn(exit_btn, "EXIT")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(mouse):
                    return

                if music_btn.collidepoint(mouse):
                    music_on = not music_on
                    if music_on:
                        start_background_music("CriticalTheme.mp3")
                    else:
                        pygame.mixer.music.stop()

                if exit_btn.collidepoint(mouse):
                    pygame.quit(); exit()
menu()
game_instance = Game()
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    game_instance.update()
    game_instance.draw()

    clock.tick(60)

