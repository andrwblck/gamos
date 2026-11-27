"""Перевірка проходимості світу (грубе моделювання стрибків).
Для кожного набору здібностей рахує досяжні клітинки і перевіряє:
 - що потрібні предмети досяжні, а "закриті" ще ні (правильний порядок здібностей);
 - що з кожного досяжного місця можна повернутися до станції (немає пасток)."""
import sys, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import world
G, W, H = world.G, world.W, world.H
U, S, JU, JS, DASH = 4, 2, 2, 2, 3   # стрибок ~4.5 тайла, ранець ~3, ривок ~3.5

def run(ab):
    drill, boots, charge, jet = ('drill' in ab), ('boots' in ab), ('charge' in ab), ('jet' in ab)
    def ch(x, y): return G[y][x] if 0 <= x < W and 0 <= y < H else '#'
    def passable(x, y):
        c = ch(x, y)
        if c == '#' or c == '^': return False
        if c == 'x': return drill
        if c == 'b': return charge
        return True
    def solid(x, y):
        c = ch(x, y); return c == '#' or (c == 'x' and not drill) or (c == 'b' and not charge)
    def support(x, y): return solid(x, y+1) or ch(x, y+1) == '='
    def nxt(st):
        m, x, y, u, s, d, j = st
        out = []
        if m == 'g':
            for dx in (-1, 1):
                if passable(x+dx, y):
                    out.append(('g', x+dx, y, 0, 0, 1, 1) if support(x+dx, y) else ('f', x+dx, y, 0, 0, 1, 1))
            out.append(('r', x, y, U, S, 1, 1))
            if ch(x, y+1) == '=': out.append(('f', x, y+1, 0, 0, 1, 1))
            return out
        wall = boots and (solid(x-1, y) or solid(x+1, y))
        if wall:
            out.append(('r', x, y, U, S, 1, 1))
            if passable(x, y-1): out.append(('r', x, y-1, U, S, 1, 1))
        if d:
            for dx in (-1, 1):
                for k in range(1, DASH+1):
                    if not passable(x+dx*k, y): break
                    out.append((m, x+dx*k, y, u, s, 0, j))
        if jet and j: out.append(('r', x, y, JU, JS, d, 0))
        if m == 'r':
            if u > 0 and passable(x, y-1): out.append(('r', x, y-1, u-1, s, d, j))
            if s > 0:
                for dx in (-1, 1):
                    if passable(x+dx, y): out.append(('r', x+dx, y, u, s-1, d, j))
            out.append(('f', x, y, 0, 0, d, j))
        else:
            if support(x, y): out.append(('g', x, y, 0, 0, 1, 1)); return out
            if passable(x, y+1): out.append(('f', x, y+1, 0, 0, d, j))
            for dx in (-1, 1):
                if passable(x+dx, y+1) and (passable(x+dx, y) or passable(x, y+1)):
                    out.append(('f', x+dx, y+1, 0, 0, d, j))
        return out
    start = ('g', 5, 17+15, 0, 0, 1, 1)
    seen = {start}; q = collections.deque([start]); rev = collections.defaultdict(list)
    while q:
        st = q.popleft()
        for n in nxt(st):
            rev[n].append(st)
            if n not in seen: seen.add(n); q.append(n)
    cells = {(s[1], s[2]) for s in seen}
    # повернення до станцій
    stations = [s for s in seen if s[0] == 'g' and G[s[2]][s[1]] == 'S']
    back = set(stations); q = collections.deque(stations)
    while q:
        st = q.popleft()
        for p in rev[st]:
            if p not in back: back.add(p); q.append(p)
    traps = [s for s in seen if s[0] == 'g' and s not in back]
    return cells, traps

def find(c):
    return [(x, y) for y in range(H) for x in range(W) if G[y][x] == c]
def room_of(x, y):
    for r in world.ROOMS:
        if r.x0 <= x < r.x0+r.w and r.y0 <= y < r.y0+r.h: return r.key
    return '?'

stages = [
    ([], ['D'], ['M', 'C', 'J', 'Z']),
    (['drill'], ['M', 'W'], ['C', 'J', 'Z']),
    (['drill', 'boots'], ['B', 'C', 'R'], ['J', 'Z']),
    (['drill', 'boots', 'charge'], ['J'], ['Z']),
    (['drill', 'boots', 'charge', 'jet'], ['Z', 'H', 'W', 'R', 'S', 'M', 'D', 'C', 'J'], []),
]
ok = True
for ab, need, forbid in stages:
    cells, traps = run(ab)
    print('== здібності:', ab or ['немає'], ' досяжних клітинок:', len(cells))
    for c in need:
        for pos in find(c):
            if c in 'BZ':
                hit = any((pos[0]+dx, pos[1]) in cells for dx in range(-20, 20))
            else:
                hit = pos in cells
            if not hit and c in need and (c != 'H' and c != 'W' and c != 'R' or ab == stages[-1][0]):
                print('   НЕДОСЯЖНО', c, pos, room_of(*pos)); ok = False
    for c in forbid:
        for pos in find(c):
            if pos in cells: print('   ЗАРАНО ДОСЯЖНО', c, pos, room_of(*pos)); ok = False
    if traps:
        ok = False
        rooms = collections.Counter(room_of(s[1], s[2]) for s in traps)
        print('   ПАСТКИ (немає шляху назад):', dict(rooms), traps[:5])
print('OK' if ok else 'ПОМИЛКИ')

# секрети: (символ, кімната) -> з якої стадії мають ставати досяжними
SECRETS = [('H', 'storage', 1), ('W', 'vault', 1), ('R', 'shaft', 2), ('R', 'cache', 0),
           ('H', 'cavern', 4), ('H', 'crucible', 3), ('W', 'crucible', 3)]
res = [run(ab)[0] for ab, _, _ in stages]
for c, rk, st in SECRETS:
    pos = [p for p in find(c) if room_of(*p) == rk][0]
    first = next(i for i, cells in enumerate(res) if pos in cells)
    flag = 'ok' if first == st else 'ПОМИЛКА'
    if first != st: ok = False
    print(f'секрет {c} у {rk}: відкривається на стадії {first} (очікується {st}) {flag}')
print('ВСЕ OK' if ok else 'Є ПОМИЛКИ')
