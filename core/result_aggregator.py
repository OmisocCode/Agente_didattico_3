"""
Result Aggregator module for Multi-Agent System.

Aggregates and combines results from multiple agents using various strategies.
"""

import logging
from typing import Any, Dict, List, Optional
from collections import Counter
from statistics import mean, median
from enum import Enum

logger = logging.getLogger(__name__)


class AggregationStrategy(Enum):
    """Strategies for aggregating results."""
    CONSENSUS = "consensus"  # Majority vote
    WEIGHTED = "weighted"  # Weighted average by confidence
    ENSEMBLE = "ensemble"  # Combine all results
    BEST = "best"  # Take best result by score
    FIRST = "first"  # Take first result
    MERGE = "merge"  # Merge results into single structure


class AgentResult:
    """
    Wrapper for agent result with metadata.

    Attributes:
        agent_id: Agent identifier
        agent_type: Type of agent
        value: The actual result value
        confidence: Confidence score (0-1)
        timestamp: Result timestamp
        metadata: Additional metadata
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        value: Any,
        confidence: float = 1.0,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize agent result."""
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.value = value
        self.confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
        self.timestamp = timestamp
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"AgentResult(agent={self.agent_type}, confidence={self.confidence:.2f})"


class ResultAggregator:
    """
    Aggregates results from multiple agents.

    Supports various aggregation strategies:
    - Consensus: Majority vote
    - Weighted: Weighted average by confidence
    - Ensemble: Combine all results
    - Best: Select best result by score
    - First: Take first available result
    - Merge: Merge results into single structure
    """

    def aggregate(
        self,
        results: List[AgentResult],
        strategy: AggregationStrategy = AggregationStrategy.CONSENSUS
    ) -> Any:
        """
        Aggregate results using specified strategy.

        Args:
            results: List of agent results
            strategy: Aggregation strategy

        Returns:
            Aggregated result
        """
        if not results:
            logger.warning("No results to aggregate")
            return None

        if len(results) == 1:
            return results[0].value

        logger.info(f"Aggregating {len(results)} results using {strategy.value} strategy")

        if strategy == AggregationStrategy.CONSENSUS:
            return self._consensus(results)
        elif strategy == AggregationStrategy.WEIGHTED:
            return self._weighted(results)
        elif strategy == AggregationStrategy.ENSEMBLE:
            return self._ensemble(results)
        elif strategy == AggregationStrategy.BEST:
            return self._best(results)
        elif strategy == AggregationStrategy.FIRST:
            return self._first(results)
        elif strategy == AggregationStrategy.MERGE:
            return self._merge(results)
        else:
            logger.error(f"Unknown aggregation strategy: {strategy}")
            return results[0].value

    def _consensus(self, results: List[AgentResult]) -> Any:
        """
        Consensus aggregation (majority vote).

        Args:
            results: List of agent results

        Returns:
            Most common result value
        """
        values = [r.value for r in results]

        # For simple values, use Counter
        if all(isinstance(v, (str, int, bool, type(None))) for v in values):
            counter = Counter(values)
            most_common = counter.most_common(1)[0]
            logger.debug(f"Consensus: {most_common[0]} (count: {most_common[1]})")
            return most_common[0]

        # For complex values, use confidence-weighted voting
        return self._weighted(results)

    def _weighted(self, results: List[AgentResult]) -> Any:
        """
        Weighted aggregation by confidence.

        Args:
            results: List of agent results

        Returns:
            Weighted result
        """
        # For numeric values, compute weighted average
        values = [r.value for r in results]

        if all(isinstance(v, (int, float)) for v in values):
            weighted_sum = sum(r.value * r.confidence for r in results)
            total_confidence = sum(r.confidence for r in results)

            if total_confidence > 0:
                result = weighted_sum / total_confidence
                logger.debug(f"Weighted average: {result:.4f}")
                return result

        # For non-numeric, return highest confidence result
        return max(results, key=lambda r: r.confidence).value

    def _ensemble(self, results: List[AgentResult]) -> List[Any]:
        """
        Ensemble aggregation (combine all results).

        Args:
            results: List of agent results

        Returns:
            List of all result values
        """
        return [r.value for r in results]

    def _best(self, results: List[AgentResult]) -> Any:
        """
        Select best result by confidence score.

        Args:
            results: List of agent results

        Returns:
            Result with highest confidence
        """
        best_result = max(results, key=lambda r: r.confidence)
        logger.debug(f"Best result from {best_result.agent_type} (confidence: {best_result.confidence:.2f})")
        return best_result.value

    def _first(self, results: List[AgentResult]) -> Any:
        """
        Take first result.

        Args:
            results: List of agent results

        Returns:
            First result value
        """
        return results[0].value

    def _merge(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Merge results into single dictionary.

        Args:
            results: List of agent results

        Returns:
            Merged dictionary
        """
        merged = {}

        for result in results:
            if isinstance(result.value, dict):
                # Merge dictionaries
                for key, value in result.value.items():
                    if key not in merged:
                        merged[key] = value
                    elif isinstance(merged[key], list):
                        if isinstance(value, list):
                            merged[key].extend(value)
                        else:
                            merged[key].append(value)
                    else:
                        merged[key] = [merged[key], value]
            else:
                # Add as agent-specific key
                merged[result.agent_type] = result.value

        return merged

    def aggregate_numeric(self, results: List[AgentResult], method: str = "mean") -> float:
        """
        Aggregate numeric results.

        Args:
            results: List of agent results with numeric values
            method: Aggregation method (mean, median, min, max, sum)

        Returns:
            Aggregated numeric value
        """
        values = [r.value for r in results if isinstance(r.value, (int, float))]

        if not values:
            logger.warning("No numeric values to aggregate")
            return 0.0

        if method == "mean":
            return mean(values)
        elif method == "median":
            return median(values)
        elif method == "min":
            return min(values)
        elif method == "max":
            return max(values)
        elif method == "sum":
            return sum(values)
        else:
            logger.error(f"Unknown numeric method: {method}")
            return mean(values)

    def aggregate_lists(self, results: List[AgentResult], unique: bool = False) -> List[Any]:
        """
        Aggregate list results.

        Args:
            results: List of agent results with list values
            unique: Whether to remove duplicates

        Returns:
            Combined list
        """
        combined = []

        for result in results:
            if isinstance(result.value, list):
                combined.extend(result.value)
            else:
                combined.append(result.value)

        if unique:
            # Remove duplicates while preserving order
            seen = set()
            unique_list = []
            for item in combined:
                # For unhashable types, just add
                try:
                    if item not in seen:
                        seen.add(item)
                        unique_list.append(item)
                except TypeError:
                    unique_list.append(item)
            return unique_list

        return combined

    def aggregate_dicts(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Aggregate dictionary results by merging.

        Args:
            results: List of agent results with dict values

        Returns:
            Merged dictionary
        """
        return self._merge(results)

    def get_confidence_weighted_result(
        self,
        results: List[AgentResult],
        threshold: float = 0.5
    ) -> Optional[Any]:
        """
        Get result only if confidence exceeds threshold.

        Args:
            results: List of agent results
            threshold: Minimum confidence threshold

        Returns:
            Result if confidence >= threshold, else None
        """
        # Get best result
        if not results:
            return None

        best = max(results, key=lambda r: r.confidence)

        if best.confidence >= threshold:
            logger.debug(f"Confidence {best.confidence:.2f} exceeds threshold {threshold}")
            return best.value
        else:
            logger.debug(f"Confidence {best.confidence:.2f} below threshold {threshold}")
            return None

    def analyze_agreement(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Analyze agreement level among results.

        Args:
            results: List of agent results

        Returns:
            Dictionary with agreement analysis
        """
        if len(results) < 2:
            return {
                "agreement_level": 1.0,
                "num_unique_values": len(results),
                "majority_value": results[0].value if results else None
            }

        values = [r.value for r in results]

        # Count unique values
        value_counts = Counter(values)
        most_common = value_counts.most_common(1)[0]

        # Agreement level = proportion agreeing with majority
        agreement_level = most_common[1] / len(results)

        return {
            "agreement_level": agreement_level,
            "num_unique_values": len(value_counts),
            "majority_value": most_common[0],
            "majority_count": most_common[1],
            "total_results": len(results),
            "value_distribution": dict(value_counts)
        }
