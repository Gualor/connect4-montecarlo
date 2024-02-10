"""Connect4 Monte Carlo Tree Search module."""

from typing import Tuple, List, Optional
import random
import time
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
        except ValueError:
            return False

    def check_win(self) -> Tuple[bool, Optional[int]]:
        """Check wheter the match is over.

        Returns:
            Tuple[bool, int | None]: Game has ended, winner id or None.
        """
        winner = GameBoard.check_rows(self.board)
        if winner is not None:
            return (True, winner)

        winner = GameBoard.check_cols(self.board)
        if winner is not None:
            return (True, winner)

        winner = GameBoard.check_diag(self.board)
        if winner is not None:
            return (True, winner)

        if GameBoard.check_tie(self.board):
            return (True, None)

        return (False, None)

    @staticmethod
    def check_rows(board: np.ndarray) -> Optional[int]:
        """Check for winner in rows.

        Args:
            board (np.ndarray): Board game.

        Returns:
            int | None: Winner id or None.
        """
        for y in range(6):
            row = list(board[y, :])
            for x in range(4):
                if row[x : x + 4].count(row[x]) == 4:
                    if row[x] != 0:
                        return row[x]
        return None

    @staticmethod
    def check_cols(board: np.ndarray) -> Optional[int]:
        """Check for winner in columns.

        Args:
            board (np.ndarray): Board game.

        Returns:
            int | None: Winner id or None.
        """
        for x in range(7):
            col = list(board[:, x])
            for y in range(3):
                if col[y : y + 4].count(col[y]) == 4:
                    if col[y] != 0:
                        return col[y]
        return None

    @staticmethod
    def check_diag(board: np.ndarray) -> Optional[int]:
        """Check for winner in diagonals.

        Args:
            board (np.ndarray): Board game.

        Returns:
            int | None: Winner id or None.
        """
        # Right diagonal
        for point in [
            (3, 0), (4, 0), (3, 1), (5, 0), (4, 1), (3, 2), (5, 1), (4, 2),
            (3, 3), (5, 2), (4, 3), (5, 3)
        ]:
            diag = []
            for k in range(4):
                diag.append(board[point[0] - k, point[1] + k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                return diag[0]
        # Left diagonal
        for point in [
            (5, 3), (5, 4), (4, 3), (5, 5), (4, 4), (3, 3), (5, 6), (4, 5),
            (3, 4), (4, 6), (3, 5), (3, 6)
        ]:
            diag = []
            for k in range(4):
                diag.append(board[point[0] - k, point[1] - k])
            if diag.count(1) == 4 or diag.count(2) == 4:
                return diag[0]
        return None

    @staticmethod
    def check_tie(board: np.ndarray) -> bool:
        """Check if board is a tie.

        Args:
            board (np.ndarray): Board game.

        Returns:
            bool: Game is a tie.
        """
        return bool(np.all(board != 0))

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

    def compute_move(self, node: "Node") -> Tuple[int, int]:
        """Compute move using MCTS algorithm.

        Args:
            root (Node): Starting node.

        Returns:
            Tuple[int, int]: Board 2D coordinate.
        """
        time0 = time.time()
        while (time.time() - time0) < self.t:
            # selection and expansion
            leaf = self.select(node)
            if leaf is None:
                return (-1, -1)
            # simulation
            simulation_result = self.rollout(leaf)
            # backpropagation
            self.backpropagate(leaf, simulation_result)
        # from next best state get move coordinates
        selected = self.best_child(node)
        if selected is None:
            return (-1, -1)
        for j in range(6):
            for i in range(7):
                if selected.board[j][i] != node.board[j][i]:
                    return (j, i)
        return (-1, -1)

    def select(self, node: "Node") -> Optional["Node"]:
        """Node selection and expansion phase.

        Args:
            node (Node): Starting node.

        Returns:
            Node: Selected node.
        """
        # if all children of node have been expanded
        # select best one according to uct value
        while self.fully_expanded(node):
            tmp = self.select_uct(node)
            # break if select_uct returns the same node back
            if tmp == node:
                break
            node = tmp
        # if node is terminal, return it
        if node.terminal:
            return node
        # expand node and return it for rollout
        node.add_child()
        if node.children:
            return self.pick_unvisited(node.children)
        return node

    def select_uct(self, node: "Node") -> "Node":
        """Select node with best UCT value.

        Args:
            node (Node): Parent node.

        Returns:
            Node: Best child.
        """
        best_uct = -np.inf
        best_node = None
        for child in node.children:
            uct = (child.q / child.n) + 2 * np.sqrt(np.log(node.n) / child.n)
            if uct > best_uct:
                best_uct = uct
                best_node = child
        # Avoid error if node has no children
        if best_node is None:
            return node
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
                if child.n == 0:
                    visited = False
            return visited
        return False

    def pick_unvisited(self, children: List["Node"]) -> Optional["Node"]:
        """Pick first unexplored child node.

        Args:
            children (List[Node]): List of children nodes.

        Returns:
            Node: Unexplored node or None.
        """
        for child in children:
            if child.n == 0:
                return child
        return None

    def rollout(self, node: "Node") -> Optional[int]:
        """Perform a random game simulation.

        Args:
            node (Node): Starting node.

        Returns:
            int | None: Game result.
        """
        board = node.board
        turn = node.turn
        if not node.terminal:
            while True:
                # switch turn
                turn = 1 if turn == 2 else 2
                # get moves from current board
                moves = self.get_moves(board, turn)
                if moves:
                    # select next board randomly
                    board = random.choice(moves)
                    # check if state is terminal
                    terminal = self.result(board)
                    if terminal != 0:
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
        moves = []
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

    def result(self, board: np.ndarray) -> Optional[int]:
        """Get game result from terminal board.

        Args:
            board (np.ndarray): Game matrix.

        Returns:
            int | None: Winner id or None.
        """
        winner = GameBoard.check_rows(board)
        if winner is not None:
            return winner

        winner = GameBoard.check_cols(board)
        if winner is not None:
            return winner

        winner = GameBoard.check_diag(board)
        if winner is not None:
            return winner

        return None

    def backpropagate(self, node: "Node", winner: Optional[int]) -> None:
        """Update recursively node visits and scores from leaf to root.

        Args:
            node (Node): Leaf node.
            winner (int): Winner id.
        """
        # increment result by 1 if winner
        if node.turn == winner:
            node.q += 1
        # increment visit number by 1
        node.n += 1
        # stop if node is root
        if node.parent is None:
            return
        # call function recursively on parent
        self.backpropagate(node.parent, winner)

    def best_child(self, node: "Node") -> Optional["Node"]:
        """Get child node with largest number of visits.

        Args:
            node (Node): Parent node.

        Returns:
            Node | None: Best child node.
        """
        max_visit = 0
        best_node = None
        for child in node.children:
            if child.n > max_visit:
                max_visit = child.n
                best_node = child
        return best_node


class Node:
    """Monte Carlo tree node class."""

    def __init__(
        self, parent: Optional["Node"], board: np.ndarray, turn: int
    ) -> None:
        self.q = 0  # sum of rollout outcomes
        self.n = 0  # number of visits
        self.parent = parent
        self.board = board
        # root is always opponent's turn
        if turn == 1:
            self.turn = 2
        else:
            self.turn = 1
        # no children have been expanded yet
        self.children: List["Node"] = []
        self.terminal = self.check_terminal()
        self.expanded = False

    def check_terminal(self) -> bool:
        """Check whether node is a leaf.

        Returns:
            bool: Node is a leaf.
        """
        if GameBoard.check_rows(self.board):
            return True

        if GameBoard.check_cols(self.board):
            return True

        if GameBoard.check_diag(self.board):
            return True

        if GameBoard.check_tie(self.board):
            return True

        return False

    def add_child(self) -> None:
        """Add new child to node."""
        # node already expanded
        if self.expanded:
            return
        # get board of every child
        child_board = []
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
                                break
                            self.children.append(Node(self, tmp, 1))
                            return
                        else:
                            tmp[j, i] = 1
                            if child_board:
                                if not self.compare_children(tmp, child_board):
                                    self.children.append(Node(self, tmp, 2))
                                    return
                                break
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


if __name__ == "__main__":

    # Begin new game
    while True:
        game_board = GameBoard(cpu=1)
        monte_carlo = MCTS(symbol=1, t=5)

        # Game loop
        while True:
            game_board.show()

            # Check game over
            game_over, winner_id = game_board.check_win()
            if game_over is True:
                if winner_id is None:
                    print("\n\nTIE!!!")
                elif winner_id == game_board.cpu:
                    print("\n\nMONTE CARLO WON!!!")
                else:
                    print("\n\nYOU WON!!!")
                break

            # Monte Carlo turn
            if game_board.turn == monte_carlo.symbol:
                root = Node(
                    parent=None,
                    board=game_board.board,
                    turn=monte_carlo.symbol
                )
                mcts_move = monte_carlo.compute_move(root)
                game_board.board[mcts_move] = monte_carlo.symbol
                game_board.switch_turn()

            # Human turn
            else:
                game_board.play()

        # Rematch
        print("\nDo you want to play again? [Yes/No]", end=" ")
        ans = input()
        if ans not in ["Yes", "yes", "y"]:
            break
