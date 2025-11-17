"""
Researcher Agent for Multi-Agent System.

The Researcher is responsible for:
- Searching for information on given topics
- Collecting data from multiple sources
- Extracting relevant information
- Organizing findings
"""

import logging
from typing import Any, Dict, List
from datetime import datetime
from agents.base_agent import BaseAgent
from core.llm import get_llm

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent that finds and collects information.

    This agent:
    - Searches for information on topics
    - Gathers data from various sources
    - Extracts key information
    - Organizes findings for analysis
    """

    def __init__(self, llm=None):
        """
        Initialize Researcher Agent.

        Args:
            llm: LLM instance (optional, will use global if not provided)
        """
        super().__init__(
            name="Researcher",
            capabilities=["research", "information_gathering", "web_search", "extraction"]
        )
        self.llm = llm

    def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Main processing method for researcher.

        Args:
            input_data: Task data containing research topic

        Returns:
            Dictionary with research findings
        """
        if isinstance(input_data, dict):
            task = input_data.get("task", "")
            topic = task
        else:
            topic = str(input_data)

        logger.info(f"Researcher processing: {topic}")

        try:
            # Conduct research
            findings = self.research_topic(topic)

            return {
                "status": "success",
                "topic": topic,
                "findings": findings,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Researcher error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "topic": topic,
                "agent": self.name
            }

    def research_topic(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """
        Research a topic and gather information.

        Args:
            topic: The topic to research
            depth: Research depth (shallow, medium, deep)

        Returns:
            Research findings
        """
        logger.info(f"Researching topic: {topic} (depth: {depth})")

        llm = self.llm or get_llm()

        # Use LLM to generate research content
        # In a full implementation, this would scrape web sources
        prompt = f"""You are a research agent conducting comprehensive research.

Topic: {topic}

Your task:
1. Provide key facts and information about this topic
2. Identify 3-5 main aspects or subtopics
3. Note any important statistics or data points
4. Suggest credible sources (even if hypothetical)

Format your response as structured information that can be analyzed further.
Be factual and comprehensive. Limit to 400 words.
"""

        try:
            research_content = llm.generate(prompt)

            # Simulate finding multiple sources
            sources = self._generate_sources(topic)

            # Extract key points
            key_points = self._extract_key_points(research_content)

            findings = {
                "main_content": research_content,
                "key_points": key_points,
                "sources": sources,
                "depth": depth,
                "word_count": len(research_content.split())
            }

            # Store in shared memory if available
            if self.shared_memory:
                self.write_shared_memory(f"research_{topic[:30]}", findings)

            logger.info(f"Research completed: {len(key_points)} key points found")

            return findings

        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise

    def _generate_sources(self, topic: str) -> List[Dict[str, str]]:
        """
        Generate simulated sources for the research.

        Args:
            topic: Research topic

        Returns:
            List of source dictionaries

        Note:
            In production, this would fetch real web sources
        """
        # Simulated sources - in production, would use web scraping
        sources = [
            {
                "type": "article",
                "title": f"Understanding {topic}",
                "url": f"https://example.com/{topic.replace(' ', '-').lower()}",
                "credibility": "high"
            },
            {
                "type": "study",
                "title": f"Research on {topic}",
                "url": f"https://research.example.com/{topic.replace(' ', '-').lower()}",
                "credibility": "high"
            },
            {
                "type": "news",
                "title": f"Latest developments in {topic}",
                "url": f"https://news.example.com/{topic.replace(' ', '-').lower()}",
                "credibility": "medium"
            }
        ]

        return sources

    def _extract_key_points(self, content: str) -> List[str]:
        """
        Extract key points from research content.

        Args:
            content: Research content text

        Returns:
            List of key points
        """
        # Simple extraction based on sentences
        # In production, would use more sophisticated NLP
        sentences = content.split('.')
        key_points = []

        for sentence in sentences[:5]:  # Top 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                key_points.append(sentence)

        return key_points

    def search_specific_query(self, query: str) -> Dict[str, Any]:
        """
        Search for a specific query.

        Args:
            query: Search query

        Returns:
            Search results
        """
        logger.info(f"Searching: {query}")

        llm = self.llm or get_llm()

        prompt = f"""Provide concise, factual information for this query: {query}

Focus on:
- Direct answer to the query
- Key facts
- Relevant statistics or data

Keep response under 200 words.
"""

        try:
            result = llm.generate(prompt)

            return {
                "query": query,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "result": None
            }

    def gather_multiple_sources(self, topic: str, num_sources: int = 5) -> List[Dict[str, Any]]:
        """
        Gather information from multiple sources.

        Args:
            topic: Topic to research
            num_sources: Number of sources to gather

        Returns:
            List of source data
        """
        logger.info(f"Gathering {num_sources} sources for: {topic}")

        sources_data = []

        # In production, would scrape actual websites
        # For now, generate structured source data
        for i in range(num_sources):
            source = {
                "id": f"source_{i+1}",
                "type": ["article", "study", "news", "blog"][i % 4],
                "title": f"{topic} - Source {i+1}",
                "url": f"https://example.com/source_{i+1}",
                "snippet": f"Information about {topic} from source {i+1}",
                "credibility_score": 0.7 + (i % 3) * 0.1
            }
            sources_data.append(source)

        return sources_data
