"""
GitHub Analyzer Agent using Claude Agent SDK

This module contains the core analysis logic powered by the Claude Agent SDK.
The agent autonomously fetches repos, analyzes code, runs tests, and generates reports.
"""

from claude_agent_sdk import query, ClaudeAgentOptions
import os
import json
import asyncio
from pathlib import Path


def create_analysis_prompt(username: str, job_desc: str, context: str = "") -> str:
    """
    Generate the comprehensive prompt that instructs the agent.

    Args:
        username: GitHub username to analyze
        job_desc: Job description with requirements
        context: Additional context or focus areas

    Returns:
        Detailed instruction prompt for the agent
    """
    # Read the full report template from spec.md if available
    spec_path = Path(__file__).parent.parent / "spec.md"

    return f"""You are analyzing GitHub profile @{username} for a recruiter.

JOB DESCRIPTION:
{job_desc}

ADDITIONAL CONTEXT:
{context if context else "None provided"}

TASK - Complete this analysis autonomously:

1. FETCH REPOSITORIES
   - Use Bash: curl "https://api.github.com/users/{username}/repos?per_page=100"
   - If response is paginated, fetch all pages
   - Parse JSON response and save raw data

2. FILTER REPOSITORIES
   Hard filters (MUST exclude):
   - Forks (is_fork = true)
   - Not updated in past 12 months (check updated_at field)
   - < 5 commits in past year (you'll need to check this after cloning)
   - Names containing: tutorial, learning, practice, course, bootcamp

   Score remaining repos (0-100):
   - Tech stack match to JD: 70% weight
     (examine languages_url, topics, description for tech matches)
   - Recency: 20% weight
     (how recently updated)
   - Activity level: 10% weight
     (number of commits, stars, watchers)

   Select top 10 repos with score >= 30

3. ANALYZE EACH SELECTED REPO
   For each selected repository (up to 10):

   a) Clone it:
      mkdir -p repos
      cd repos
      git clone --depth 50 <repo_url>
      cd <repo_name>

   b) Static analysis FIRST (ALWAYS DO THIS):
      - Use Glob to find source files: **/*.{{js,ts,py,go,java,rb,php,cs}}
      - Use Glob to find test files: **/*test*.{{js,ts,py}} or **/test/** directories
      - Use Read to examine: README.md, package.json, requirements.txt, go.mod, etc.
      - Assess project organization, code patterns, dependencies, documentation

   c) Dynamic analysis (ONLY if tests exist and setup is clear):
      **IMPORTANT:** Most personal projects don't have tests - this is NORMAL and acceptable.
      Only attempt dynamic analysis if ALL of these are true:
      - Real test files exist (not empty test/ directories)
      - Clear dependency manifest exists (package.json, requirements.txt, go.mod)
      - Project looks like it has a working setup

      If attempting dynamic analysis:
      - Try: npm install / pip install (2 min timeout)
      - If install succeeds: try running tests
      - If tests run: capture output (pass/fail, coverage)
      - If anything fails: note it and move on (no big deal)

      **SKIP dynamic analysis entirely if:**
      - No test files found (most common - don't penalize this)
      - Unclear how to install/run
      - Project looks abandoned or incomplete

   d) What to evaluate (tests or no tests):
      - Code organization and architecture
      - Dependency choices (modern? appropriate?)
      - Git commit patterns and history
      - Documentation quality
      - If tests exist: bonus points (especially if they pass)
      - If no tests: focus on code quality and structure instead

   e) Git history analysis:
      - git log --oneline --since="1 year ago" --pretty=format:"%h %an %ar %s"
      - Assess commit frequency, message quality, author patterns
      - git shortlog -s -n --since="1 year ago" (contributor breakdown)

4. GENERATE COMPREHENSIVE REPORT
   **CRITICAL:** Use Write tool to save markdown report to: ./report.md (current directory)
   **DO NOT** use absolute paths like /Users/user/repos/report.md
   **ALWAYS** use relative paths starting with ./

   The report MUST follow this structure:

   # Technical Evaluation: @{username}

   ## Summary (For Recruiters)

   **SCORING CALIBRATION - BE HONEST AND CRITICAL:**
   - 9-10/10: Exceptional. Senior-level work, comprehensive testing, production systems, clear architectural vision. RARE.
   - 7-8/10: Strong. Solid fundamentals, some testing, good code organization, appropriate for mid-level
   - 5-6/10: Adequate. Basic functionality works, limited testing, acceptable for junior roles. MOST CANDIDATES.
   - 3-4/10: Weak. Poor practices, no tests, unclear organization, major gaps
   - 1-2/10: Very weak. Broken code, no documentation, tutorial-level work only

   **Default assumption: Most candidates score 5-6. Require strong evidence to score higher.**

   **Overall Score:** X/10
   **Match to JD:** X%
   **Code Quality:** High/Medium/Low
   **Experience Level:** Junior/Mid/Senior/Lead
   **Recommendation:** ✅ Interview / ⚠️ Maybe / ❌ Pass

   **Key Strengths:**
   - [3-5 specific bullet points]

   **Red Flags:**
   - [Any concerns, or "None identified"]

   ---

   ## Projects Analyzed (Past Year Only)

   **Repos selected:** X of Y total
   **Selection criteria:** Recent, relevant to JD, substantial original work

   ---

   ### 1. [repo-name] ⭐ PRIMARY FOCUS

   **Why this matters:** [Why this repo is most relevant]

   **Relevance Score:** XX/100
   **Last Updated:** X months ago
   **Tech Stack:** [List technologies] ✅/⚠️/❌ Match to JD
   **Analysis Tier:** DEEP ANALYSIS / STATIC ANALYSIS

   **Code Quality Assessment:** X/10

   **Architecture:**
   [Describe project structure, design patterns]

   **Testing:**
   - ✅/❌ Tests present
   - ✅/❌ Tests passing
   - Coverage: X% (if available)

   **Code Quality:**
   [Specific observations about code quality]

   **Dependencies:**
   [Assessment of dependencies, any security issues]

   **Git Practices:**
   [Commit patterns, message quality]

   **Strengths:**
   [3-5 specific strengths]

   **Areas for Improvement:**
   [2-3 areas if any]

   ---

   [Repeat for repos 2-5, but briefer for repos 3-5]

   ---

   ## Contribution Patterns

   **Consistency:** REGULAR / SPORADIC / INACTIVE
   [Describe commit frequency and patterns]

   **Velocity:** HIGH / MODERATE / LOW
   [Commits per month, development pace]

   **Work Style:** SOLO / COLLABORATIVE / MIXED
   [Based on repo collaborators and commit patterns]

   ---

   ## Open Source Activity

   **Engagement Level:** ACTIVE / MODERATE / LIMITED
   **Total Contributions (Past Year):** X+
   [Brief high-level summary only - don't deep-dive into OSS]

   ---

   ## Technical Profile

   **Specialization Type:** T-SHAPED / I-SHAPED / GENERALIST
   **Deep expertise:** [Languages/frameworks with most evidence]
   **Broad experience:** [Other technologies touched]

   **Domain Experience:**
   [Any patterns in project types - fintech, SaaS, ML, etc.]

   **Skill Progression:**
   [Evidence of learning and growth over time]

   ---

   ## What We Excluded

   **Not analyzed (X repos):**
   - X repos: Updated more than 12 months ago
   - X repos: Forks (not original work)
   - X repos: Different tech stack
   - X repos: Tutorial/learning projects
   - X repos: Too small or trivial

   **Why focus on these X:**
   Recent, relevant, substantial original work that demonstrates current capabilities

   ---

   ## Match to Job Requirements

   **Required Skills vs. Evidence:**

   [For each skill in JD:]
   ✅ [Skill] - **Strong evidence** ([where seen])
   ⚠️ [Skill] - **Limited evidence** ([context])
   ❌ [Skill] - **No evidence** (gap identified)

   **Skill Gaps to Explore:**
   [List any gaps that should be discussed in interview]

   ---

   ## Interview Questions

   Based on the analysis, ask:

   **Technical Questions:**
   1. "In [specific repo], you used [specific pattern]. Walk me through why you chose that approach."
   2. [2-3 more specific questions based on actual code]

   **Experience Questions:**
   3. [Questions about scale, team collaboration, etc.]

   **Gap Questions:**
   4. [Questions about missing skills from JD]

   ---

   ## Overall Assessment

   **Final Recommendation:** ✅/⚠️/❌ + explanation

   **Summary:**
   [2-3 paragraph honest assessment]

   **Why Interview:**
   [Specific reasons based on analysis]

   **What to Watch For:**
   [Specific concerns or areas to probe in interview]

   **Expected Level:**
   [Junior/Mid/Senior with justification]

   ---

   ## Analysis Metadata

   **Analysis Date:** [Current date]
   **Repos Analyzed:** X
   **Total Repos Found:** Y
   **Analysis Duration:** [Approximate time]
   **Tests Executed:** X projects successfully, Y skipped

   ---

   ALTERNATIVE - If NO relevant repos found:

   # Analysis Result: Insufficient Data

   **Candidate:** @{username}
   **GitHub Repos:** X total

   **Analysis Status:** ❌ Cannot evaluate

   **Why:**
   No relevant, recent projects found matching job requirements.

   **Breakdown:**
   - X repos are forks (excluded - not original work)
   - X repos haven't been updated in 12+ months (excluded - too old)
   - X repos use different tech stack (excluded - not relevant to role)
   - X repos are learning/tutorial projects (excluded)
   - X repos have minimal commits (excluded - insufficient work)

   **Recommendation:**
   - Ask candidate about recent work (may be in private/company repos)
   - Request code samples from current or recent job
   - Consider structured technical assessment
   - Discuss their experience in interview despite lack of public portfolio

   **Note:** Lack of recent public GitHub activity is common for:
   - Developers working primarily on private company codebases
   - Senior engineers focused on architecture/leadership vs. coding
   - Career switchers or recent bootcamp graduates

5. UPDATE PROGRESS REGULARLY
   After each major step, use Write to update ./status.json (current directory) with:
   {{
     "stage": "current_stage",
     "progress": 0-100,
     "current_repo": "repo_name",
     "current": 1,
     "total": 10,
     "timestamp": "[ISO timestamp]"
   }}

   Progress stages:
   - fetching_repos (progress: 10)
   - filtering_repos (progress: 20)
   - analyzing_repo (progress: 30-90, increment per repo)
   - generating_report (progress: 95)
   - completed (progress: 100)

IMPORTANT GUIDELINES:
- Be thorough but efficient - aim for 5-15 minutes total
- Be honest - if code quality is poor, say so
- Be specific - reference actual file names, line numbers, patterns
- Be fair - consider the candidate's apparent skill level
- If you can't run tests due to dependencies, that's OK - note it and continue
- Don't spend more than 2-3 minutes per repo on execution attempts
- Focus on the top 3 repos most deeply, be briefer on repos 4-10

Good luck! Provide a comprehensive, honest, actionable analysis.
"""


class GitHubAnalyzer:
    """
    Wrapper for Claude Agent SDK to analyze GitHub profiles.

    This class manages the agent execution and ensures all outputs
    are saved to the appropriate analysis directory.
    """

    def __init__(self, analysis_id: str):
        """
        Initialize analyzer for a specific analysis run.

        Args:
            analysis_id: Unique ID for this analysis
        """
        self.analysis_id = analysis_id
        self.work_dir = f"analyses/{analysis_id}"
        os.makedirs(self.work_dir, exist_ok=True)

    def run(self, username: str, job_desc: str, context: str = "") -> dict:
        """
        Run the autonomous GitHub analysis.

        This method uses the Claude Agent SDK query function with full autonomy.
        The agent will use Bash, Read, Write, Grep, and Glob tools to:
        - Fetch repos from GitHub API
        - Filter and score them
        - Clone and analyze code
        - Run tests where possible
        - Generate comprehensive report

        Args:
            username: GitHub username to analyze
            job_desc: Job description with requirements
            context: Additional context (optional)

        Returns:
            dict with analysis_id, status, and report_path
        """
        # Create the comprehensive instruction prompt
        prompt = create_analysis_prompt(username, job_desc, context)

        # Configure options for the agent
        options = ClaudeAgentOptions(
            model="claude-opus-4-5-20251101",  # Most capable Claude model
            permission_mode="bypassPermissions",  # Auto-approve all tool use
            cwd=self.work_dir  # Agent works in this directory
        )

        try:
            # Run the agent query asynchronously
            # We need to collect all messages
            async def run_query():
                messages = []
                async for message in query(prompt=prompt, options=options):
                    messages.append(message)
                    print(f"[Agent] Received message type: {type(message).__name__}")
                return messages

            # Execute the async query
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                messages = loop.run_until_complete(run_query())
            finally:
                loop.close()

            print(f"[Agent] Total messages received: {len(messages)}")

            # Check if report was actually created
            report_path = f"{self.work_dir}/report.md"
            if not os.path.exists(report_path):
                # Agent didn't create the report
                error_msg = f"Agent completed but did not create report.md. Received {len(messages)} messages."
                print(f"[Agent ERROR] {error_msg}")

                # Save debug info
                with open(f"{self.work_dir}/debug.txt", "w", encoding="utf-8") as f:
                    f.write(f"Messages received: {len(messages)}\n\n")
                    for i, msg in enumerate(messages):
                        f.write(f"Message {i}: {type(msg).__name__} - {str(msg)[:200]}\n\n")

                raise Exception(error_msg)

            return {
                "analysis_id": self.analysis_id,
                "status": "completed",
                "report_path": report_path,
                "messages": len(messages)
            }

        except Exception as e:
            # If agent fails, log the error
            error_msg = f"Agent execution failed: {str(e)}"

            # Save error to status
            with open(f"{self.work_dir}/status.json", "w") as f:
                json.dump({
                    "stage": "error",
                    "progress": 0,
                    "error": error_msg
                }, f)

            raise Exception(error_msg)
