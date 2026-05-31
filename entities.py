import pygame
import random
import math
from constants import *

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

class Particle:
    def __init__(self, x, y, color, count=1):
        self.parts = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(60, 200)
            self.parts.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * spd,
                "vy": math.sin(angle) * spd,
                "life": random.uniform(0.2, 0.6),
                "max_life": random.uniform(0.2, 0.6),
                "color": color,
                "size": random.randint(2, 5),
            })

    def update(self, dt):
        for p in self.parts:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt

    def draw(self, screen, shake=(0, 0)):
        sx, sy = shake
        for p in self.parts:
            if p["life"] <= 0:
                continue
            f = p["life"] / p["max_life"]
            c = tuple(max(0, min(255, int(v * f))) for v in p["color"])
            pygame.draw.rect(screen, c,
                (int(p["x"] + sx), int(p["y"] + sy), p["size"], p["size"]))

    @property
    def dead(self):
        return all(p["life"] <= 0 for p in self.parts)

class Food:
    def __init__(self, snakes, obstacles=[]):
        self.obstacles = obstacles
        # snakes pode ser uma lista de cobras ou uma única cobra (para compatibilidade)
        self.snakes = snakes if isinstance(snakes, list) else [snakes]
        self.pos = self._find_spot()
        self.ftype = NORMAL
        if random.random() < 0.2:
            self.ftype = random.choice([GOLDEN, ICE, SHRINK, SPEED])

    def _find_spot(self):
        while True:
            p = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            in_any_snake = any(p in s for s in self.snakes)
            if not in_any_snake and p not in self.obstacles:
                return p

    def draw(self, screen, t, shake=(0, 0)):
        sx, sy = shake
        x, y = self.pos
        cx = x * CELL + CELL // 2 + sx
        cy = y * CELL + CELL // 2 + sy
        color = FOOD_COLORS[self.ftype]
        pulse = abs(math.sin(t * 3)) * 3
        r = CELL // 2 - 4 + int(pulse)
        pygame.draw.circle(screen, color, (cx, cy), r)
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), r * 3 // 5)
        if self.ftype != NORMAL:
            ring = abs(math.sin(t * 5)) * 4 + 2
            pygame.draw.circle(screen, (255, 255, 200), (cx, cy), r + int(ring), 2)

class Portal:
    def __init__(self, pos_a, pos_b):
        self.pos_a = pos_a
        self.pos_b = pos_b

    def draw(self, screen, t, shake=(0, 0)):
        sx, sy = shake
        for pos, color in [(self.pos_a, PORTAL_COLOR_A), (self.pos_b, PORTAL_COLOR_B)]:
            cx = pos[0] * CELL + CELL // 2 + sx
            cy = pos[1] * CELL + CELL // 2 + sy
            
            # Efeito de espiral/pulso
            for r_off in range(3):
                r = (CELL // 2 - 2) - r_off * 4
                pulse = abs(math.sin(t * 8 - r_off)) * 5
                pygame.draw.circle(screen, color, (cx, cy), max(2, int(r + pulse)), 2)
            
            # Brilho central
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 4)

    def get_exit(self, pos):
        if pos == self.pos_a: return self.pos_b
        if pos == self.pos_b: return self.pos_a
        return None

class Snake:
    def __init__(self, head_color=SNAKE_HEAD, tail_color=SNAKE_TAIL, 
                 start_pos=None, start_dir=RIGHT, key_map=DIR_KEYS):
        if start_pos is None:
            start_pos = (COLS // 2, ROWS // 2)
        
        self.body = [start_pos, (start_pos[0] - start_dir[0], start_pos[1] - start_dir[1]), 
                     (start_pos[0] - 2*start_dir[0], start_pos[1] - 2*start_dir[1])]
        self.body_set = set(self.body)
        self.direction = start_dir
        self.next_dir = start_dir
        self.head_color = head_color
        self.tail_color = tail_color
        self.key_map = key_map
        self.fever_timer = 0

    def handle_input(self, key):
        if key in self.key_map:
            d = self.key_map[key]
            if d != OPPOSITE[self.direction]:
                self.next_dir = d

    def update(self, wrap_mode):
        self.direction = self.next_dir
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if wrap_mode:
            new_head = (new_head[0] % COLS, new_head[1] % ROWS)

        self.body.insert(0, new_head)
        self.body_set.add(new_head)
        return new_head

    def pop_tail(self):
        if len(self.body) > 1:
            tail = self.body.pop()
            if tail not in self.body:
                self.body_set.remove(tail)

    def check_collision(self, wrap_mode):
        head = self.body[0]
        if not wrap_mode:
            if (head[0] < 0 or head[0] >= COLS or
                head[1] < 0 or head[1] >= ROWS):
                return True
        
        # Invencibilidade parcial no Modo Fever: ignora colisão com o próprio corpo
        if self.fever_timer <= 0:
            if self.body.count(head) > 1:
                return True
        return False

    def draw(self, screen, shake=(0, 0)):
        sx, sy = shake
        n = len(self.body)
        t = pygame.time.get_ticks() / 1000
        
        # Efeito de brilho no Modo Fever
        is_fever = self.fever_timer > 0
        glow = abs(math.sin(t * 15)) if is_fever else 0
        
        for i, (x, y) in enumerate(self.body):
            rect = (x * CELL + 2 + sx, y * CELL + 2 + sy, CELL - 4, CELL - 4)
            if n == 1:
                base_color = self.head_color
            else:
                base_color = lerp_color(self.head_color, self.tail_color, i / (n - 1))
            
            if is_fever:
                color = lerp_color(base_color, FEVER_COLOR_GLOW, glow)
            else:
                color = base_color
                
            pygame.draw.rect(screen, color, rect, border_radius=SNAKE_BORDER_RADIUS)
            
            if i == 0:
                head_border = (200, 255, 220) if not is_fever else FEVER_COLOR_GLOW
                pygame.draw.rect(screen, head_border, rect, 2, border_radius=SNAKE_BORDER_RADIUS)
                cx, cy = x * CELL + CELL // 2 + sx, y * CELL + CELL // 2 + sy
                for ex, ey in [(-1, -1), (1, -1)]:
                    ex_final, ey_final = ex, ey
                    if self.direction == RIGHT: ex_final, ey_final = 1, ex
                    elif self.direction == LEFT: ex_final, ey_final = -1, ex
                    elif self.direction == DOWN: ex_final, ey_final = -ex, 1
                    pygame.draw.circle(screen, (0, 0, 0),
                        (cx + ex_final * SNAKE_EYE_OFFSET, cy + ey_final * SNAKE_EYE_OFFSET), SNAKE_EYE_SIZE)

    def __contains__(self, item):
        return item in self.body_set

    def __len__(self):
        return len(self.body)

class EnemySnake(Snake):
    def decide_direction(self, food_pos, obstacles, all_snakes, wrap_mode):
        head = self.body[0]
        possible_dirs = [UP, DOWN, LEFT, RIGHT]
        valid_dirs = []

        # 1. Filtrar movimentos que não causam morte imediata
        for d in possible_dirs:
            if d == OPPOSITE[self.direction]: continue
            
            new_head = (head[0] + d[0], head[1] + d[1])
            if wrap_mode:
                new_head = (new_head[0] % COLS, new_head[1] % ROWS)
            
            # Checar obstáculos e paredes
            is_deadly = False
            if new_head in obstacles: is_deadly = True
            if not wrap_mode:
                if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS:
                    is_deadly = True

            
            # Checar colisões com cobras
            for s in all_snakes:
                if new_head in s.body:
                    is_deadly = True
                    break
            
            if not is_deadly:
                valid_dirs.append(d)

        if not valid_dirs: return # Vai bater de qualquer jeito

        # 2. Escolher a melhor direção válida para chegar na comida
        def dist(d):
            nx, ny = head[0] + d[0], head[1] + d[1]
            if wrap_mode: nx, ny = nx % COLS, ny % ROWS
            return abs(nx - food_pos[0]) + abs(ny - food_pos[1])

        valid_dirs.sort(key=dist)
        self.next_dir = valid_dirs[0]
