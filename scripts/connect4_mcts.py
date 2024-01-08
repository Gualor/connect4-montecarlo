"""Connect4 Monte Carlo Tree Search module."""

from typing import Tuple, List
import random
import time
import math
import os

import numpy as np

# MCTS move computation time
PROCESS_TIME: float = 3.0


class GameBoard:
    """Connect4 game board class."""

    def __init__(self, cpu: int) -> None:
        self.turn = random.randint(1, 2)
        self.board = np.zeros(shape=(6, 7))
        self.cpu = cpu

    def show(self) -> None:
        """Print out game board on console."""
        os.system("cls")
        print("+---------------------------+")
        for j in range(5, -1, -1):
            for i in range(7):
                if self.board[j, i] == 1:
                    print("| X", end=" ")
                elif self.board[j, i] == 2:
                    print("| O", end=" ")
                else:
                    print("|  ", end=" ")
            print("|")
        print("+---------------------------+")
        print("| 1   2   3   4   5   6   7 |")
        print("+---------------------------+")
        if self.turn == self.cpu:
            print("Opponent's turn [X]")
            print("Please wait...")
        else:
            print("Your turn [O]")
            print("Enter a number between 1 and 7: ", end="")

    def play(self) -> bool:
        """Take user input and play move.

        Returns:
            bool: Move registered correctly.
        """
        try:
            move = int(input())
            if move in [1, 2, 3, 4, 5, 6, 7]:
                for i in range(6):
                    if self.board[i, move - 1] == 0:
                        self.board[i, move - 1] = self.turn
                        self.switch_turn()
                        return True
            return False
        except:
            return False

    def check_win(self) -> int | None:
        """Check wheter the match is over.

        Returns:
            int | None: Winner id or None.
        """
        # check rows
        for y in range(6):
            row = list(self.board[y, :])
            for x in range(4):
                if row[x : x + 4].count(row[x]) == 4:
                    if row[x] != 0:
                        return row[x]
        # check columns
        for x in range(7):
            col = list(self.board[:, x])
            for y in range(3):
                if col[y : y + 4].count(col[y]) == 4:
                    if col[y] != 0:
                        return col[y]
        # check right diagonals
        points = [(3, 0), (4, 0), (3, 1), (5, 0), (4, 1), (3, 2), (5, 1),
                  (4, 2), (3, 3), (5, 2), (4, 3), (5, 3)]
        for point in points:
            diag = []
            for k in range(4):
                diag.append(self.board[point[0] - k, point[1] + k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                return diag[0]
        # check left diagonals
        points = [(5, 3), (5, 4), (4, 3), (5, 5), (4, 4), (3, 3), (5, 6),
                  (4, 5), (3, 4), (4, 6), (3, 5), (3, 6)]
        for point in points:
            diag = []
            for k in range(4):
                diag.append(self.board[point[0] - k, point[1] - k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                return diag[0]
        # no winner
        return None

    def apply_move(self, column: int) -> bool:
        """Apply move to board.

        Args:
            column (int): Selected column index.

        Returns:
            bool: Move applied successfully.
        """
        for i in range(6):
            if self.board[i, column - 1] == 0:
                self.board[i, column - 1] = self.turn
                self.switch_turn()
                return True
        return False

    def switch_turn(self) -> None:
        """Switch turn between players."""
        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1


class MCTS:
    """Monte Carlo Tree search class."""

    def __init__(self, symbol: int, t: float) -> None:
        self.symbol = symbol
        self.t = t

    def compute_move(self, node: "Node") -> Tuple[int, int] | None:
        """Compute move using MCTS algorithm.

        Args:
            root (Node): Starting node.

        Returns:
            Tuple[int, int] | None: Board 2D coordinate.
        """
        time0 = time.time()
        while (time.time() - time0) < self.t:
            # selection and expansion
            leaf = self.select(node)
            # simulation
            simulation_result = self.rollout(leaf)
            # backpropagation
            self.backpropagate(leaf, simulation_result)
        # from next best state get move coordinates
        selected = self.best_child(node)
        for j in range(6):
            for i in range(7):
                if selected.board[j][i] != node.board[j][i]:
                    return (j, i)
        return None

    def select(self, node: "Node") -> "Node":
        """Node selection and expansion phase.

        Args:
            node (Node): Starting node.

        Returns:
            Node: Selected node.
        """
        # if all children of node has been expanded
        # select best one according to uct value
        while self.fully_expanded(node):
            tmp = self.select_uct(node)
            # if select_uct returns back the node break
            if tmp == node:
                break
            # if not, keep exploring the tree
            else:
                node = tmp
        # if node is terminal, return it
        if node.terminal:
            return node
        else:
            # expand node and return it for rollout
            node.add_child()
            if node.children:
                return self.pick_unvisited(node.children)
            else:
                return node

    def select_uct(self, node: "Node") -> "Node":
        """Select node with best UCT value.

        Args:
            node (Node): Parent node.

        Returns:
            Node: Best child.
        """
        best_uct = -10000000
        best_node = None
        for child in node.children:
            uct = (child.Q / child.N) + \
                2 * math.sqrt((math.log(node.N)) / child.N)
            if uct > best_uct:
                best_uct = uct
                best_node = child
        # Avoid error if node has no children
        if best_node is None:
            return node
        else:
            return best_node

    def fully_expanded(self, node: "Node") -> bool:
        """Check whether a node is fully expanded.

        Args:
            node (Node): Node to be checked.

        Returns:
            bool: Node is fully expanded.
        """
        visited = True
        # max number of children a node can have
        if list(node.board[5]).count(0) == len(node.children):
            # check if every node has been visited
            for child in node.children:
                if child.N == 0:
                    visited = False
            return visited
        else:
            return False

    def pick_unvisited(self, children: List["Node"]) -> "Node" | None:
        """Pick first unexplored child node.

        Args:
            children (List[Node]): List of children nodes.

        Returns:
            Node: Unexplored node or None.
        """
        for child in children:
            if child.N == 0:
                return child
        return None

    def rollout(self, node: "Node") -> int:
        """Perform a random game simulation.

        Args:
            node (Node): Starting node.

        Returns:
            int: Game result.
        """
        board = node.board
        turn = node.turn
        if not node.terminal:
            while True:
                # switch turn
                if turn == 1:
                    turn = 2
                else:
                    turn = 1
                # get moves from current board
                moves = self.get_moves(board, turn)
                if moves:
                    # select next board randomly
                    board = random.choice(moves)
                    # check if state is terminal
                    terminal = self.result(board)
                    if terminal != 0:
                        # print("rollout", board)
                        return terminal
                # with no moves left return result
                else:
                    return self.result(board)
        else:
            # if node is already terminal return result
            return self.result(board)

    def get_moves(self, board: np.ndarray, turn: int) -> List[np.ndarray]:
        """Get all possible next states.

        Args:
            board (np.ndarray): Game matrix.
            turn (int): Player id.

        Returns:
            List[np.ndarray]: List of new matrices.
        """
        moves = list()
        for i in range(7):
            if board[5, i] == 0:
                for j in range(6):
                    if board[j, i] == 0:
                        tmp = board.copy()
                        if turn == 1:
                            tmp[j, i] = 2
                        else:
                            tmp[j, i] = 1
                        moves.append(tmp)
                        break
        return moves

    def result(self, board: np.ndarray) -> int:
        """Get game result from board.

        Args:
            board (np.ndarray): Game matrix.

        Returns:
            int: Game result.
        """
        winner = None
        # check rows
        for y in range(6):
            row = list(board[y, :])
            for x in range(4):
                if row[x : x + 4].count(row[x]) == 4:
                    if row[x] != 0:
                        winner = row[x]
        # check columns
        for x in range(7):
            col = list(board[:, x])
            for y in range(3):
                if col[y : y + 4].count(col[y]) == 4:
                    if col[y] != 0:
                        winner = col[y]
        # check right diagonals
        points = [(3, 0), (4, 0), (3, 1), (5, 0), (4, 1), (3, 2), (5, 1),
                  (4, 2), (3, 3), (5, 2), (4, 3), (5, 3)]
        for point in points:
            diag = []
            for k in range(4):
                diag.append(board[point[0] - k, point[1] + k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                winner = diag[k]
        # check left diagonals
        points = [(5, 3), (5, 4), (4, 3), (5, 5), (4, 4), (3, 3), (5, 6),
                  (4, 5), (3, 4), (4, 6), (3, 5), (3, 6),]
        for point in points:
            diag = list()
            for k in range(4):
                diag.append(board[point[0] - k, point[1] - k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                winner = diag[k]
        # Tie
        if winner is None:
            return 0
        else:
            # Win
            if self.symbol == winner:
                return 1
            # Defeat
            else:
                return -1

    def backpropagate(self, node: "Node", result: int) -> None:
        """Update recursively node visits and scores from leaf to root.

        Args:
            node (Node): Leaf node.
            result (int): Game result of leaf node.
        """
        # add result when AI's turn
        if node.turn == self.symbol:
            node.Q += result
        # or else subtract it
        else:
            node.Q -= result
        # increment visit number by 1
        node.N += 1
        # stop if node is root
        if node.parent is None:
            return
        else:
            # call function recursively on parent
            self.backpropagate(node.parent, result)

    def best_child(self, node: "Node") -> "Node" | None:
        """Get child node with largest number of visits.

        Args:
            node (Node): Parent node.

        Returns:
            Node | None: Best child node.
        """
        max_visit = 0
        best_node = None
        for child in node.children:
            if child.N > max_visit:
                max_visit = child.N
                best_node = child
        return best_node


class Node:
    """Monte Carlo tree node class."""

    def __init__(
        self, parent: "Node" | None, board: np.ndarray, turn: int
    ) -> None:
        self.Q = 0  # sum of rollout outcomes
        self.N = 0  # number of visits
        self.parent = parent
        self.board = board
        # root is always opponent's turn
        if turn == 1:
            self.turn = 2
        else:
            self.turn = 1
        # no children has been expanded yet
        self.children = []
        self.expanded = False
        self.terminal = self.check_terminal()

    def check_terminal(self) -> bool:
        """Check whether node is a leaf.

        Returns:
            bool: Node is a leaf.
        """
        # check rows
        for y in range(6):
            row = list(self.board[y, :])
            for x in range(4):
                if row[x : x + 4].count(row[x]) == 4:
                    if row[x] != 0:
                        return True
        # check columns
        for x in range(7):
            col = list(self.board[:, x])
            for y in range(3):
                if col[y : y + 4].count(col[y]) == 4:
                    if col[y] != 0:
                        return True
        # check right diagonals
        points = [(3, 0), (4, 0), (3, 1), (5, 0), (4, 1), (3, 2), (5, 1),
                  (4, 2), (3, 3), (5, 2), (4, 3), (5, 3)]
        for point in points:
            diag = list()
            for k in range(4):
                diag.append(self.board[point[0] - k, point[1] + k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                return True
        # check left diagonals
        points = [(5, 3), (5, 4), (4, 3), (5, 5), (4, 4), (3, 3), (5, 6),
                  (4, 5), (3, 4), (4, 6), (3, 5), (3, 6)]
        for point in points:
            diag = []
            for k in range(4):
                diag.append(self.board[point[0] - k, point[1] - k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                return True
        # no moves left
        if np.all(self.board != 0):
            return True
        # no winner
        return False

    def add_child(self) -> None:
        """Add new child to node."""
        # node already expanded
        if self.expanded:
            return
        # get board of every child
        child_board = list()
        for child in self.children:
            child_board.append(child.board)
        # find new child
        for i in range(7):
            if self.board[5, i] == 0:
                for j in range(6):
                    if self.board[j, i] == 0:
                        tmp = self.board.copy()
                        if self.turn == 1:
                            tmp[j, i] = 2
                            if child_board:
                                if not self.compare_children(tmp, child_board):
                                    self.children.append(Node(self, tmp, 1))
                                    return
                                else:
                                    break
                            else:
                                self.children.append(Node(self, tmp, 1))
                                return
                        else:
                            tmp[j, i] = 1
                            if child_board:
                                if not self.compare_children(tmp, child_board):
                                    self.children.append(Node(self, tmp, 2))
                                    return
                                else:
                                    break
                            else:
                                self.children.append(Node(self, tmp, 2))
                                return
        # no more children
        self.expanded = True
        return

    def compare_children(
        self, new_child: np.ndarray, children: List[np.ndarray]
    ) -> bool:
        """Check if node state is equal to one of children state.

        Args:
            new_child (Node): _description_
            children (List[Node]): _description_

        Returns:
            bool: _description_
        """
        for child in children:
            if (new_child == child).all():
                return True
        return False


# Run this script to play Connect 4 against Monte Carlo AI
# with graphics printed out on the console with ASCII characters
if __name__ == "__main__":
    # Begin new game
    while True:
        # Classes declaration
        gameBoard = GameBoard(cpu=1)
        monteCarlo = MCTS(symbol=1, t=5)

        # Game loop
        while True:
            # Print out the updated game board
            gameBoard.show()

            # Check game over
            winner = gameBoard.check_win()
            if winner is not None:
                if winner == gameBoard.cpu:
                    print("\n\nMONTE CARLO WON!!!")
                else:
                    print("\n\nYOU WON!!!")
                break
            else:
                if list(gameBoard.board.flatten()).count(0) == 0:
                    print("\n\nTIE!!!")
                    break

            # Monte Carlo turn
            if gameBoard.turn == monteCarlo.symbol:
                # initialiaze root node
                root = Node(
                    parent=None, board=gameBoard.board, turn=monteCarlo.symbol)
                # compute best move with monte carlo tree search
                move = monteCarlo.compute_move(root)
                # update game board
                gameBoard.board[move[0], move[1]] = monteCarlo.symbol
                gameBoard.switch_turn()
            # Human turn
            else:
                gameBoard.play()

        # Rematch
        print("\n\nDo you want to play again? [Yes/No]", end=" ")
        ans = input()
        if ans in ["Yes", "yes", "y"]:
            continue
        else:
            break
