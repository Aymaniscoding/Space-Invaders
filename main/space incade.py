import pygame
import random
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
black = (0, 0, 0)
white = (255, 255, 255)
background_image = pygame.image.load("Desktop/assets/backg.jpg").convert()
player1_image = pygame.image.load("Desktop/assets/player.png").convert_alpha()
player1_image = pygame.transform.scale(player1_image, (60, 60))
player2_image = pygame.image.load("Desktop/assets/player2.png").convert_alpha()
player2_image = pygame.transform.scale(player2_image, (60, 60))
enemy_image = pygame.image.load("Desktop/assets/enemy.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (40, 40))
bullet_image = pygame.image.load("Desktop/assets/bullet.png").convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (15, 25))
enemy_bullet_image = pygame.image.load("Desktop/assets/enemy_bullet.png").convert_alpha()
enemy_bullet_image = pygame.transform.scale(enemy_bullet_image, (15, 25))
start_screen_image = pygame.image.load("Desktop/assets/Title screen.webp").convert()
start_screen_image = pygame.transform.scale(start_screen_image, (screen_width, screen_height))

class Player(pygame.sprite.Sprite):
    def __init__(self, image, x, y, up_key, down_key, left_key, right_key, shoot_key):
        super(Player, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.up_key = up_key
        self.down_key = down_key
        self.left_key = left_key
        self.right_key = right_key
        self.shoot_key = shoot_key

    def update(self, keys):
        if keys[self.left_key]:
            self.rect.x -= self.speed
        if keys[self.right_key]:
            self.rect.x += self.speed
        if keys[self.up_key]:
            self.rect.y -= self.speed
        if keys[self.down_key]:
            self.rect.y += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, shoot_delay):
        super(Enemy, self).__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = speed
        self.shoot_delay = shoot_delay
        self.shoot_timer = 0

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(1, 3)

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot_timer = 0
            self.shoot_bullet()

    def shoot_bullet(self):
        bullet_speed = 1 + (game_manager.level // 2)
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, 5)
        game_manager.enemy_bullets.add(bullet)
        game_manager.all_sprites.add(bullet)

    def kill(self):
        for bullet in game_manager.enemy_bullets:
            if bullet.rect.centerx == self.rect.centerx:
                bullet.kill()
        super().kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, shooter):
        super(Bullet, self).__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = speed
        self.shooter = shooter  

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super(EnemyBullet, self).__init__()
        self.image = enemy_bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 2 + (game_manager.level // 2)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()

class GameManager:
    def __init__(self, two_player_mode):
        self.two_player_mode = two_player_mode
        self.player1 = Player(player1_image, 3 * (screen_width // 4), screen_height - 50, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE)
        self.players = [self.player1]
        if self.two_player_mode:
            self.player2 = Player(player2_image, screen_width // 4, screen_height - 50, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_x)
            self.players.append(self.player2)

        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player1)
        if self.two_player_mode:
            self.all_sprites.add(self.player2)

        self.scores = [0, 0] 
        self.font = pygame.font.SysFont(None, 55)
        self.level = 1
        self.enemy_speed = 1
        self.enemy_count = 3
        self.enemy_spawn_delay = 120 
        self.enemy_spawn_timer = 0
        self.game_over = False
        self.spawn_enemies()

    def spawn_enemies(self):
        for _ in range(self.enemy_count):
            enemy = Enemy(self.enemy_speed, random.randint(180, 240))
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def handle_event(self, event):
        for player in self.players:
            if event.type == pygame.KEYDOWN:
                if event.key == player.shoot_key and not self.game_over:
                    bullet = Bullet(player.rect.centerx, player.rect.top, 10, player)
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
    
    def update(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()
            for player in self.players:
                player.update(keys)
            self.enemies.update()
            self.bullets.update()
            self.enemy_bullets.update()

            hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
            for bullet, enemies in hits.items():
                shooter = bullet.shooter
                if shooter == self.player1:
                    self.scores[0] += len(enemies)
                elif shooter == self.player2:
                    self.scores[1] += len(enemies)

                self.adjust_difficulty()

           
                for _ in enemies:
                    enemy = Enemy(self.enemy_speed, random.randint(180, 240))
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
            for player in self.players:
                if pygame.sprite.spritecollideany(player, self.enemies):
                    self.game_over = True
                    self.reset_game()

            for player in self.players:
                if pygame.sprite.spritecollideany(player, self.enemy_bullets):
                    self.game_over = True
                    self.reset_game()

       
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_delay:
                self.enemy_spawn_timer = 0
                enemy = Enemy(self.enemy_speed, random.randint(180, 240))
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def adjust_difficulty(self):
        if self.scores[0] >= 10 * self.level:
            self.level += 1
            self.enemy_speed += 0.2
            self.enemy_count += 1
            self.spawn_enemies()

    def draw(self, screen):
        screen.blit(background_image, (0, 0))
        self.all_sprites.draw(screen)

    
        score_text1 = self.font.render(f"Player 1 Score: {self.scores[0]}", True, white)
        screen.blit(score_text1, (10, 10))
        if self.two_player_mode:
            score_text2 = self.font.render(f"Player 2 Score: {self.scores[1]}", True, white)
            screen.blit(score_text2, (screen_width - 300, 10))

       
        level_text = self.font.render(f"Level: {self.level}", True, white)
        screen.blit(level_text, (screen_width // 2 - 50, 10))

       
        if self.game_over:
            game_over_text = self.font.render("Game Over", True, white)
            game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(game_over_text, game_over_rect)

    def reset_game(self):
        self.__init__(self.two_player_mode)

def draw_start_screen(screen):
    screen.blit(start_screen_image, (0, 0))
    font = pygame.font.SysFont(None, 60)
    single_text = font.render("Press 1 for Single Player", True, white)
    two_text = font.render("Press 2 for Two Players", True, white)
    single_rect = single_text.get_rect(center=(screen_width // 2, screen_height - 150))
    two_rect = two_text.get_rect(center=(screen_width // 2, screen_height - 90))
    screen.blit(single_text, single_rect)
    screen.blit(two_text, two_rect)
    
def main():
    global game_manager
    pygame.display.set_caption("Invading Spacers")
    clock = pygame.time.Clock()
    game_manager = None
    running = True
    game_active = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game_active:
                    if event.key == pygame.K_1:
                        game_active = True
                        game_manager = GameManager(two_player_mode=False)  
                    if event.key == pygame.K_2:
                        game_active = True
                        game_manager = GameManager(two_player_mode=True) 
                else:
                    game_manager.handle_event(event)

        if game_active and game_manager:
            game_manager.update()
            screen.fill(black)
            game_manager.draw(screen)
        else:
            draw_start_screen(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()