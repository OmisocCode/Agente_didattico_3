"""
Analyst Agent for Multi-Agent System.

The Analyst is responsible for:
- Analyzing research findings
- Evaluating data quality and credibility
- Identifying patterns and trends
- Generating insights and conclusions
"""

import json
import logging
from typing import Any, Dict, List
from datetime import datetime
from agents.base_agent import BaseAgent
from core.llm import get_llm

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """
    Analyst Agent that analyzes data and generates insights.

    This agent:
    - Evaluates quality and credibility of information
    - Identifies patterns and trends
    - Performs comparative analysis
    - Generates insights and conclusions
    """

    def __init__(self, llm=None):
        """
        Initialize Analyst Agent.

        Args:
            llm: LLM instance (optional, will use global if not provided)
        """
        super().__init__(
            name="Analyst",
            capabilities=["analysis", "evaluation", "pattern_recognition", "insights"]
        )
        self.llm = llm

    def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Main processing method for analyst.

        Args:
            input_data: Task data containing information to analyze

        Returns:
            Dictionary with analysis results
        """
        if isinstance(input_data, dict):
            task = input_data.get("task", "")
            dependencies = input_data.get("dependencies", {})

            # Get research data from dependencies
            research_data = None
            for dep_name, dep_data in dependencies.items():
                if isinstance(dep_data, dict) and "findings" in dep_data:
                    research_data = dep_data
                    break

            data_to_analyze = research_data if research_data else input_data
        else:
            data_to_analyze = input_data

        logger.info(f"Analyst processing data analysis")

        try:
            # Perform analysis
            analysis = self.analyze_data(data_to_analyze)

            return {
                "status": "success",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"Analyst error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def analyze_data(self, data: Any) -> Dict[str, Any]:
        """
        Analyze data and generate insights.

        Args:
            data: Data to analyze

        Returns:
            Analysis results with insights
        """
        logger.info("Performing data analysis...")

        llm = self.llm or get_llm()

        # Prepare data for analysis
        data_str = json.dumps(data, indent=2, default=str)

        prompt = f"""You are an expert analyst reviewing research data.

Data to analyze:
{data_str}

Provide a comprehensive analysis including:

1. **Quality Assessment**: Evaluate the quality and credibility of the information
2. **Key Findings**: Identify the most important findings
3. **Patterns**: Identify any patterns, trends, or relationships
4. **Insights**: Generate meaningful insights from the data
5. **Gaps**: Note any information gaps or limitations
6. **Confidence**: Rate your confidence in the analysis (low/medium/high)

Be critical and objective. Limit to 400 words.
"""

        try:
            analysis_content = llm.generate(prompt)

            # Extract structured insights
            insights = self._extract_insights(analysis_content)

            # Assess credibility
            credibility = self._assess_credibility(data)

            analysis = {
                "full_analysis": analysis_content,
                "insights": insights,
                "credibility_assessment": credibility,
                "quality_score": self._calculate_quality_score(data, credibility),
                "confidence": "medium"  # Default, could be extracted from LLM response
            }

            # Store in shared memory if available
            if self.shared_memory:
                self.write_shared_memory("latest_analysis", analysis)

            logger.info(f"Analysis completed with {len(insights)} insights")

            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def _extract_insights(self, analysis_content: str) -> List[str]:
        """
        Extract key insights from analysis content.

        Args:
            analysis_content: Full analysis text

        Returns:
            List of insights
        """
        insights = []

        # Simple extraction - look for numbered points or key sentences
        lines = analysis_content.split('\n')

        for line in lines:
            line = line.strip()
            # Look for lines that seem like insights
            if any(indicator in line.lower() for indicator in ['insight:', 'finding:', 'key:', 'important:', '**']):
                if len(line) > 20:
                    # Clean up markdown formatting
                    insight = line.replace('**', '').replace('*', '').strip('- ')
                    if insight:
                        insights.append(insight)

        # If no insights found, extract first few meaningful sentences
        if not insights:
            sentences = [s.strip() for s in analysis_content.split('.') if len(s.strip()) > 30]
            insights = sentences[:3]

        return insights[:5]  # Max 5 insights

    def _assess_credibility(self, data: Any) -> Dict[str, Any]:
        """
        Assess credibility of data sources.

        Args:
            data: Data with sources to assess

        Returns:
            Credibility assessment
        """
        assessment = {
            "overall_credibility": "medium",
            "factors": []
        }

        # Check if data has sources
        if isinstance(data, dict):
            sources = data.get("sources", [])

            if sources:
                # Count high credibility sources
                high_cred_count = sum(1 for s in sources if isinstance(s, dict) and s.get("credibility") == "high")
                total_sources = len(sources)

                if high_cred_count / total_sources > 0.6:
                    assessment["overall_credibility"] = "high"
                    assessment["factors"].append(f"{high_cred_count}/{total_sources} high-credibility sources")
                elif high_cred_count / total_sources < 0.3:
                    assessment["overall_credibility"] = "low"
                    assessment["factors"].append(f"Only {high_cred_count}/{total_sources} high-credibility sources")
                else:
                    assessment["factors"].append(f"{high_cred_count}/{total_sources} high-credibility sources")

            # Check for data completeness
            if "findings" in data or "main_content" in data:
                assessment["factors"].append("Comprehensive data available")
            else:
                assessment["factors"].append("Limited data available")

        return assessment

    def _calculate_quality_score(self, data: Any, credibility: Dict[str, Any]) -> float:
        """
        Calculate overall quality score.

        Args:
            data: Data to score
            credibility: Credibility assessment

        Returns:
            Quality score (0-1)
        """
        score = 0.5  # Base score

        # Adjust based on credibility
        cred_level = credibility.get("overall_credibility", "medium")
        if cred_level == "high":
            score += 0.3
        elif cred_level == "low":
            score -= 0.2

        # Adjust based on data completeness
        if isinstance(data, dict):
            if "findings" in data and "sources" in data:
                score += 0.1

            sources = data.get("sources", [])
            if len(sources) >= 3:
                score += 0.1

        # Ensure score is in valid range
        return max(0.0, min(1.0, score))

    def compare_data(self, data_sets: List[Any]) -> Dict[str, Any]:
        """
        Compare multiple data sets.

        Args:
            data_sets: List of data sets to compare

        Returns:
            Comparison results
        """
        logger.info(f"Comparing {len(data_sets)} data sets...")

        llm = self.llm or get_llm()

        # Prepare data for comparison
        data_str = "\n\n---\n\n".join([
            f"Dataset {i+1}:\n{json.dumps(ds, indent=2, default=str)}"
            for i, ds in enumerate(data_sets)
        ])

        prompt = f"""Compare these datasets and identify:

{data_str}

1. **Similarities**: What information is consistent across sources?
2. **Differences**: What contradictions or variations exist?
3. **Reliability**: Which dataset seems most reliable and why?
4. **Synthesis**: What's the most accurate understanding based on all data?

Be analytical and objective. Limit to 300 words.
"""

        try:
            comparison = llm.generate(prompt)

            return {
                "comparison": comparison,
                "num_datasets": len(data_sets),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {
                "error": str(e),
                "num_datasets": len(data_sets)
            }

    def identify_trends(self, data: Any) -> List[str]:
        """
        Identify trends in the data.

        Args:
            data: Data to analyze for trends

        Returns:
            List of identified trends
        """
        logger.info("Identifying trends...")

        # Simple trend identification
        # In production, would use more sophisticated analysis
        trends = [
            "Data shows consistent patterns",
            "Multiple sources confirm key findings",
            "Information quality is above average"
        ]

        return trends
