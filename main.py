import pygame
import random
pygame.init()

Width, Height = 800, 600
screen = pygame.display.set_mode((Width, Height))
clock = pygame.time.Clock()


red = (255, 0, 0)
green = (0, 255, 0)


class Player:
    def __init__(self):
        self.x = Width // 2
        self.y = Height // 2
        self.speed = 4
        self.direction = "down"
        self.hp = 100

    def move(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
            self.direction = "up"
        if keys[pygame.K_s]:
            self.y += self.speed
            self.direction = "down"
        if keys[pygame.K_a]:
            self.x -= self.speed
            self.direction = "left"
        if keys[pygame.K_d]:
            self.x += self.speed
            self.direction = "right"

    def attack(self, enemies_in_room):
        for enemy in enemies_in_room:
            if self.direction == "up" and enemy.y < self.y and abs(enemy.x - self.x) < 30:
                enemy.hp -= 20
            if self.direction == "down" and enemy.y > self.y and abs(enemy.x - self.x) < 30:
                enemy.hp -= 20
            if self.direction == "left" and enemy.x < self.x and abs(enemy.y - self.y) < 30:
                enemy.hp -= 20
            if self.direction == "right" and enemy.x > self.x and abs(enemy.y - self.y) < 30:
                enemy.hp -= 20

    def draw(self):
        pygame.draw.rect(screen, red, (self.x, self.y, 20, 20))


class Enemy:
    def __init__(self):
        self.x = random.randint(100, Width-100)
        self.y = random.randint(100, Height-100)
        self.hp = 40

    def update(self, player_character):
        dx = player_character.x - self.x
        dy = player_character.y - self.y
        distance = max(1, (dx**2 + dy**2)**0.5)
        self.x += dx / distance * 1.5
        self.y += dy / distance * 1.5

    def draw(self):
        pygame.draw.circle(screen, (200, 0, 0), (int(self.x), int(self.y)), 10)
        pygame.draw.rect(screen, (0, 200, 0), (self.x - 10, self.y - 20, 20 * (self.hp / 40), 4))


class Room:
    def __init__(self, room_type):
        self.type = room_type
        self.enemies_in_room = []
        if room_type == "enemy":
            for _ in range(random.randint(1,3)):
                self.enemies_in_room.append(Enemy())

    def update(self, player_character):
        for enemy in self.enemies_in_room:
            enemy.update(player_character)
        self.enemies_in_room = [enemy for enemy in self.enemies_in_room if enemy.hp > 0]

    def draw(self):
        screen.fill((34, 139, 34))
        for enemy in self.enemies_in_room:
            enemy.draw()



rooms_list = []
for _ in range(random.randint(5,6)):
    rooms_list.append(Room(random.choice(["enemy","empty"])))

current_room_index = 0
player_character = Player()

running = True
while running:
    keys_pressed = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if rooms_list[current_room_index].enemies_in_room:
                    player_character.attack(rooms_list[current_room_index].enemies_in_room)

    player_character.move(keys_pressed)
    rooms_list[current_room_index].update(player_character)

    rooms_list[current_room_index].draw()
    player_character.draw()


    if keys_pressed[pygame.K_RIGHT] and current_room_index < len(rooms_list)-1:
        current_room_index += 1
        player_character.x = 50
        player_character.y = Height // 2
    if keys_pressed[pygame.K_LEFT] and current_room_index > 0:
        current_room_index -= 1
        player_character.x = Width - 70
        player_character.y = Height // 2


    pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 10))
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, player_character.hp, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()