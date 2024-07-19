import pygame as game
from os.path import join

from random import randint, uniform

class Player(game.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = game.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = game.math.Vector2()
        self.speed = 300

        # cooldown for shooting
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        
        # mask
        self.mask = game.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = game.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = game.key.get_pressed()
        self.direction.x = int(keys[game.K_RIGHT]) - int(keys[game.K_LEFT])
        self.direction.y = int(keys[game.K_DOWN]) - int(keys[game.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        player.rect.center += self.direction * self.speed * dt  # type: ignore

        recent_keys = game.key.get_just_pressed()
        if recent_keys[game.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))  # type: ignore
            self.can_shoot = False
            self.laser_shoot_time = game.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(game.sprite.Sprite):
    def __init__(self, groups, Surf):
        super().__init__(groups)
        self.image = Surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(game.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt  # type: ignore
        if self.rect.bottom < 0:  # type: ignore
            self.kill()

class Meteor(game.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_image = surf
        self.image = self.original_image
        self.rect = self.image.get_frect(center=pos)
        self.start_time = game.time.get_ticks()
        self.lifetime = 3000
        self.direction = game.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        self.rotation = 0
        self.rotation_speed = randint(40, 80)  # make random rotation speed

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt  # type: ignore
        if game.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = game.transform.rotozoom(self.original_image, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center) # type: ignore

class AnimatedExplosion(game.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        explosion_sound.play()
        
        
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global running
    collision_sprites = game.sprite.spritecollide(player, meteor_sprites, True, game.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collision_sprites = game.sprite.spritecollide(laser, meteor_sprites, True)
        if collision_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

def display_score():
    current_time = game.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, '#f0f0f0')
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    game.draw.rect(display_surface, '#f0f0f0', text_rect.inflate(20, 10).move(0, -8), 5, 10)

# general setup
game.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = game.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
game.display.set_caption('Spaceship Game')
running = True
clock = game.time.Clock()

# import
star_surf = game.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = game.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = game.image.load(join('images', 'laser.png')).convert_alpha()
font = game.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [game.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = game.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = game.mixer.Sound(join('audio', 'explosion.wav'))
game_music = game.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play()

# sprites
all_sprites = game.sprite.Group()
meteor_sprites = game.sprite.Group()
laser_sprites = game.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = game.event.custom_type()
game.time.set_timer(meteor_event, 600)

while running:
    dt = clock.tick() / 1000
    # event loop
    for event in game.event.get():
        if event.type == game.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # update the game
    all_sprites.update(dt)
    collisions()

    # draw the game
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    display_score()
    
    game.display.update()

game.quit()
