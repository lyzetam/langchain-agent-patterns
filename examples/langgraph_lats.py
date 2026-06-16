"""
LATS (Language Agent Tree Search) Example
=========================================
A Monte Carlo Tree Search-based agent that explores multiple reasoning paths.

Based on Zhou et al.'s LATS paper. Combines:
- Reflection/evaluation
- Tree search (Monte Carlo)
- Reward backpropagation

Steps:
1. Select: Pick best node by UCB (upper confidence bound)
2. Expand: Generate candidate next actions
3. Reflect+Evaluate: Score each candidate
4. Backpropagate: Update scores up the tree
"""

import math
from collections import deque
from typing import Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ============ Data Structures ============

class Reflection(BaseModel):
    """Reflection on a candidate response."""
    reflections: str = Field(
        description="Critique and reflections on the response quality"
    )
    score: int = Field(
        description="Score from 0-10",
        ge=0,
        le=10
    )
    found_solution: bool = Field(
        description="Whether this response solves the problem"
    )
    
    def as_message(self):
        return HumanMessage(
            content=f"Reflection: {self.reflections}\nScore: {self.score}"
        )
    
    @property
    def normalized_score(self) -> float:
        return self.score / 10.0


class Node:
    """Tree node for LATS."""
    
    def __init__(
        self,
        messages: list[BaseMessage],
        reflection: Optional[Reflection] = None,
        parent: Optional["Node"] = None
    ):
        self.messages = messages
        self.parent = parent
        self.children = []
        self.value = 0.0
        self.visits = 0
        self.reflection = reflection
        self.depth = parent.depth + 1 if parent else 1
        
        # Track if solution found
        self._is_solved = reflection.found_solution if reflection else False
        if self._is_solved:
            self._mark_tree_as_solved()
        
        # Backpropagate initial score
        if reflection:
            self.backpropagate(reflection.normalized_score)
    
    def upper_confidence_bound(self, exploration_weight: float = 1.0) -> float:
        """Calculate UCT score for node selection."""
        if self.parent is None:
            raise ValueError("Cannot calculate UCT for root node")
        
        if self.visits == 0:
            return self.value
        
        # Exploitation: average reward
        average_reward = self.value / self.visits
        
        # Exploration: less visited nodes
        exploration_term = math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        
        return average_reward + exploration_weight * exploration_term
    
    def backpropagate(self, reward: float):
        """Update node value and propagate up the tree."""
        node = self
        while node:
            node.visits += 1
            # Running average
            node.value = (node.value * (node.visits - 1) + reward) / node.visits
            node = node.parent
    
    def get_trajectory(self) -> list[BaseMessage]:
        """Get full message trajectory from root to this node."""
        messages = []
        node = self
        while node:
            messages.extend(node.messages[::-1])
            node = node.parent
        return messages[::-1]
    
    def get_best_solution(self) -> "Node":
        """Find best terminal node in subtree."""
        all_nodes = [self] + list(self._get_all_children())
        best = max(
            all_nodes,
            key=lambda n: int(n.is_terminal and n.is_solved) * n.value
        )
        return best
    
    def _get_all_children(self):
        """Get all descendants."""
        all_nodes = []
        queue = deque([self])
        while queue:
            node = queue.popleft()
            all_nodes.extend(node.children)
            queue.extend(node.children)
        return all_nodes
    
    def _mark_tree_as_solved(self):
        """Mark all ancestors as having a solution."""
        parent = self.parent
        while parent:
            parent._is_solved = True
            parent = parent.parent
    
    @property
    def is_solved(self) -> bool:
        return self._is_solved
    
    @property
    def is_terminal(self) -> bool:
        return not self.children
    
    def __repr__(self):
        return (
            f"<Node value={self.value:.2f}, visits={self.visits}, "
            f"depth={self.depth}, solved={self.is_solved}>"
        )


# ============ State ============

class TreeState(TypedDict):
    """State for LATS."""
    root: Node
    input: str
    candidate_count: int
    max_depth: int
    current_rollout: int
    max_rollouts: int


# ============ LLMs ============

llm = init_chat_model("anthropic:claude-sonnet-4-6", temperature=0.7)


# ============ Nodes ============

def select(state: TreeState) -> Node:
    """Select node with highest UCB."""
    root = state["root"]
    
    # If root has no children, select root
    if not root.children:
        return root
    
    # Find leaf with highest UCB
    node = root
    while node.children:
        # Select child with highest UCB
        node = max(node.children, key=lambda n: n.upper_confidence_bound())
    
    return node


def expand(state: TreeState):
    """Expand node by generating candidate actions."""
    node = select(state)
    
    print(f"\n🔍 Selecting node at depth {node.depth} (value={node.value:.2f}, visits={node.visits})")
    
    if node.depth >= state["max_depth"]:
        print(f"   Max depth reached, not expanding")
        return {"root": state["root"]}
    
    # Generate candidate next steps
    trajectory = node.get_trajectory()
    messages = trajectory + [HumanMessage(content="What are possible next steps? Generate 3 options.")]
    
    print(f"   Generating {state['candidate_count']} candidates...")
    
    for i in range(state["candidate_count"]):
        # Generate candidate
        response = llm.invoke(messages)
        
        # Evaluate candidate
        evaluation_prompt = f"""Evaluate this response for quality and correctness:
        
{response.content}

Score 0-10 and indicate if it solves the problem."""
        
        evaluation = llm.with_structured_output(Reflection).invoke(evaluation_prompt)
        
        print(f"   Candidate {i+1}: score={evaluation.score}, solved={evaluation.found_solution}")
        
        # Create child node
        child = Node(
            messages=[response],
            reflection=evaluation,
            parent=node
        )
        node.children.append(child)
    
    return {"root": state["root"]}


def should_continue(state: TreeState) -> str:
    """Check if search should continue."""
    root = state["root"]
    
    # Check if we found a solution
    best = root.get_best_solution()
    if best.is_solved:
        print(f"\n✅ Found solution!")
        return END
    
    # Check max rollouts
    if state["current_rollout"] >= state["max_rollouts"]:
        print(f"\n⏹️  Max rollouts reached")
        return END
    
    return "expand"


def get_best_answer(state: TreeState):
    """Extract best answer from tree."""
    root = state["root"]
    best = root.get_best_solution()
    
    trajectory = best.get_trajectory()
    final_answer = trajectory[-1].content if trajectory else "No answer found"
    
    print(f"\n📊 Best solution from depth {best.depth}")
    print(f"   Value: {best.value:.2f}")
    print(f"   Visits: {best.visits}")
    
    return {
        "root": state["root"],
        "best_answer": final_answer
    }


# ============ Build Graph ============

def create_lats_graph(
    candidate_count: int = 3,
    max_depth: int = 5,
    max_rollouts: int = 10
):
    """Create LATS graph."""
    builder = StateGraph(TreeState)
    
    builder.add_node("expand", expand)
    builder.add_node("best_answer", get_best_answer)
    
    builder.add_edge(START, "expand")
    builder.add_conditional_edges("expand", should_continue)
    builder.add_edge("best_answer", END)
    
    return builder.compile()


# ============ Main ============

def main():
    print("=" * 60)
    print("LATS: Language Agent Tree Search")
    print("=" * 60)
    
    # Problem to solve
    problem = (
        "A farmer has 17 sheep and all but 9 die. "
        "How many sheep are left?"
    )
    
    print(f"\n🎯 Problem: {problem}")
    
    # Create initial root node
    root = Node(
        messages=[HumanMessage(content=problem)],
        reflection=None,
        parent=None
    )
    
    # Create and run graph
    graph = create_lats_graph(
        candidate_count=3,
        max_depth=4,
        max_rollouts=8
    )
    
    initial_state = {
        "root": root,
        "input": problem,
        "candidate_count": 3,
        "max_depth": 4,
        "current_rollout": 0,
        "max_rollouts": 8
    }
    
    print("\n" + "─" * 60)
    print("Running Tree Search...")
    print("─" * 60)
    
    result = graph.invoke(initial_state)
    
    # Display results
    print("\n" + "=" * 60)
    print("📄 Best Answer:")
    print("=" * 60)
    print(result.get("best_answer", "No answer found"))
    
    # Tree statistics
    root = result["root"]
    print(f"\n📊 Tree Statistics:")
    print(f"   Total nodes: {len(root._get_all_children()) + 1}")
    print(f"   Tree depth: {max(n.depth for n in [root] + list(root._get_all_children()))}")
    
    best = root.get_best_solution()
    print(f"   Best node depth: {best.depth}")
    print(f"   Best node value: {best.value:.2f}")


if __name__ == "__main__":
    main()
