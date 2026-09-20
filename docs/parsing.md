# Parsing and bits

## `ints` — stop writing parsers

Four reviewed files parsed numbers with fixed-width slices, three with bespoke regexes,
one by stripping brackets with `[1:-1]` three times in a single file. All of them are
this:

```{py-editor}
from puzzlekit import ints

print(ints("Button A: X+94, Y+34"))
print(ints("p=0,4 v=3,-3"))
print(ints("[#..#] 1,3,4 [12]"))
print(ints("no digits here"))
```

Fixed-width slicing is the specific habit worth dropping. `int(line[:6])` depends on both
the digit count and the trailing newline; a final line without one silently loses a digit.

## `sections` — inputs with two shapes

Splitting on blank lines replaces the `if/elif` parser state machines and the
`mode = None` flags that appear whenever an input stacks two formats in one file. One
reviewed file needed a type-checker suppression purely because its section boundary
doubled as a variable initialiser.

```{py-editor}
from puzzlekit import ints, sections

blob = """\
47|53
97|13
75|29

75,47,61,53,29
97,61,53,29,13"""

rules, updates = sections(blob)
print("rules:  ", [ints(line) for line in rules])
print("updates:", [ints(line) for line in updates])
```

## `text` and `lines` resolve against the caller

Every solution file in the survey hardcoded a path relative to the repository root, so
none of them ran from anywhere else. {func}`~puzzlekit.io.text` and
{func}`~puzzlekit.io.lines` look next to the *calling module* instead.

`lines` uses {meth}`str.splitlines`, which removes the rstrip-or-not decision entirely —
currently spelled four different ways across one year of solutions, one of which
(`.strip()` on column-aligned data) was a live hazard.

```python
from puzzlekit import lines

grid = lines("day12input.txt")   # sits next to this file, not next to your shell
```

If the input is an Advent of Code puzzle you have not downloaded yet,
[`aocd`](https://pypi.org/project/advent-of-code-data/) is the better tool: it fetches,
caches per day, and verifies answers.

## `bits`

{meth}`int.bit_count` is popcount, {meth}`int.bit_length` is width, and
`numpy.packbits`/`unpackbits` convert to and from arrays. Iterating set-bit *indices* has
no stdlib equivalent, and hand-rolling it tends to come out as a string round trip like
`bin(word)[:1:-1]`.

```{py-editor}
from puzzlekit import bits

word = 0b1011_0010
print("indices:", list(bits(word)))
print("popcount agrees:", len(list(bits(word))) == word.bit_count())
print("round trip:", sum(1 << i for i in bits(word)) == word)

try:
    list(bits(-1))
except ValueError as err:
    print("negative:", err)
```
