# Where this came from

Four independent reviewers went through ~44 Advent of Code and Google Foobar solutions
written under time pressure, ranking findings by readability, then correctness, then
performance. This package is the part of that review that turned into code.

The full write-up lives in
[`CODE_REVIEW.md`](https://github.com/jburgy/blog/blob/main/CODE_REVIEW.md).

## The findings that became API decisions

**A `while q:` loop doesn't say which algorithm you wrote.** Four visually identical
loops across the surveyed files had four different semantics: flood fill, SPFA, a path
counter with no visited set at all, and one shortest-path search that was accidentally
component labelling. Hence `order` with no default, and `key` as an explicit parameter
rather than a hardcoded `seen` set.

**Silent wraparound beats you eventually.** Negative-index wrap, missing column checks,
and grids doubling as distance arrays produced wrong answers rather than crashes in three
separate files. Hence `Grid.__getitem__` raising, ragged input rejected at construction,
and `Grid.get` taking the sentinel instead of a padded border shifting every coordinate.

**Floats used purely to be compared.** One solution took a square root to decide a
tie-break. The exact integer version was correct *and* 1.5× faster. Hence
`Vec.norm2() -> int`, and no `abs()`.

**Two meanings in one value.** A function returning `list | None` where `None` meant
"loop detected"; a `complex` carrying two unrelated integer counters; a grid array that
was simultaneously wall map, visited set and distance table. Hence `dijkstra` returning a
named pair, and `patrol`-style examples returning two values rather than overloading one.

**The stdlib misses cluster at the end of the file.** `math.prod` that would have printed
part 1, a `bisect` worth 200×, a second `print` — all wrap-up-phase omissions in code
whose author demonstrably knew `graphlib`, `functools.cache` and `scipy.optimize`. Hence
this package being as small as it is.

## What was cut, and why

Seven modules were sketched. Three already existed:

`dsu` → {class}`scipy.cluster.hierarchy.DisjointSet`
: The proposed API was `union()` returning a bool and a maintained component count.
  scipy's `merge()` returns a bool and `n_subsets` is maintained, with union-by-size and
  path halving for free. Identical, shipped, in a package the reviewed repo already
  imported. The hand-rolled version it would have replaced recomputed its component
  count with a thousand-element scan after every union.

`runner` → [`aocd`](https://pypi.org/project/advent-of-code-data/)
: `solve(parse, part1, part2, expect=...)` is what `aocd`'s runner already does.

`INF = 1 << 62` → {data}`sys.maxsize`
: Inventing a constant when the stdlib names one.

And `bits` shrank from four functions to one once `int.bit_count`, `int.bit_length` and
`numpy.packbits` were accounted for.

That leaves the one genuine gap — search over states that do not exist until you generate
them — plus enough grid and parsing glue to make the call sites readable.

## Testing

Every test in the repository is a regression for something the review actually found,
including a fuzz test against a nine-line reference BFS. That reference is what caught the
worst defect in the survey: a shortest-path function wrong on 14% of random grids whose
two hand-written test cases both passed.

Two examples from a problem statement are not a test suite. When a problem has a cheap,
obviously-correct, exponential reference, write it and fuzz against it.
