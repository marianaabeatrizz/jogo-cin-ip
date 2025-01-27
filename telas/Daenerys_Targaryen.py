import pygame
import sys
import random

# Inicializar o Pygame
pygame.init()

# Configurar tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Ano")

# Carregar imagem de fundo
background_image = pygame.image.load('D:/mapa.jpg').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Definir cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.attack_images = [
            pygame.image.load('D:/draca.png').convert_alpha(),
            pygame.image.load('D:/draca.png').convert_alpha()
        ]
        self.image = self.attack_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 2)
        self.speed = 2
        self.max_health = 100
        self.health = self.max_health
        self.is_attacking = False
        self.attack_index = 0
        self.attack_animation_speed = 10
        self.attack_frame_count = 1
        self.inventory = {"Fire Ball": 0, "Ovo": 0}  # Adicionando "Ovo" ao inventário
        self.fireball_cooldown = 500  # Cooldown inicial em milissegundos
        self.fireball_timer = 0  # Temporizador para controle de cooldown
        self.double_shoot = False  # Flag para controle do disparo duplo

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

        # Disparar projéteis somente quando a tecla 'K' é pressionada
        if keys[pygame.K_k]:
            self.shoot()
        
        if keys[pygame.K_a]:
            self.attack()

    def attack(self):
        self.is_attacking = True
        self.attack_frame_count += 1
        if self.attack_frame_count >= self.attack_animation_speed:
            self.attack_frame_count = 0
            self.attack_index += 1
            if self.attack_index >= len(self.attack_images):
                self.attack_index = 0
            self.image = self.attack_images[self.attack_index]
            # Verificar se há colisão com dragões
            dragons_hit = pygame.sprite.spritecollide(self, dragons, False)
            for dragon in dragons_hit:
                dragon.take_damage()
                # Criar item "Fire Ball" quando o dragão é atacado
                create_collectible(dragon.rect.centerx, dragon.rect.bottom, "Fire Ball")
        else:
            self.is_attacking = False

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.fireball_timer >= self.fireball_cooldown:
            if self.double_shoot:
                # Disparar dois projéteis
                fireball1 = FireballAttack(self.rect.right, self.rect.centery - 15, "player")
                fireball2 = FireballAttack(self.rect.right, self.rect.centery + 15, "player")
                fireballs.add(fireball1)
                fireballs.add(fireball2)
                all_sprites.add(fireball1)
                all_sprites.add(fireball2)
            else:
                # Disparar um projétil
                fireball = FireballAttack(self.rect.right, self.rect.centery, "player")
                fireballs.add(fireball)
                all_sprites.add(fireball)
            self.fireball_timer = current_time  # Atualiza o temporizador para o último disparo

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def draw_health_bar(self, screen):
        bar_width = 100
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 20
        health_ratio = self.health / self.max_health
        health_bar_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_bar_width, bar_height))

    def draw_inventory(self, screen):
        font = pygame.font.Font(None, 24)
        text = font.render("Inventário:", True, WHITE)
        screen.blit(text, (10, 10))
        inventory_y = 30
        for item, count in self.inventory.items():
            item_text = font.render(f"{item}: {count}", True, WHITE)
            screen.blit(item_text, (10, inventory_y))
            inventory_y += 20

    def increase_fireball_speed(self):
        # Reduz o tempo de cooldown
        self.fireball_cooldown = max(100, self.fireball_cooldown - 100)  # O cooldown não pode ser menor que 100 ms

    def enable_double_shoot(self):
        # Ativa o disparo duplo
        self.double_shoot = True

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 150))  # Redimensionar para tamanho médio
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1
        self.max_health = 50
        self.health = self.max_health
        self.attack_cooldown = 100
        self.attack_timer = 0
        self.reappearance_delay = 10000  # Tempo de reaparecimento em milissegundos
        self.reappearance_timer = 0
        self.is_reappearing = False

    def update(self):
        # Recolocar o dragão se sair da tela
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

        # Mover e atacar
        self.rect.x -= self.speed
        self.attack_timer += 1
        if self.attack_timer >= self.attack_cooldown:
            self.attack()
            self.attack_timer = 0

    def attack(self):
        fireball = FireballAttack(self.rect.centerx - 20, self.rect.centery, "enemy")
        fireballs.add(fireball)
        all_sprites.add(fireball)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def draw_health_bar(self, screen):
        bar_width = 100
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 20
        health_ratio = self.health / self.max_health
        health_bar_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_bar_width, bar_height))

    def take_damage(self):
        self.health -= 10
        if self.health <= 0:
            self.kill()
            # Criar item "Fire Ball" quando o dragão é derrotado
            create_collectible(self.rect.centerx, self.rect.bottom, "Fire Ball")
            # Não removemos o dragão do grupo; ele só irá reaparecer na tela
            self.health = self.max_health
            self.rect.center = (WIDTH - 100, random.randint(50, HEIGHT - 50))

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        if item_type == "Fire Ball":
            try:
                self.image = pygame.image.load('D:/colecio.png').convert_alpha()
                self.image = pygame.transform.scale(self.image, (30, 30))
            except pygame.error as e:
                print(f"Erro ao carregar a imagem 'colecio.png': {e}")
                self.image = pygame.Surface((30, 30))
                self.image.fill(RED)
        elif item_type == "Ovo":
            try:
                self.image = pygame.image.load('D:/ovo.png').convert_alpha()
                self.image = pygame.transform.scale(self.image, (30, 30))
            except pygame.error as e:
                print(f"Erro ao carregar a imagem 'ovo.png': {e}")
                self.image = pygame.Surface((30, 30))
                self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.time_to_live = 5000
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.time_to_live:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class FireballAttack(pygame.sprite.Sprite):
    def __init__(self, x, y, source):
        super().__init__()
        self.source = source
        try:
            self.image = pygame.image.load('D:/ball_fire_attack.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except pygame.error as e:
            print(f"Erro ao carregar a imagem 'fireball.png': {e}")
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5  # Reduzido a velocidade dos projéteis

    def update(self):
        if self.source == "player":
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def create_collectible(x, y, item_type):
    collectible = Collectible(x, y, item_type)
    collectibles.add(collectible)
    all_sprites.add(collectible)

def show_game_over(screen):
    font = pygame.font.Font(None, 36)
    text = font.render("Fim de Jogo", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

player = Player()

dragon1 = Enemy('D:/dragao.png', WIDTH - 100, HEIGHT // 2)
dragon2 = Enemy('D:/dragao2.png', WIDTH - 100, random.randint(50, HEIGHT - 50))

dragons = pygame.sprite.Group()
dragons.add(dragon1, dragon2)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(dragon1)
all_sprites.add(dragon2)

collectibles = pygame.sprite.Group()
fireballs = pygame.sprite.Group()

# Criar item "Ovo" no início do jogo
create_collectible(WIDTH // 2, HEIGHT // 2, "Ovo")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    collected_items = pygame.sprite.spritecollide(player, collectibles, True)
    for item in collected_items:
        if isinstance(item, Collectible):
            if item.image.get_at((0, 0)) != RED:  # Corrigido para permitir coleta se a cor não for RED
                if item.image.get_at((0, 0)) == BLUE:
                    player.increase_fireball_speed()  # Aumenta a velocidade do disparo
                else:
                    player.inventory["Fire Ball"] += 1
                    if player.inventory["Ovo"] == 0:
                        player.enable_double_shoot()  # Habilita o disparo duplo após pegar o item "Ovo"
                        player.inventory["Ovo"] += 1  # Atualiza o inventário para refletir a coleta do item

    # Verificar colisões entre projéteis e inimigos
    for fireball in fireballs.copy():
        if fireball.source == "player":
            dragons_hit = pygame.sprite.spritecollide(fireball, dragons, False)
            for dragon in dragons_hit:
                dragon.take_damage()
                fireball.kill()
        elif fireball.source == "enemy":
            if pygame.sprite.collide_rect(player, fireball):
                player.health -= 5
                fireball.kill()

    # Verificar se o jogador morreu
    if player.health <= 0:
        show_game_over(screen)
        pygame.display.flip()
        pygame.time.delay(2000)
        running = False

    # Atualizar e desenhar
    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)
    player.draw_health_bar(screen)
    player.draw_inventory(screen)
    for dragon in dragons:
        dragon.draw_health_bar(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
