import pygame
import sys
import os
import json
import random
import asyncio

from constants import *
from audio import *
from entities import Snake, Food, Particle, Portal, EnemySnake

# ---------------------------------------------------------------------------
# Inicialização
# ---------------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Deluxe - Web Edition")
clock = pygame.time.Clock()

font_big   = pygame.font.Font(None, FONT_SIZE_BIG)
font_mid   = pygame.font.Font(None, FONT_SIZE_MID)
font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
font_tiny  = pygame.font.Font(None, FONT_SIZE_TINY)

DATA_FILE = os.path.join(os.path.dirname(__file__), "snake_data.json")

def load_game_data():
    default = {
        "high_score": 0,
        "gold": 0,
        "owned_skins": ["Classica"],
        "selected_skin": "Classica"
    }
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                for k, v in default.items():
                    if k not in data: data[k] = v
                return data
    except:
        pass
    return default

def save_game_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

# ---------------------------------------------------------------------------
# Helpers de Desenho
# ---------------------------------------------------------------------------
def draw_grid(shake=(0, 0)):
    sx, sy = shake
    for x in range(0, WIDTH + 1, CELL):
        pygame.draw.line(screen, GRID_LINE, (x + sx, sy), (x + sx, ROWS * CELL + sy))
    for y in range(0, ROWS * CELL + 1, CELL):
        pygame.draw.line(screen, GRID_LINE, (sx, y + sy), (WIDTH + sx, y + sy))

def draw_obstacles(obstacles, shake=(0, 0)):
    sx, sy = shake
    for (ox, oy) in obstacles:
        rect = (ox * CELL + 1 + sx, oy * CELL + 1 + sy, CELL - 2, CELL - 2)
        pygame.draw.rect(screen, OBSTACLE_COLOR, rect, border_radius=4)
        pygame.draw.rect(screen, (40, 40, 60), rect, 1, border_radius=4)

def draw_score(score, high, powerup_timer, shake=(0, 0)):
    sx, sy = shake
    grid_bottom = ROWS * CELL
    surf = font_mid.render(f"Score: {score}", True, TEXT)
    screen.blit(surf, (UI_MARGIN_X + sx, grid_bottom + UI_SCORE_Y_OFFSET + sy))
    surf2 = font_mid.render(f"Recorde: {high}", True, RECORD_COLOR)
    screen.blit(surf2, (WIDTH - UI_MARGIN_X - surf2.get_width() + sx, grid_bottom + UI_RECORD_Y_OFFSET + sy))
    if powerup_timer > 0:
        label = f"ICE: {powerup_timer:.1f}s" if powerup_timer < 10 else f"TURBO: {powerup_timer:.1f}s"
        c = (100, 180, 255) if powerup_timer < 10 else (255, 180, 80)
        t = font_tiny.render(label, True, c)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2 + sx, grid_bottom + 5 + sy))

def draw_fever_ui(combo_count, fever_timer, shake=(0, 0)):
    sx, sy = shake
    bar_width, bar_height = 140, 10
    x, y = WIDTH // 2 - bar_width // 2 + sx, ROWS * CELL + 50 + sy
    pygame.draw.rect(screen, (40, 40, 60), (x, y, bar_width, bar_height), border_radius=5)
    if fever_timer > 0:
        w = int(bar_width * (fever_timer / FEVER_DURATION))
        color = (255, 255, 100) if pygame.time.get_ticks() % 200 > 100 else (255, 255, 255)
        pygame.draw.rect(screen, color, (x, y, w, bar_height), border_radius=5)
        txt = font_tiny.render("MODO FEVER!", True, (255, 255, 0))
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2 + sx, y - 15 + sy))
    elif combo_count > 0:
        w = int(bar_width * (combo_count / FEVER_COMBO_LIMIT))
        pygame.draw.rect(screen, (100, 255, 150), (x, y, w, bar_height), border_radius=5)
        txt = font_tiny.render(f"COMBO x{combo_count}", True, (100, 255, 150))
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2 + sx, y - 15 + sy))

def draw_food_label(food):
    if food.ftype != NORMAL:
        label, color = FOOD_LABELS[food.ftype], FOOD_COLORS[food.ftype]
        x, y = food.pos
        t = font_tiny.render(label, True, color)
        screen.blit(t, (x * CELL + CELL // 2 - t.get_width() // 2, y * CELL - 16))

def draw_touch_controls():
    # Botões de toque para Celular (D-Pad visual semi-transparente)
    # Desenhar círculos nos cantos ou áreas de clique
    alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ctrl_color = (255, 255, 255, 40)
    
    # Posições dos botões (D-Pad no canto inferior direito)
    btn_size = 60
    bx, by = WIDTH - 110, HEIGHT - 150
    
    pygame.draw.circle(alpha_surf, ctrl_color, (bx, by - btn_size), 30) # Cima
    pygame.draw.circle(alpha_surf, ctrl_color, (bx, by + btn_size), 30) # Baixo
    pygame.draw.circle(alpha_surf, ctrl_color, (bx - btn_size, by), 30) # Esquerda
    pygame.draw.circle(alpha_surf, ctrl_color, (bx + btn_size, by), 30) # Direita
    
    screen.blit(alpha_surf, (0, 0))

def handle_touch_input(pos):
    # Converte clique/toque em direção
    bx, by = WIDTH - 110, HEIGHT - 150
    tx, ty = pos
    dist = 40
    
    if abs(tx - bx) < dist and abs(ty - (by - 60)) < dist: return pygame.K_UP
    if abs(tx - bx) < dist and abs(ty - (by + 60)) < dist: return pygame.K_DOWN
    if abs(tx - (bx - 60)) < dist and abs(ty - by) < dist: return pygame.K_LEFT
    if abs(tx - (bx + 60)) < dist and abs(ty - by) < dist: return pygame.K_RIGHT
    
    # Pausa se clicar no topo
    if ty < 50: return pygame.K_p
    return None

# ---------------------------------------------------------------------------
# Telas
# ---------------------------------------------------------------------------
async def menu_screen(gold):
    opts = ["Modo Clássico (paredes)", "Modo Livre (wrap)", "Multiplayer (X1)", "Selecionar Nível", "Loja de Skins"]
    sel = 0
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: sel = (sel - 1) % len(opts)
                elif e.key == pygame.K_DOWN: sel = (sel + 1) % len(opts)
                elif e.key == pygame.K_RETURN: return sel
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                for i in range(len(opts)):
                    y = 160 + i * 45
                    if abs(my - (y + 15)) < 20: 
                        if sel == i: return i
                        sel = i
        
        screen.fill(BG)
        t = font_big.render("SNAKE DELUXE", True, (100, 255, 150))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 60))
        g_surf = font_small.render(f"Ouro: {gold}", True, GOLD_COLOR)
        screen.blit(g_surf, (WIDTH - g_surf.get_width() - 20, 20))
        for i, o in enumerate(opts):
            color = (255, 255, 255) if i == sel else (120, 120, 120)
            txt = font_small.render(o, True, color)
            x, y = WIDTH // 2 - txt.get_width() // 2, 160 + i * 45
            if i == sel:
                pygame.draw.rect(screen, SNAKE_HEAD, (x-10, y-5, txt.get_width()+20, txt.get_height()+10), 2, border_radius=6)
            screen.blit(txt, (x, y))
        h = font_tiny.render("Tocar para selecionar / Enter confirmar", True, (100, 100, 100))
        screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT - 30))
        pygame.display.flip()
        await asyncio.sleep(0)

async def level_selection_screen():
    sel = 0
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: sel = (sel - 1) % len(LEVELS)
                elif e.key == pygame.K_DOWN: sel = (sel + 1) % len(LEVELS)
                elif e.key == pygame.K_ESCAPE: return "menu"
                elif e.key == pygame.K_RETURN: return sel
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                for i in range(len(LEVELS)):
                    y = 150 + i * 60
                    if abs(my - (y + 15)) < 25:
                        if sel == i: return i
                        sel = i
        screen.fill(BG)
        t = font_mid.render("SELECIONAR NÍVEL", True, TEXT)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 40))
        for i, level in enumerate(LEVELS):
            color = (255, 255, 255) if i == sel else (100, 100, 100)
            txt = font_small.render(level["name"], True, color)
            x, y = WIDTH // 2 - txt.get_width() // 2, 150 + i * 60
            if i == sel:
                pygame.draw.rect(screen, SNAKE_HEAD, (x-15, y-5, txt.get_width()+30, txt.get_height()+10), 2, border_radius=6)
            screen.blit(txt, (x, y))
        hint = font_tiny.render("ESC para voltar", True, (80, 80, 80))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))
        pygame.display.flip()
        await asyncio.sleep(0)

async def shop_screen(game_data):
    sel = 0
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT: sel = (sel - 1) % len(SKINS)
                elif e.key == pygame.K_RIGHT: sel = (sel + 1) % len(SKINS)
                elif e.key == pygame.K_ESCAPE: return "menu"
                elif e.key == pygame.K_RETURN:
                    skin = SKINS[sel]
                    if skin["name"] in game_data["owned_skins"]:
                        game_data["selected_skin"] = skin["name"]
                    elif game_data["gold"] >= skin["price"]:
                        game_data["gold"] -= skin["price"]
                        game_data["owned_skins"].append(skin["name"])
                        game_data["selected_skin"] = skin["name"]
                        save_game_data(game_data)
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if mx < WIDTH // 2: sel = (sel - 1) % len(SKINS)
                else: sel = (sel + 1) % len(SKINS)
                # Lógica de compra simplificada para toque (clique duplo no card)
                if my > HEIGHT // 2 - 50 and my < HEIGHT // 2 + 150:
                    skin = SKINS[sel]
                    if skin["name"] in game_data["owned_skins"]: game_data["selected_skin"] = skin["name"]
                    elif game_data["gold"] >= skin["price"]:
                        game_data["gold"] -= skin["price"]
                        game_data["owned_skins"].append(skin["name"])
                        game_data["selected_skin"] = skin["name"]
                        save_game_data(game_data)

        screen.fill(SHOP_BG)
        t = font_mid.render("LOJA DE SKINS", True, TEXT)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 30))
        g_surf = font_small.render(f"Seu Ouro: {game_data['gold']}", True, GOLD_COLOR)
        screen.blit(g_surf, (WIDTH // 2 - g_surf.get_width() // 2, 70))
        skin = SKINS[sel]
        card_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 220)
        pygame.draw.rect(screen, SHOP_CARD, card_rect, border_radius=15)
        for i in range(3):
            c = lerp_color(skin["head"], skin["tail"], i/2)
            pygame.draw.rect(screen, c, (WIDTH // 2 - 15, HEIGHT // 2 - 30 + i*25, 30, 20), border_radius=4)
        name_t = font_small.render(skin["name"], True, TEXT)
        screen.blit(name_t, (WIDTH // 2 - name_t.get_width() // 2, HEIGHT // 2 + 60))
        status, color = "", TEXT
        if skin["name"] == game_data["selected_skin"]:
            status, color = "[ EQUIPADO ]", (100, 255, 100)
        elif skin["name"] in game_data["owned_skins"]:
            status = "EQUIPAR (Toque)"
        else:
            status = f"COMPRAR: {skin['price']} Ouro"
            if game_data["gold"] < skin["price"]: color = (255, 100, 100)
        st_t = font_tiny.render(status, True, color)
        screen.blit(st_t, (WIDTH // 2 - st_t.get_width() // 2, HEIGHT // 2 + 95))
        hint = font_tiny.render("Tocar lados para navegar  ESC voltar", True, (150, 150, 150))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))
        pygame.display.flip()
        await asyncio.sleep(0)

async def game_over_screen(score, high, is_record, winner=None):
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_r, pygame.K_SPACE): return "restart"
                if e.key == pygame.K_m: return "menu"
                if e.key == pygame.K_q: return "quit"
            if e.type == pygame.MOUSEBUTTONDOWN: return "restart"
        screen.fill(BG)
        draw_grid()
        t_title = winner if winner else "GAME OVER"
        t1 = font_big.render(t_title, True, (255, 100, 100) if not winner else (255, 255, 100))
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 70))
        t2 = font_mid.render(f"Score: {score}", True, TEXT)
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 - 10))
        if is_record and not winner:
            t3 = font_small.render("NOVO RECORDE!", True, (255, 255, 100))
            screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 35))
        t4 = font_small.render("Toque para Jogar Novamente", True, (150, 150, 150))
        screen.blit(t4, (WIDTH // 2 - t4.get_width() // 2, HEIGHT // 2 + 85))
        pygame.display.flip()
        await asyncio.sleep(0)

# ---------------------------------------------------------------------------
# Loop Principal do Jogo
# ---------------------------------------------------------------------------
async def run_game(wrap_mode, skin_data, obstacles=[], multiplayer=False):
    # Inicialização das cobras
    p1 = Snake(skin_data["head"], skin_data["tail"], start_pos=P1_START_POS if multiplayer else None, start_dir=RIGHT, key_map=DIR_KEYS)
    snakes, enemies = [p1], []
    if multiplayer:
        snakes.append(Snake(P2_DEFAULT_SKIN["head"], P2_DEFAULT_SKIN["tail"], start_pos=P2_START_POS, start_dir=LEFT, key_map=DIR_KEYS_P2))
    
    food = Food(snakes + enemies, obstacles)
    active_portal, portal_timer = None, 0
    score, gold_earned, combo_count, combo_timer, last_enemy_spawn_score = 0, 0, 0, 0, 0
    data = load_game_data()
    high = data["high_score"]
    move_timer, state, particles, shake_timer, shake_intensity = 0, PLAYING, [], 0, 0
    powerup = {"type": None, "timer": 0}

    def spawn_portal():
        nonlocal active_portal, portal_timer
        spots = []
        while len(spots) < 2:
            p = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if not any(p in s for s in snakes + enemies) and p not in obstacles and p != food.pos and p not in spots:
                spots.append(p)
        active_portal = Portal(spots[0], spots[1])
        portal_timer = PORTAL_DURATION

    def spawn_enemy():
        nonlocal last_enemy_spawn_score
        if len(enemies) >= ENEMY_MAX_COUNT: return
        while True:
            p = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if abs(p[0] - p1.body[0][0]) + abs(p[1] - p1.body[0][1]) > 8 and p not in obstacles and p != food.pos:
                enemies.append(EnemySnake(ENEMY_SKIN["head"], ENEMY_SKIN["tail"], start_pos=p, start_dir=random.choice([UP, DOWN, LEFT, RIGHT])))
                break

    def apply_powerup(ptype):
        nonlocal food
        powerup["type"] = ptype
        if ptype == ICE: powerup["timer"] = 5.0
        elif ptype == SPEED: powerup["timer"] = 3.0
        elif ptype == SHRINK:
            for s in snakes + enemies:
                for _ in range(3): s.pop_tail()

    while True:
        dt = clock.tick(FPS) / 1000.0
        t_now = pygame.time.get_ticks() / 1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit", {}
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "menu", {}
                if e.key == pygame.K_p:
                    state = PAUSED if state == PLAYING else PLAYING
                    continue
                if state == PLAYING:
                    for s in snakes: s.handle_input(e.key)
            if e.type == pygame.MOUSEBUTTONDOWN and state == PLAYING:
                # Controles de Toque integrados
                touch_key = handle_touch_input(e.pos)
                if touch_key:
                    if touch_key == pygame.K_p: state = PAUSED
                    else: 
                        for s in snakes: s.handle_input(touch_key)

        if state == PAUSED:
            screen.fill(BG); t1 = font_big.render("PAUSADO", True, (150, 150, 150))
            screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 20))
            t2 = font_tiny.render("Toque no topo para continuar", True, (100, 100, 100))
            screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 30))
            pygame.display.flip()
            if pygame.mouse.get_pressed()[0]:
                if pygame.mouse.get_pos()[1] < 100: state = PLAYING
            await asyncio.sleep(0); continue

        move_timer += dt
        if combo_timer > 0:
            combo_timer -= dt
            if combo_timer <= 0: combo_count = 0
        if portal_timer > 0:
            portal_timer -= dt
            if portal_timer <= 0: active_portal = None
        is_fever_active = any(s.fever_timer > 0 for s in snakes)
        for s in snakes + enemies:
            if s.fever_timer > 0: s.fever_timer -= dt
        
        base_interval = MOVE_INTERVAL
        if powerup["type"] == ICE: base_interval *= 2.0
        elif powerup["type"] == SPEED or is_fever_active: base_interval *= 0.6
        speed = max(0.04, base_interval - (score * 0.003))

        if powerup["timer"] > 0:
            powerup["timer"] -= dt
            if powerup["timer"] <= 0: powerup["type"] = None

        shake_timer = max(0, shake_timer - dt)
        shake = (0, 0)
        if shake_timer > 0:
            intensity = shake_intensity * (shake_timer / SHAKE_DURATION)
            shake = (random.randint(-int(intensity), int(intensity)), random.randint(-int(intensity), int(intensity)))

        if move_timer >= speed:
            move_timer = 0
            if not multiplayer and score >= last_enemy_spawn_score + ENEMY_SPAWN_SCORE_INTERVAL:
                spawn_enemy(); last_enemy_spawn_score = score
            for en in enemies: en.decide_direction(food.pos, obstacles, snakes + enemies, wrap_mode)
            
            all_active = snakes + enemies
            new_heads = []
            for s in all_active:
                nh = s.update(wrap_mode)
                if active_portal:
                    exit_pos = active_portal.get_exit(nh)
                    if exit_pos:
                        s.body_set.remove(nh); s.body.pop(0); nh = exit_pos
                        s.body.insert(0, nh); s.body_set.add(nh)
                        particles.append(Particle(nh[0]*CELL+CELL//2, nh[1]*CELL+CELL//2, (255,255,255), 10))
                new_heads.append(nh)

            food_eaten = False
            for i, s in enumerate(all_active):
                if new_heads[i] == food.pos:
                    food_eaten, ptype = True, food.ftype
                    mult = FEVER_SCORE_MULTIPLIER if s.fever_timer > 0 else 1
                    if s in snakes:
                        if ptype == NORMAL:
                            score += 1 * mult; gold_earned += GOLD_REWARD_NORMAL * mult; snd_eat.play()
                        elif ptype == GOLDEN:
                            score += 3 * mult; gold_earned += GOLD_REWARD_GOLDEN * mult; snd_eat_gold.play()
                        elif ptype in (ICE, SPEED, SHRINK):
                            apply_powerup(ptype); snd_powerup.play()
                        if not is_fever_active:
                            combo_count += 1; combo_timer = FEVER_COMBO_TIMEOUT
                            if combo_count >= FEVER_COMBO_LIMIT:
                                for sn in snakes: sn.fever_timer = FEVER_DURATION
                                combo_count, combo_timer = 0, 0
                        if not active_portal and random.random() < PORTAL_SPAWN_CHANCE: spawn_portal()
                    particles.append(Particle(food.pos[0]*CELL+CELL//2, food.pos[1]*CELL+CELL//2, FOOD_COLORS[ptype], PARTICLE_COUNT_EAT))
                else: s.pop_tail()
            if food_eaten: food = Food(all_active, obstacles)

            dead_player, winner, to_remove_enemies = False, None, []
            for i, s in enumerate(all_active):
                h, killed = new_heads[i], False
                if h in obstacles: killed = True
                elif not wrap_mode and (h[0] < 0 or h[0] >= COLS or h[1] < 0 or h[1] >= ROWS): killed = True
                if not killed and s.fever_timer <= 0:
                    if s.body.count(h) > 1: killed = True
                    else:
                        for other in all_active:
                            if s != other and h in other.body: killed = True; break
                if killed:
                    if s in snakes: dead_player = True
                    else:
                        to_remove_enemies.append(s); gold_earned += ENEMY_KILL_REWARD; score += 5
                        particles.append(Particle(s.body[0][0]*CELL+CELL//2, s.body[0][1]*CELL+CELL//2, ENEMY_SKIN["head"], 20))
            for en in to_remove_enemies:
                if en in enemies: enemies.remove(en)

            if dead_player:
                snd_die.play()
                if multiplayer:
                    if p1 in snakes and p1.check_collision(wrap_mode): winner = "Jogador 2 Venceu!"
                    else: winner = "Jogador 1 Venceu!"
                data["high_score"] = max(high, score); data["gold"] += gold_earned; save_game_data(data)
                shake_timer, shake_intensity, death_timer = 0.5, 12, 0.6
                while death_timer > 0:
                    dt_d = clock.tick(FPS) / 1000.0; death_timer -= dt_d
                    screen.fill(BG); draw_grid((random.randint(-5,5), random.randint(-5,5))); draw_obstacles(obstacles, (random.randint(-5,5), random.randint(-5,5)))
                    if active_portal: active_portal.draw(screen, t_now, (random.randint(-5,5), random.randint(-5,5)))
                    for sn in snakes + enemies: sn.draw(screen, (random.randint(-5,5), random.randint(-5,5)))
                    if multiplayer and winner:
                        tw = font_mid.render(winner, True, (255, 255, 100)); screen.blit(tw, (WIDTH//2 - tw.get_width()//2, HEIGHT//2))
                    pygame.display.flip()
                    await asyncio.sleep(0)
                return "over", {"score": score, "high": data["high_score"], "is_record": score > high, "gold_earned": gold_earned, "winner": winner}

        for p in particles: p.update(dt)
        particles = [p for p in particles if not p.dead]
        screen.fill(BG); draw_grid(shake); draw_obstacles(obstacles, shake)
        if active_portal: active_portal.draw(screen, t_now, shake)
        for s in snakes + enemies: s.draw(screen, shake)
        food.draw(screen, t_now, shake); draw_food_label(food)
        for p in particles: p.draw(screen, shake)
        draw_score(score, high, powerup["timer"], shake)
        draw_fever_ui(combo_count, snakes[0].fever_timer, shake)
        draw_touch_controls()
        
        pause_hint = font_tiny.render("Topo = Pausa", True, PAUSE_HINT_COLOR)
        screen.blit(pause_hint, (WIDTH // 2 - pause_hint.get_width() // 2, 10))
        pygame.display.flip()
        await asyncio.sleep(0)

async def main():
    selected_level_idx = 0
    while True:
        data = load_game_data()
        mode = await menu_screen(data["gold"])
        
        if mode is None: 
            break
        
        # Mapeamento do menu conforme menu_screen:
        # 0: Modo Clássico, 1: Modo Livre, 2: Multiplayer (X1), 3: Selecionar Nível, 4: Loja
        is_multiplayer = (mode == 2)
        
        if mode == 3: # Seleção de Nível
            lvl_action = await level_selection_screen()
            if lvl_action == "quit": break
            if isinstance(lvl_action, int):
                selected_level_idx = lvl_action
            continue
            
        if mode == 4: # Loja
            shop_action = await shop_screen(data)
            if shop_action == "quit": break
            continue

        # Configurações da partida
        selected_skin_data = next(s for s in SKINS if s["name"] == data["selected_skin"])
        obstacles = LEVELS[selected_level_idx]["obstacles"]

        while True:
            # mode == 1 é Modo Livre (wrap)
            result, game_result = await run_game(mode == 1, selected_skin_data, obstacles, is_multiplayer)
            
            if result == "over":
                action = await game_over_screen(
                    game_result["score"], 
                    game_result["high"], 
                    game_result["is_record"],
                    game_result.get("winner")
                )
                if action == "restart":
                    continue
                elif action == "menu":
                    break
                else: # quit
                    pygame.quit()
                    sys.exit()
            elif result == "menu":
                break
            else: # quit
                pygame.quit()
                sys.exit()
                
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
