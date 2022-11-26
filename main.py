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
        self.type = "markdown" if is_markdown else "code"
        self.lines = [*lines]
        if self.type == "markdown":
            self.lines = [l[1:] for l in self.lines]

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

    def __repr__(self):
        line_repr = '\n'.join(self.lines)
        match self.type:
            case "markdown":
                return f"Markdown {{\n{line_repr}\n}}"
            case "code":
                return f"Code {{\n{line_repr}\n}}"

# This can be improved, line comments without a space
# before the code block should not be converted to markdown
def parse_code(code):
    lines = code.split('\n')
    blocks = it.groupby(lines, lambda line: len(line := line.strip()) == 0 or line[0] == '#')

    blocks = (Block(*args) for args in blocks)
    blocks = (b for b in blocks if b.lines not in [[], ['']])
    return blocks

def to_jupyter(blocks):
    cells = [block.to_jupyter() for block in blocks]
    toplevel = {'cells': cells, 'metadata': metadata, 'nbformat': 4, 'nbformat_minor': 5}
    return json.dumps(toplevel, indent=1)

if __name__ == "__main__":
    match sys.argv:
        case [_, '--to-jupyter', filename]:
            with open(filename, 'r') as inp:
                parsed = parse_code(inp.read())
                jupytered = to_jupyter(parsed)
                print(jupytered)
        case _: print("incorrect usage")
