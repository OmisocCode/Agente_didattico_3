"""
Fact Checker Agent for Multi-Agent System.

The Fact Checker is responsible for:
- Verifying claims and statements
- Cross-referencing information across sources
- Identifying contradictions
- Assigning confidence scores
"""

import json
import logging
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
from agents.base_agent import BaseAgent
from core.llm import get_llm

logger = logging.getLogger(__name__)


class FactCheckerAgent(BaseAgent):
    """
    Fact Checker Agent that verifies accuracy of information.

    This agent:
    - Verifies factual claims
    - Cross-references information
    - Identifies inconsistencies
    - Assigns confidence/credibility scores
    """

    def __init__(self, llm=None):
        """
        Initialize Fact Checker Agent.

        Args:
            llm: LLM instance (optional, will use global if not provided)
        """
        super().__init__(
            name="FactChecker",
            capabilities=["fact_checking", "verification", "cross_reference", "credibility_assessment"]
        )
        self.llm = llm

    def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Main processing method for fact checker.

        Args:
            input_data: Task data containing information to verify

        Returns:
            Dictionary with verification results
        """
        if isinstance(input_data, dict):
            task = input_data.get("task", "")
            dependencies = input_data.get("dependencies", {})

            # Gather data to verify
            claims_to_verify = []
            sources_data = []

            for dep_name, dep_data in dependencies.items():
                if isinstance(dep_data, dict):
                    # Extract claims from research/analysis
                    if "findings" in dep_data:
                        findings = dep_data.get("findings", {})
                        key_points = findings.get("key_points", [])
                        claims_to_verify.extend(key_points)
                        sources_data.extend(findings.get("sources", []))

                    if "analysis" in dep_data:
                        analysis = dep_data.get("analysis", {})
                        insights = analysis.get("insights", [])
                        claims_to_verify.extend(insights)

            verification_data = {
                "claims": claims_to_verify,
                "sources": sources_data
            }
        else:
            verification_data = {"claims": [str(input_data)], "sources": []}

        logger.info(f"FactChecker verifying {len(verification_data['claims'])} claims")

        try:
            # Verify claims
            verification = self.verify_claims(
                verification_data["claims"],
                verification_data["sources"]
            )

            return {
                "status": "success",
                "verification": verification,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"FactChecker error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    def verify_claims(
        self,
        claims: List[str],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a list of claims against sources.

        Args:
            claims: List of claims to verify
            sources: List of source data

        Returns:
            Verification results
        """
        logger.info(f"Verifying {len(claims)} claims...")

        verifications = []

        for claim in claims[:10]:  # Limit to 10 claims
            if not claim or len(claim.strip()) < 10:
                continue

            verification = self._verify_single_claim(claim, sources)
            verifications.append(verification)

        # Calculate overall verification stats
        verified_count = sum(1 for v in verifications if v["status"] == "verified")
        total_count = len(verifications)

        results = {
            "total_claims": len(claims),
            "verified_claims": verified_count,
            "verification_rate": verified_count / total_count if total_count > 0 else 0,
            "verifications": verifications,
            "summary": self._create_verification_summary(verifications)
        }

        # Store in shared memory if available
        if self.shared_memory:
            self.write_shared_memory("fact_check_results", results)

        logger.info(f"Verification complete: {verified_count}/{total_count} verified")

        return results

    def _verify_single_claim(
        self,
        claim: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a single claim.

        Args:
            claim: Claim to verify
            sources: Available sources

        Returns:
            Verification result for the claim
        """
        llm = self.llm or get_llm()

        # Prepare sources context
        sources_text = "\n".join([
            f"- {s.get('title', 'Source')}: {s.get('url', 'N/A')}"
            for s in sources[:5]  # Limit to 5 sources
        ])

        prompt = f"""You are a fact-checker verifying claims.

Claim to verify: "{claim}"

Available sources:
{sources_text if sources_text else "No specific sources provided"}

Assess this claim:
1. Is it verifiable? (yes/no)
2. Status: verified/unverified/partially-verified/contradicted
3. Confidence level: low/medium/high
4. Brief explanation (1-2 sentences)

Respond in JSON format:
{{
    "verifiable": true/false,
    "status": "verified",
    "confidence": "medium",
    "explanation": "..."
}}
"""

        try:
            response = llm.generate(prompt)

            # Extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            result = json.loads(json_str)

            return {
                "claim": claim,
                "verifiable": result.get("verifiable", False),
                "status": result.get("status", "unverified"),
                "confidence": result.get("confidence", "low"),
                "explanation": result.get("explanation", ""),
                "sources_checked": len(sources)
            }

        except Exception as e:
            logger.warning(f"Verification failed for claim, using fallback: {e}")
            return {
                "claim": claim,
                "verifiable": False,
                "status": "unknown",
                "confidence": "low",
                "explanation": "Could not verify claim",
                "sources_checked": len(sources)
            }

    def _create_verification_summary(self, verifications: List[Dict[str, Any]]) -> str:
        """
        Create summary of verification results.

        Args:
            verifications: List of verification results

        Returns:
            Summary text
        """
        if not verifications:
            return "No claims verified."

        verified = sum(1 for v in verifications if v["status"] == "verified")
        partial = sum(1 for v in verifications if v["status"] == "partially-verified")
        contradicted = sum(1 for v in verifications if v["status"] == "contradicted")
        unverified = sum(1 for v in verifications if v["status"] == "unverified")

        summary_parts = []

        if verified > 0:
            summary_parts.append(f"{verified} claim(s) verified")
        if partial > 0:
            summary_parts.append(f"{partial} partially verified")
        if contradicted > 0:
            summary_parts.append(f"{contradicted} contradicted")
        if unverified > 0:
            summary_parts.append(f"{unverified} unverified")

        return ", ".join(summary_parts) + "."

    def cross_reference(
        self,
        claim: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cross-reference a claim across multiple sources.

        Args:
            claim: Claim to cross-reference
            sources: Sources to check against

        Returns:
            Cross-reference results
        """
        logger.info(f"Cross-referencing claim across {len(sources)} sources")

        llm = self.llm or get_llm()

        sources_info = "\n".join([
            f"{i+1}. {s.get('title', 'Source')}: {s.get('snippet', 'N/A')}"
            for i, s in enumerate(sources[:5])
        ])

        prompt = f"""Cross-reference this claim across multiple sources:

Claim: "{claim}"

Sources:
{sources_info}

Determine:
1. How many sources support this claim?
2. Are there contradictions?
3. What's the consensus view?

Respond briefly (2-3 sentences).
"""

        try:
            cross_ref_result = llm.generate(prompt)

            return {
                "claim": claim,
                "sources_checked": len(sources),
                "cross_reference": cross_ref_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Cross-reference failed: {e}")
            return {
                "claim": claim,
                "sources_checked": len(sources),
                "error": str(e)
            }

    def identify_contradictions(
        self,
        data_sets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify contradictions between data sets.

        Args:
            data_sets: Multiple data sets to compare

        Returns:
            List of identified contradictions
        """
        logger.info(f"Identifying contradictions in {len(data_sets)} data sets")

        contradictions = []

        # Simple contradiction detection
        # In production, would use more sophisticated NLP
        for i, ds1 in enumerate(data_sets):
            for j, ds2 in enumerate(data_sets[i+1:], i+1):
                # Compare key claims or findings
                contradiction = self._compare_datasets(ds1, ds2)
                if contradiction:
                    contradictions.append({
                        "dataset_1": i,
                        "dataset_2": j,
                        "contradiction": contradiction
                    })

        return contradictions

    def _compare_datasets(
        self,
        ds1: Dict[str, Any],
        ds2: Dict[str, Any]
    ) -> Optional[str]:
        """
        Compare two datasets for contradictions.

        Args:
            ds1: First dataset
            ds2: Second dataset

        Returns:
            Contradiction description or None
        """
        # Simplified comparison
        # In production, would do deeper analysis
        return None  # No contradictions found in simple version

    def assign_confidence_score(
        self,
        claim: str,
        verification_data: Dict[str, Any]
    ) -> float:
        """
        Assign confidence score to a verified claim.

        Args:
            claim: The claim
            verification_data: Verification data

        Returns:
            Confidence score (0-1)
        """
        score = 0.5  # Base score

        status = verification_data.get("status", "unknown")

        if status == "verified":
            score = 0.9
        elif status == "partially-verified":
            score = 0.6
        elif status == "contradicted":
            score = 0.2
        else:  # unverified or unknown
            score = 0.3

        # Adjust based on sources
        sources_checked = verification_data.get("sources_checked", 0)
        if sources_checked >= 3:
            score += 0.1
        elif sources_checked == 0:
            score -= 0.1

        # Ensure in valid range
        return max(0.0, min(1.0, score))
