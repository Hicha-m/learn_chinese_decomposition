"""
Tree structure and analysis module.

This module contains:
- HanziNode and HanziTreeBuilder classes for character decomposition
- Tree traversal and analysis functions
- Character dependency mapping
"""

from collections import defaultdict
from hanzipy.decomposer import HanziDecomposer
from hanzipy.dictionary import HanziDictionary

from . import config, data

__all__ = [
    'HanziNode',
    'HanziTreeBuilder',
    'print_tree',
    'traverse_tree',
    'build_dependency_map_full',
    'analyze_character_v3',
    'compute_status',
    'print_tree_with_status',
    'get_decomposer',
    'get_dictionary',
]

# Module-level singletons
_decomposer = None
_dictionary = None


def get_decomposer():
    """Get or create HanziDecomposer singleton."""
    global _decomposer
    if _decomposer is None:
        _decomposer = HanziDecomposer()
    return _decomposer


def get_dictionary():
    """Get or create HanziDictionary singleton."""
    global _dictionary
    if _dictionary is None:
        _dictionary = HanziDictionary()
    return _dictionary


class HanziNode:
    """
    Node representing a Chinese character in decomposition tree.
    
    Attributes:
        id: Unique identifier for the node
        character: The Chinese character
        parent: Parent node in the tree
        depth: Depth in the tree
        children: Child nodes
        status: Learning status (learned/ready/blocked)
    """
    _id_counter = 0

    def __init__(self, character, parent=None, depth=0):
        self.id = HanziNode._id_counter
        HanziNode._id_counter += 1
        
        self.character = character
        self.parent = parent
        self.children = []
        self.depth = depth
        self.status = None

    def is_leaf(self):
        """Check if node is a leaf (has no children)."""
        return len(self.children) == 0


class HanziTreeBuilder:
    """
    Builder for creating character decomposition trees.
    
    Decomposes Chinese characters into their component parts.
    """

    def __init__(self, overrides=None, path_overrides=None, atomic_chars=None, max_depth=8):
        self.decomposer = get_decomposer()
        self.overrides = overrides or {}
        self.path_overrides = path_overrides or {}
        self.atomic_chars = set(atomic_chars or [])
        self.max_depth = max_depth

    def build_tree(self, node, visited=None):
        """
        Build decomposition tree recursively.
        
        Args:
            node: HanziNode to decompose
            visited: Set of already visited characters (to prevent cycles)
        """
        if visited is None:
            visited = set()

        # Stop at max depth
        if node.depth >= self.max_depth:
            return

        # Stop on cycles
        if node.character in visited:
            return

        # 1️⃣ EDGE-LOCAL OVERRIDE (parent → child)
        if node.parent:
            key = (node.parent.character, node.character)
            if key in self.path_overrides:
                new_char = self.path_overrides[key]
                print(
                    f"[Edge-Correct] {node.parent.character} → "
                    f"{node.character} ⇒ {new_char}"
                )
                node.character = new_char

        # 2️⃣ GLOBAL OVERRIDE
        if node.character in self.overrides:
            node.character = self.overrides[node.character]

        # 3️⃣ ATOMIC STOP (AFTER override)
        if node.character in self.atomic_chars:
            return

        visited.add(node.character)

        # 4️⃣ DECOMPOSITION
        try:
            result = self.decomposer.decompose(node.character, 1)
            components = result.get("components", [])
        except Exception:
            return

        if not components or components == [node.character]:
            return

        for comp in components:
            child = HanziNode(
                character=comp,
                parent=node,
                depth=node.depth + 1
            )
            node.children.append(child)
            self.build_tree(child, visited.copy())


def print_tree(node, indent=0):
    """Print tree structure."""
    prefix = "  " * indent
    print(f"{prefix}- {node.character} (id={node.id}, depth={node.depth})")
    for child in node.children:
        print_tree(child, indent + 1)


def traverse_tree(root):
    """
    Traverse and collect all nodes in the tree (DFS).
    
    Returns:
        List of tuples (char, depth, parent_char)
    """
    result = []

    def _dfs(node):
        parent_char = node.parent.character if node.parent else None
        result.append((node.character, node.depth, parent_char))
        for child in node.children:
            _dfs(child)

    _dfs(root)
    return result


def build_dependency_map_full(tree_nodes, target_char):
    """
    Build a map of character dependencies.
    
    Args:
        tree_nodes: List of (char, depth, parent) tuples
        target_char: Target character (not used but kept for compatibility)
        
    Returns:
        Dictionary mapping parent -> [children]
    """
    dep_map = defaultdict(list)

    for char, depth, parent in tree_nodes:
        if parent is not None:
            dep_map[parent].append(char)

    return dict(dep_map)


def analyze_character_v3(character, builder, learned_chars):
    """
    Analyze a character and its dependencies.
    
    Args:
        character: Character to analyze
        builder: HanziTreeBuilder instance
        learned_chars: Set of already learned characters
        
    Returns:
        Dictionary with analysis results including required radicals, known radicals,
        ready-to-learn characters, dependencies, and root node
    """
    root = HanziNode(character)
    builder.build_tree(root)

    tree_nodes = traverse_tree(root)

    required = set()
    known = set()
    ready = set()

    # For quick access: char -> [children]
    dep_map = build_dependency_map_full(tree_nodes, character)

    for char, _, _ in tree_nodes:
        if char == character:
            continue
        if char in learned_chars:
            known.add(char)
        else:
            required.add(char)

    # Calculate READY characters
    for char in required:
        children = dep_map.get(char, [])

        # Leaf or all children known → READY
        if all(child in learned_chars for child in children):
            ready.add(char)

    # If the root itself is not learned and all its children are learned,
    # the root is ready to learn.
    root_children = dep_map.get(character, [])
    if character not in learned_chars and root_children:
        if all(child in learned_chars for child in root_children):
            ready.add(character)

    # If the root has no children, it is a standalone character.
    if character not in learned_chars and not root_children:
        ready.add(character)

    return {
        "character": character,
        "required_radicals": sorted(required),
        "known_radicals": sorted(known),
        "ready": sorted(ready),
        "dependencies": dep_map,
        "root": root
    }


def compute_status(node, learned_chars):
    """
    Compute the learning status of a node.
    
    Args:
        node: HanziNode to compute status for
        learned_chars: Set of learned characters
        
    Returns:
        Status string: 'learned', 'ready', or 'blocked'
    """
    # Leaf node
    if not node.children:
        node.status = "learned" if node.character in learned_chars else "ready"
        return node.status

    child_statuses = [compute_status(c, learned_chars) for c in node.children]

    if node.character in learned_chars:
        node.status = "learned"
    elif all(s == "learned" for s in child_statuses):
        node.status = "ready"
    else:
        node.status = "blocked"

    return node.status


def print_tree_with_status(node, indent="", is_last=True):
    """
    Print tree with learning status for each node.
    
    Args:
        node: HanziNode to print
        indent: Current indentation string
        is_last: Whether this is the last child
    """
    marker = "└─ " if is_last else "├─ "

    symbol = {
        "learned": "✅",
        "ready": "🟡",
        "blocked": "🔴"
    }[node.status]

    print(indent + marker + f"{node.character} {symbol}")

    indent += "   " if is_last else "│  "

    for i, child in enumerate(node.children):
        print_tree_with_status(
            child,
            indent,
            i == len(node.children) - 1
        )
