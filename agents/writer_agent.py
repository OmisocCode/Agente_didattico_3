"""
Writer Agent for Multi-Agent System.

The Writer is responsible for:
- Creating professional reports
- Structuring information clearly
- Adapting tone and style
- Properly citing sources
"""

import json
import logging
from typing import Any, Dict, List
from datetime import datetime
from agents.base_agent import BaseAgent
from core.llm import get_llm

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """
    Writer Agent that creates professional documents and reports.

    This agent:
    - Writes clear, well-structured reports
    - Adapts style to context (formal, casual, technical, etc.)
    - Properly formats and organizes content
    - Cites sources appropriately
    """

    def __init__(self, llm=None):
        """
        Initialize Writer Agent.

        Args:
            llm: LLM instance (optional, will use global if not provided)
        """
        super().__init__(
            name="Writer",
            capabilities=["writing", "report_generation", "content_structuring", "formatting"]
        )
        self.llm = llm

    def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Main processing method for writer.

        Args:
            input_data: Task data containing information to write about

        Returns:
            Dictionary with written report
        """
        if isinstance(input_data, dict):
            task = input_data.get("task", "")
            dependencies = input_data.get("dependencies", {})

            # Gather all available data
            research_data = None
            analysis_data = None

            for dep_name, dep_data in dependencies.items():
                if isinstance(dep_data, dict):
                    if "findings" in dep_data:
                        research_data = dep_data
                    if "analysis" in dep_data:
                        analysis_data = dep_data

            content_data = {
                "task": task,
                "research": research_data,
                "analysis": analysis_data
            }
        else:
            content_data = {"task": str(input_data)}

        logger.info(f"Writer creating report")

        try:
            # Write report
            report = self.write_report(content_data)

            return {
                "status": "success",
                "report": report,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Writer error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def write_report(
        self,
        data: Dict[str, Any],
        style: str = "professional",
        format_type: str = "markdown"
    ) -> str:
        """
        Write a professional report from data.

        Args:
            data: Data to write about (research, analysis, etc.)
            style: Writing style (professional, casual, technical)
            format_type: Output format (markdown, plain, html)

        Returns:
            Formatted report
        """
        logger.info(f"Writing report in {style} style, {format_type} format")

        llm = self.llm or get_llm()

        # Prepare data for report
        research = data.get("research", {})
        analysis = data.get("analysis", {})
        task = data.get("task", "General Report")

        # Build context for LLM
        context_parts = []

        if research:
            findings = research.get("findings", {})
            main_content = findings.get("main_content", "")
            sources = findings.get("sources", [])

            context_parts.append(f"Research Findings:\n{main_content}")

            if sources:
                sources_list = "\n".join([f"- {s.get('title', 'Source')}: {s.get('url', 'N/A')}" for s in sources])
                context_parts.append(f"\nSources:\n{sources_list}")

        if analysis:
            analysis_content = analysis.get("analysis", {})
            full_analysis = analysis_content.get("full_analysis", "")
            insights = analysis_content.get("insights", [])

            if full_analysis:
                context_parts.append(f"\nAnalysis:\n{full_analysis}")

            if insights:
                insights_list = "\n".join([f"- {insight}" for insight in insights])
                context_parts.append(f"\nKey Insights:\n{insights_list}")

        context = "\n\n".join(context_parts) if context_parts else "No detailed data available."

        # Create writing prompt
        prompt = f"""You are a professional writer creating a comprehensive report.

Topic: {task}

Information available:
{context}

Write a well-structured, professional report that:
1. Has a clear title and introduction
2. Presents information logically with sections
3. Incorporates key findings and insights
4. Cites sources where appropriate
5. Includes a conclusion

Style: {style}
Format: {format_type}

Create a complete, publication-ready report (400-600 words).
"""

        try:
            report = llm.generate(prompt)

            # Add metadata footer
            footer = self._create_footer(data)
            full_report = f"{report}\n\n{footer}"

            # Store in shared memory if available
            if self.shared_memory:
                self.write_shared_memory("latest_report", full_report)

            logger.info(f"Report completed: {len(full_report.split())} words")

            return full_report

        except Exception as e:
            logger.error(f"Report writing failed: {e}")
            raise

    def _create_footer(self, data: Dict[str, Any]) -> str:
        """
        Create report footer with metadata.

        Args:
            data: Report data

        Returns:
            Formatted footer
        """
        footer_parts = [
            "---",
            f"*Report generated by {self.name} Agent*",
            f"*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ]

        # Add source count if available
        research = data.get("research", {})
        if research:
            sources = research.get("findings", {}).get("sources", [])
            if sources:
                footer_parts.append(f"*Sources consulted: {len(sources)}*")

        # Add quality score if available
        analysis = data.get("analysis", {})
        if analysis:
            quality = analysis.get("analysis", {}).get("quality_score")
            if quality:
                footer_parts.append(f"*Quality score: {quality:.2f}/1.00*")

        return "\n".join(footer_parts)

    def create_summary(self, content: str, max_words: int = 100) -> str:
        """
        Create a summary of content.

        Args:
            content: Content to summarize
            max_words: Maximum words in summary

        Returns:
            Summary text
        """
        logger.info(f"Creating summary (max {max_words} words)")

        llm = self.llm or get_llm()

        prompt = f"""Summarize the following content in no more than {max_words} words:

{content}

Provide a concise summary that captures the main points.
"""

        try:
            summary = llm.generate(prompt)
            return summary.strip()

        except Exception as e:
            logger.error(f"Summary creation failed: {e}")
            # Fallback: truncate content
            words = content.split()
            return " ".join(words[:max_words]) + "..."

    def format_as_markdown(self, content: Dict[str, Any]) -> str:
        """
        Format content as markdown document.

        Args:
            content: Content to format

        Returns:
            Markdown formatted text
        """
        sections = []

        # Title
        title = content.get("title", "Report")
        sections.append(f"# {title}\n")

        # Introduction
        if "introduction" in content:
            sections.append(f"## Introduction\n\n{content['introduction']}\n")

        # Main content sections
        if "sections" in content:
            for section in content["sections"]:
                section_title = section.get("title", "Section")
                section_content = section.get("content", "")
                sections.append(f"## {section_title}\n\n{section_content}\n")

        # Conclusion
        if "conclusion" in content:
            sections.append(f"## Conclusion\n\n{content['conclusion']}\n")

        # Sources
        if "sources" in content:
            sections.append("## Sources\n")
            for i, source in enumerate(content["sources"], 1):
                sections.append(f"{i}. {source}\n")

        return "\n".join(sections)

    def adapt_tone(self, text: str, target_tone: str) -> str:
        """
        Adapt text to a different tone.

        Args:
            text: Original text
            target_tone: Desired tone (formal, casual, technical, etc.)

        Returns:
            Adapted text
        """
        logger.info(f"Adapting tone to: {target_tone}")

        llm = self.llm or get_llm()

        prompt = f"""Rewrite the following text in a {target_tone} tone while preserving the core information:

{text}

Adapted version:
"""

        try:
            adapted = llm.generate(prompt)
            return adapted.strip()

        except Exception as e:
            logger.error(f"Tone adaptation failed: {e}")
            return text  # Return original on failure
