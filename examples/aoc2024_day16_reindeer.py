"""AoC 2024 day 16 - all optimal paths without a second traversal.

The state is ``(position, heading)``: stepping costs 1, turning costs 1000, so the
graph is implicit and weighted. Part 2 asks which tiles lie on *some* best path. The
original solution answered it with a whole second search that materialised complete
paths as growing tuples; ``dijkstra`` already records every optimal predecessor, so it
is a backward walk over ``preds``.
"""

from puzzlekit import RIGHT, Grid, Vec, backtrack, dijkstra
from puzzlekit.vec import ORTHOGONAL

SAMPLE = """\
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############\
"""

EXPECTED = (7036, 45)

State = tuple[Vec, Vec]


def solve(text: str) -> tuple[int, int]:
    grid = Grid.parse(text)
    start, end = grid.find("S"), grid.find("E")

    def moves(state: State) -> list[tuple[State, int]]:
        pos, heading = state
        ahead = pos + heading
        out = [((pos, heading.rot(1)), 1000), ((pos, heading.rot(-1)), 1000)]
        if grid.get(ahead, "#") != "#":
            out.append(((ahead, heading), 1))
        return out

    dist, preds = dijkstra([(start, RIGHT)], moves)

    arrivals = [(end, h) for h in ORTHOGONAL if (end, h) in dist]
    best = min(dist[a] for a in arrivals)
    winners = [a for a in arrivals if dist[a] == best]
    tiles = {pos for pos, _ in backtrack(preds, winners)}
    return best, len(tiles)


def main() -> tuple[int, int]:
    return solve(SAMPLE)


if __name__ == "__main__":
    print(*main(), sep="\n")
