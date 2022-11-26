# # Python to Jupyter
# Converts commented python to jupyter notebook

import ast
import sys
import itertools as it
import json

metadata = {
        "kernelspec": {
            "display_name": "Python 3.10 (ipykernel)",
            "language": "python",
            "name": "python3.10",
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3,
            },
            "file_extension": ".py",
            "mimetype": "x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10.7"
        }
    }

id_count = 0

class Block:
    def __init__(self, is_markdown, lines):
        if type(is_markdown) == bool:
            self.type = "markdown" if is_markdown else "code"
        else:
            self.type = is_markdown

        self.lines = [*lines]

        if self.type == "markdown":
            self.lines = [line[1:] for line in self.lines]

        if self.lines != [] and len(self.lines[0].strip()) == 0:
            self.lines = self.lines[1:]

        if self.lines != [] and len(self.lines[-1].strip()) == 0:
            self.lines = self.lines[:-1]

    def to_jupyter(self):
        global id_count
        id_count += 1

        source = [l + '\n' for l in self.lines[:-1]] + self.lines[-1:]

        match self.type:
            case "markdown": 
                return { "cell_type": "markdown",
                        "metadata": {},
                        "source": source }
            case "code":
                return { "cell_type": "code",
                        "execution_count": None,
                        "id": f'{id_count}',
                        "metadata": {},
                        "outputs": [],
                        "source": source }

    def to_py(self):
        return ''.join(self.lines)

    def __repr__(self):
        line_repr = '\n'.join(self.lines)
        match self.type:
            case "markdown":
                return f"Markdown {{\n{line_repr}\n}}"
            case "code":
                return f"Code {{\n{line_repr}\n}}"

# if there is a space between comments
# it makes a new block
# - bullet 1

# line comments without a space before the code
# stay in the code block
def parse_code(code):
    lines = code.split('\n')

    def classify_line(line):
        line = line.strip()
        if len(line) > 0 and line[0] == '#':
            return 'markdown'
        else:
            return 'code'

    blocks = it.groupby(lines, classify_line)
    blocks = [(t, [*l]) for t, l in blocks]

    squished_blocks = []
    i = 0
    while i < len(blocks) - 1:
        (t1, l1) = blocks[i]
        (t2, l2) = blocks[i + 1]

        l1, l2 = [*l1], [*l2]

        if t1 == 'markdown' and t2 == 'code' and not (l2 == [] or len(l2[0].strip()) == 0):
            squished_blocks.append((t2, l1 + l2))
            i += 2
        else:
            squished_blocks.append((t1, l1))
            i += 1

    if i != len(blocks):
        squished_blocks.append(blocks[-1])

    blocks = (Block(*args) for args in squished_blocks)
    blocks = (b for b in blocks if b.lines not in [[], ['']])
    return blocks

def parse_jupyter(source):
    data = json.loads(source)
    blocks = [Block(block['cell_type'] == 'markdown', block['source']) for block in data['cells']]
    return blocks

def to_jupyter(blocks):
    cells = [block.to_jupyter() for block in blocks]
    toplevel = {'cells': cells, 'metadata': metadata, 'nbformat': 4, 'nbformat_minor': 5}
    return json.dumps(toplevel, indent=1)

def to_py(blocks):
    return '\n\n'.join(block.to_py() for block in blocks)

if __name__ == "__main__":
    match sys.argv:
        case [_, '--to-jupyter', filename]:
            with open(filename, 'r') as inp:
                parsed = parse_code(inp.read())
                jupytered = to_jupyter(parsed)
                print(jupytered)
        case [_, '--from-jupyter', filename]:
            with open(filename, 'r') as inp:
                parsed = parse_jupyter(inp.read())
                py = to_py(parsed)
                print(py)
        case _: print("incorrect usage")
