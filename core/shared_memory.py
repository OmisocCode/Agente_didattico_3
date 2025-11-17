"""
Shared Memory module for Multi-Agent System.

Implements the Blackboard pattern where agents can read and write shared data.
Supports observers, locking for thread-safety, and optional persistence.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """
    Entry in shared memory.

    Attributes:
        value: The actual data stored
        author: ID of the agent that wrote this value
        timestamp: When the value was written
        version: Version number (incremented on each update)
        metadata: Additional metadata
    """

    value: Any
    author: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "value": self.value,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary."""
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class SharedMemory:
    """
    Shared memory implementation using the Blackboard pattern.

    Allows multiple agents to:
    - Read and write shared data
    - Subscribe to changes (observer pattern)
    - Lock specific keys for exclusive access
    - Persist data to disk (optional)

    Thread-safe using locks.
    """

    def __init__(
        self,
        enable_persistence: bool = False,
        persistence_path: Optional[Path] = None,
    ):
        """
        Initialize shared memory.

        Args:
            enable_persistence: Whether to persist data to disk
            persistence_path: Path to persistence file
        """
        # Main data store (key -> MemoryEntry)
        self.data: Dict[str, MemoryEntry] = {}

        # Lock for thread-safe operations
        self._global_lock = RLock()

        # Per-key locks for fine-grained locking
        self._key_locks: Dict[str, Lock] = {}

        # Observers for change notifications (key -> list of callbacks)
        self._observers: Dict[str, List[Callable]] = {}

        # Persistence settings
        self.enable_persistence = enable_persistence
        self.persistence_path = persistence_path

        # Statistics
        self.stats = {
            "reads": 0,
            "writes": 0,
            "deletes": 0,
            "notifications_sent": 0,
        }

        # Load from persistence if enabled
        if enable_persistence and persistence_path:
            self._load_from_disk()

        logger.info(
            f"SharedMemory initialized "
            f"(persistence: {enable_persistence}, path: {persistence_path})"
        )

    def write(
        self,
        key: str,
        value: Any,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Write a value to shared memory.

        Args:
            key: The key to write to
            value: The value to store
            agent_id: ID of the agent writing the value
            metadata: Optional metadata
        """
        with self._global_lock:
            # Get or create key-specific lock
            if key not in self._key_locks:
                self._key_locks[key] = Lock()

            with self._key_locks[key]:
                # Update existing entry or create new one
                if key in self.data:
                    # Increment version
                    old_entry = self.data[key]
                    new_version = old_entry.version + 1
                else:
                    new_version = 1

                # Create new entry
                entry = MemoryEntry(
                    value=value,
                    author=agent_id,
                    timestamp=datetime.now(),
                    version=new_version,
                    metadata=metadata or {},
                )

                self.data[key] = entry

                # Update statistics
                self.stats["writes"] += 1

                logger.debug(
                    f"Write to shared memory: key={key}, "
                    f"author={agent_id}, version={new_version}"
                )

                # Notify observers
                self._notify_observers(key, entry)

                # Persist if enabled
                if self.enable_persistence:
                    self._save_to_disk()

    def read(self, key: str, default: Any = None) -> Any:
        """
        Read a value from shared memory.

        Args:
            key: The key to read
            default: Default value if key doesn't exist

        Returns:
            The value stored at the key, or default if not found
        """
        with self._global_lock:
            entry = self.data.get(key)

            if entry is None:
                logger.debug(f"Read from shared memory: key={key} (not found)")
                return default

            # Update statistics
            self.stats["reads"] += 1

            logger.debug(
                f"Read from shared memory: key={key}, "
                f"author={entry.author}, version={entry.version}"
            )

            return entry.value

    def read_entry(self, key: str) -> Optional[MemoryEntry]:
        """
        Read the full memory entry (including metadata).

        Args:
            key: The key to read

        Returns:
            The MemoryEntry, or None if not found
        """
        with self._global_lock:
            return self.data.get(key)

    def delete(self, key: str) -> bool:
        """
        Delete a key from shared memory.

        Args:
            key: The key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        with self._global_lock:
            if key in self.data:
                del self.data[key]

                # Remove key lock
                if key in self._key_locks:
                    del self._key_locks[key]

                # Remove observers for this key
                if key in self._observers:
                    del self._observers[key]

                # Update statistics
                self.stats["deletes"] += 1

                logger.debug(f"Deleted from shared memory: key={key}")

                # Persist if enabled
                if self.enable_persistence:
                    self._save_to_disk()

                return True

            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in shared memory.

        Args:
            key: The key to check

        Returns:
            True if key exists, False otherwise
        """
        with self._global_lock:
            return key in self.data

    def keys(self) -> List[str]:
        """
        Get all keys in shared memory.

        Returns:
            List of all keys
        """
        with self._global_lock:
            return list(self.data.keys())

    def subscribe(self, key: str, callback: Callable[[str, MemoryEntry], None]) -> None:
        """
        Subscribe to changes for a specific key.

        Args:
            key: The key to subscribe to
            callback: Function to call when key changes (receives key and new entry)
        """
        with self._global_lock:
            if key not in self._observers:
                self._observers[key] = []

            self._observers[key].append(callback)
            logger.debug(f"Observer subscribed to key: {key}")

    def unsubscribe(self, key: str, callback: Callable) -> None:
        """
        Unsubscribe from changes for a specific key.

        Args:
            key: The key to unsubscribe from
            callback: The callback function to remove
        """
        with self._global_lock:
            if key in self._observers:
                try:
                    self._observers[key].remove(callback)
                    logger.debug(f"Observer unsubscribed from key: {key}")
                except ValueError:
                    logger.warning(f"Callback not found for key: {key}")

    def _notify_observers(self, key: str, entry: MemoryEntry) -> None:
        """
        Notify all observers of a key change.

        Args:
            key: The key that changed
            entry: The new entry
        """
        if key in self._observers:
            for callback in self._observers[key]:
                try:
                    callback(key, entry)
                    self.stats["notifications_sent"] += 1
                except Exception as e:
                    logger.error(f"Error in observer callback for key {key}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get shared memory statistics.

        Returns:
            Dictionary with statistics
        """
        with self._global_lock:
            return {
                **self.stats,
                "total_keys": len(self.data),
                "total_observers": sum(len(obs) for obs in self._observers.values()),
            }

    def clear(self) -> None:
        """
        Clear all data from shared memory.
        """
        with self._global_lock:
            self.data.clear()
            self._key_locks.clear()
            self._observers.clear()

            logger.info("SharedMemory cleared")

            # Persist if enabled
            if self.enable_persistence:
                self._save_to_disk()

    def _save_to_disk(self) -> None:
        """
        Save shared memory to disk.
        """
        if not self.persistence_path:
            return

        try:
            # Ensure directory exists
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert data to serializable format
            data_dict = {
                key: entry.to_dict()
                for key, entry in self.data.items()
            }

            # Write to file
            with open(self.persistence_path, "w") as f:
                json.dump(data_dict, f, indent=2, default=str)

            logger.debug(f"SharedMemory saved to {self.persistence_path}")

        except Exception as e:
            logger.error(f"Error saving SharedMemory to disk: {e}")

    def _load_from_disk(self) -> None:
        """
        Load shared memory from disk.
        """
        if not self.persistence_path or not self.persistence_path.exists():
            return

        try:
            with open(self.persistence_path, "r") as f:
                data_dict = json.load(f)

            # Convert back to MemoryEntry objects
            for key, entry_dict in data_dict.items():
                self.data[key] = MemoryEntry.from_dict(entry_dict)

            logger.info(
                f"SharedMemory loaded from {self.persistence_path} "
                f"({len(self.data)} keys)"
            )

        except Exception as e:
            logger.error(f"Error loading SharedMemory from disk: {e}")

    def get_by_author(self, author: str) -> Dict[str, Any]:
        """
        Get all entries written by a specific author.

        Args:
            author: The author (agent_id) to filter by

        Returns:
            Dictionary of key -> value for entries by this author
        """
        with self._global_lock:
            return {
                key: entry.value
                for key, entry in self.data.items()
                if entry.author == author
            }

    def get_recent(self, n: int = 10) -> List[tuple[str, MemoryEntry]]:
        """
        Get the N most recently written entries.

        Args:
            n: Number of entries to return

        Returns:
            List of (key, entry) tuples, sorted by timestamp (newest first)
        """
        with self._global_lock:
            sorted_entries = sorted(
                self.data.items(),
                key=lambda x: x[1].timestamp,
                reverse=True,
            )
            return sorted_entries[:n]

    def __repr__(self) -> str:
        """String representation of shared memory."""
        return (
            f"SharedMemory("
            f"keys={len(self.data)}, "
            f"reads={self.stats['reads']}, "
            f"writes={self.stats['writes']}, "
            f"persistence={self.enable_persistence})"
        )

    def __len__(self) -> int:
        """Number of keys in shared memory."""
        return len(self.data)

    def __contains__(self, key: str) -> bool:
        """Check if key exists using 'in' operator."""
        return self.exists(key)
