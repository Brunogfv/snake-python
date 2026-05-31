import pygame

# ---------------------------------------------------------------------------
# Configurações de Tela e Grade
# ---------------------------------------------------------------------------
COLS, ROWS = 20, 20
CELL = 28
UI_HEIGHT = 80
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + UI_HEIGHT
FPS = 60
MOVE_INTERVAL = 0.13

# ---------------------------------------------------------------------------
# Estética e Desenho
# ---------------------------------------------------------------------------
SNAKE_BORDER_RADIUS = 5
SNAKE_EYE_SIZE = 3
SNAKE_EYE_OFFSET = 4
FOOD_PULSE_SPEED = 3
FOOD_RING_SPEED = 5
SHAKE_DURATION = 0.3
SHAKE_DEFAULT_INTENSITY = 8
PARTICLE_COUNT_EAT = 15
PARTICLE_COUNT_DIE = 30

# ---------------------------------------------------------------------------
# Fontes (Tamanhos)
# ---------------------------------------------------------------------------
FONT_SIZE_BIG = 60
FONT_SIZE_MID = 40
FONT_SIZE_SMALL = 28
FONT_SIZE_TINY = 20

# ---------------------------------------------------------------------------
# Posicionamento UI
# ---------------------------------------------------------------------------
UI_MARGIN_X = 20
UI_SCORE_Y_OFFSET = 15
UI_RECORD_Y_OFFSET = 15
UI_POWERUP_Y_OFFSET = 20
UI_PAUSE_HINT_Y_OFFSET = 48
UI_PAUSE_HINT_X_OFFSET = 80

# ---------------------------------------------------------------------------
# Economia e Skins
# ---------------------------------------------------------------------------
GOLD_REWARD_NORMAL = 1
GOLD_REWARD_GOLDEN = 10

# ---------------------------------------------------------------------------
# Modo Fever (Berserk)
# ---------------------------------------------------------------------------
FEVER_COMBO_LIMIT = 5
FEVER_DURATION = 5.0
FEVER_COMBO_TIMEOUT = 3.0
FEVER_SCORE_MULTIPLIER = 2
FEVER_COLOR_GLOW = (255, 255, 255)

# ---------------------------------------------------------------------------
# Portais (Wormholes)
# ---------------------------------------------------------------------------
PORTAL_COLOR_A = (100, 255, 255)
PORTAL_COLOR_B = (255, 100, 255)
PORTAL_SPAWN_CHANCE = 0.1
PORTAL_DURATION = 10.0

# ---------------------------------------------------------------------------
# Inimigos (Cobras IA)
# ---------------------------------------------------------------------------
ENEMY_SPAWN_SCORE_INTERVAL = 15
ENEMY_MAX_COUNT = 2
ENEMY_SKIN = {"head": (255, 50, 50), "tail": (150, 20, 20)}
ENEMY_KILL_REWARD = 20

SKINS = [
    {"name": "Classica", "head": (60, 255, 140), "tail": (0, 120, 50), "price": 0},
    {"name": "Neon",     "head": (255, 0, 255),  "tail": (50, 0, 50),   "price": 50},
    {"name": "Fogo",     "head": (255, 100, 0),  "tail": (100, 20, 0),  "price": 100},
    {"name": "Gelo",     "head": (0, 200, 255),  "tail": (0, 50, 100),  "price": 100},
    {"name": "Realeza",  "head": (255, 215, 0),  "tail": (139, 69, 19), "price": 250},
]

SHOP_BG = (15, 15, 30)
SHOP_CARD = (30, 30, 50)
GOLD_COLOR = (255, 215, 0)

# ---------------------------------------------------------------------------
# Direções e Controles
# ---------------------------------------------------------------------------
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

DIR_KEYS = {
    pygame.K_UP: UP, 
    pygame.K_DOWN: DOWN, 
    pygame.K_LEFT: LEFT, 
    pygame.K_RIGHT: RIGHT
}

DIR_KEYS_P2 = {
    pygame.K_w: UP,
    pygame.K_s: DOWN,
    pygame.K_a: LEFT,
    pygame.K_d: RIGHT
}

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# ---------------------------------------------------------------------------
# Configurações Multiplayer
# ---------------------------------------------------------------------------
P1_START_POS = (COLS // 4, ROWS // 2)
P2_START_POS = (3 * COLS // 4, ROWS // 2)
P2_DEFAULT_SKIN = {"name": "Sombra", "head": (150, 0, 255), "tail": (50, 0, 100)}

# ---------------------------------------------------------------------------
# Tipos de Comida e Cores
# ---------------------------------------------------------------------------
NORMAL, GOLDEN, ICE, SHRINK, SPEED = range(5)
FOOD_COLORS = [
    (255, 80, 80),   # NORMAL
    (255, 200, 50),  # GOLDEN
    (80, 150, 255),  # ICE
    (200, 80, 255),  # SHRINK
    (255, 150, 50)   # SPEED
]
FOOD_LABELS = ["", "OURO", "GELO", "ENCURTAR", "TURBO"]

# ---------------------------------------------------------------------------
# Cores do Tema
# ---------------------------------------------------------------------------
BG = (12, 12, 22)
GRID_LINE = (22, 22, 36)
SNAKE_HEAD = (60, 255, 140)
SNAKE_BODY = (0, 210, 90)
SNAKE_TAIL = (0, 120, 50)
OBSTACLE_COLOR = (80, 80, 100)
TEXT = (255, 255, 255)
RECORD_COLOR = (200, 200, 100)
PAUSE_TEXT_COLOR = (150, 150, 150)
PAUSE_HINT_COLOR = (80, 80, 80)

# ---------------------------------------------------------------------------
# Níveis e Obstáculos
# ---------------------------------------------------------------------------
LEVELS = [
    {"name": "Clássico", "obstacles": []},
    {"name": "Pilares", "obstacles": [
        (5, 5), (5, 6), (6, 5), (6, 6),
        (14, 5), (14, 6), (13, 5), (13, 6),
        (5, 14), (5, 13), (6, 14), (6, 13),
        (14, 14), (14, 13), (13, 14), (13, 13)
    ]},
    {"name": "Labirinto", "obstacles": [
        (i, 5) for i in range(4, 16)] + [(i, 14) for i in range(4, 16)] + [
        (5, i) for i in range(6, 14)] + [(14, i) for i in range(6, 14)
    ]},
    {"name": "Apartamento", "obstacles": [
        (10, i) for i in range(0, 8)] + [(10, i) for i in range(12, 20)] + [
        (i, 10) for i in range(0, 8)] + [(i, 10) for i in range(12, 20)
    ]}
]

# ---------------------------------------------------------------------------
# Estados do Jogo
# ---------------------------------------------------------------------------
MENU, PLAYING, OVER, PAUSED = range(4)
