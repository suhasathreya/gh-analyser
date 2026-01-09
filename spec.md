```markdown
# GitHub Candidate Analyzer - Product Spec

## Overview

A web application that helps recruiters evaluate technical candidates by analyzing their GitHub profiles against job requirements.

---

## Core Philosophy

**"Recent, relevant, original work only. Be honest about limitations."**

- Only analyze repos from **past 12 months**
- Only analyze repos **relevant to the job description**
- Focus on **original work** (ignore forks)
- Max **10 repos** analyzed
- If repo needs API keys, do **static analysis only**
- If **no relevant repos**, say so clearly (don't fake it)

---

## User Flow

### Input Screen

**Form fields:**

1. **GitHub Username** (required)
   - Text input
   - Validation: Must be valid GitHub username
   - Example placeholder: "octocat"

2. **Job Description** (required)
   - Large text area
   - Validation: Minimum 50 characters
   - Example placeholder: "Senior Full-Stack Engineer. Required: React, TypeScript, Node.js..."

3. **Additional Context** (optional)
   - Text area
   - For any special requests, focus areas, or notes
   - Example: "Focus on backend skills" or "Check for fintech experience" or "Ignore side projects, focus on production-quality work"

**Submit button:** "Analyze Candidate"

---

### Loading State

**While analysis runs (5-15 minutes):**
- Progress indicator
- Status updates:
  - "Fetching GitHub repos..."
  - "Filtering repos..."
  - "Analyzing project 1 of 5..."
  - "Generating report..."

---

### Output Screen

**Display:**
- Report rendered as HTML (from markdown)
- Clean, readable formatting
- Syntax highlighting for code snippets (if any)

**Actions:**
- **Download as Word** button (.docx)
- **Download as PDF** button (.pdf)
- **Copy to Clipboard** button (markdown format)
- **Start New Analysis** button

---

## Functional Requirements

### 1. Job Description Analysis

Parse JD and extract:
- Required programming languages
- Required frameworks/libraries
- Required tools (databases, cloud platforms, etc.)
- Seniority level (if mentioned)
- Domain/industry (if mentioned)
- Any other relevant keywords

Use the "Additional Context" field to guide analysis priorities if provided.

---

### 2. Repo Discovery & Filtering

**Fetch all candidate repos from GitHub API**

**Hard filters (automatic exclusion):**
- ❌ Updated more than 12 months ago
- ❌ Is a fork (not original work)
- ❌ Less than 5 commits in past year (insufficient activity)
- ❌ Name contains: "tutorial", "learning", "practice", "course", "bootcamp"

**After filtering:**
- Score remaining repos by relevance to JD (0-100)
- Select top 10 (or fewer if less than 10 match)
- If a repo scores below 30/100, exclude it

**Relevance scoring based on:**
- Tech stack match to JD (70% weight)
- Recency (20% weight)
- Activity level (10% weight)

**Note:** Let the agent decide what constitutes "too small" or trivial - don't hardcode size limits. The agent should use its judgment.

---

### 3. Repo Analysis

**For each selected repo:**

#### Static Analysis (always do this):
- Project structure and organization
- Code quality patterns
- Dependencies and potential vulnerabilities
- Testing approach and setup
- Documentation quality
- Git commit history and patterns

#### Execution Analysis (if possible):
- Detect if repo requires external dependencies (API keys, databases, services)
- If dependencies can be satisfied:
  - Install what's needed
  - Run available quality checks
  - Execute tests
  - Build if applicable
- If dependencies cannot be satisfied:
  - Note this in report
  - Rely on static analysis only

**Important:** Give the agent flexibility to adapt its approach based on what it finds. Don't prescribe exact commands - let it figure out the best way to analyze each project type.

---

### 4. Additional Signals

**Contribution patterns:**
- Consistency of commits over time
- Development velocity
- Solo vs. collaborative work style

**OSS activity (high-level only):**
- Total contributions in past year
- Notable projects contributed to
- Overall engagement level

**Code quality signals:**
- Commit message quality
- Git workflow practices
- Code organization patterns

---

### 5. Report Generation

**If NO relevant repos found:**

```markdown
# Analysis Result: Insufficient Data

**Candidate:** @username
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
```

---

**If relevant repos found:**

```markdown
# Technical Evaluation: @username

## Summary (For Recruiters)

**Overall Score:** 7.5/10
**Match to JD:** 85%
**Code Quality:** High
**Experience Level:** Mid-Senior
**Recommendation:** ✅ Interview

**Key Strengths:**
- Clean, well-structured code
- Strong testing practices (80%+ coverage visible)
- Matches required tech stack perfectly
- Active, consistent contributor

**Red Flags:**
- ⚠️ Limited evidence of large-scale production work
- ⚠️ No CI/CD setup visible in analyzed projects
- ⚠️ Gap in X technology (required but not present)

---

## Projects Analyzed (Past Year Only)

**Repos selected:** 5 of 28 total
**Selection criteria:** Recent, relevant to JD, substantial original work

---

### 1. project-name ⭐ PRIMARY FOCUS

**Why this matters:** Most recent, best match to JD, production-quality code

**Relevance Score:** 88/100
**Last Updated:** 2 months ago
**Tech Stack:** React, TypeScript, Node.js, PostgreSQL ✅ Perfect JD match
**Analysis Tier:** DEEP ANALYSIS ⭐ (tests executed successfully)

**Code Quality Assessment:** 8.5/10

**Architecture:**
- Clean separation of concerns
- Well-organized component structure
- Proper state management patterns
- RESTful API design

**Testing:**
- ✅ Tests present and passing
- ✅ 82% coverage (excellent)
- ✅ Proper mocking of external dependencies
- Integration tests included

**Code Quality:**
- Strong TypeScript usage (minimal `any` types)
- Consistent code style throughout
- Good error handling patterns
- Clear, descriptive function/variable names

**Dependencies:**
- Modern, well-maintained libraries
- 2 minor security advisories (low severity)
- Appropriate package choices for use case

**Git Practices:**
- Clear, descriptive commit messages
- Feature branch workflow
- Reasonable commit sizes

**Strengths:**
- Professional-grade code organization
- Strong testing discipline
- Modern best practices followed
- Production-ready patterns

**Areas for Improvement:**
- Some components exceed 300 lines (could be broken down)
- Limited error boundary usage in React
- Could benefit from more comprehensive documentation

**Code Sample (Redacted):**
[Brief example showing quality if relevant]

---

### 2. second-project

**Relevance Score:** 76/100
**Last Updated:** 4 months ago
**Tech Stack:** Node.js, Express, MongoDB
**Analysis Tier:** STATIC ANALYSIS (requires API keys)

**Code Quality Assessment:** 7/10

[Similar structure but briefer than primary project]

---

### 3-5. Additional Projects

**Brief summaries of supporting projects**
- Project 3: [One paragraph]
- Project 4: [One paragraph]
- Project 5: [One paragraph]

---

## Contribution Patterns

**Consistency:** REGULAR ✅
- Commits 3-4 times per week consistently
- Sustained activity over past year
- Professional work rhythm

**Velocity:** MODERATE
- ~28 commits per month average
- Suggests employed full-time (likely coding at work + personal projects)
- Healthy balance

**Work Style:** MIXED
- 3 solo projects (can work independently)
- 2 collaborative projects (comfortable on teams)
- Demonstrates versatility

---

## Open Source Activity

**Engagement Level:** ACTIVE
**Total Contributions (Past Year):** 180+
**Notable Projects Contributed To:**
- React (5 merged PRs)
- TypeScript ESLint (regular contributor)

**Assessment:** 
- Engaged in OSS community ✅
- Shows collaboration skills ✅
- Gives back to tools they use ✅

---

## Technical Profile

**Specialization Type:** T-SHAPED ✅
- **Deep expertise:** React, TypeScript, Node.js
- **Broad experience:** Python, Docker, AWS, GraphQL

**Domain Experience:**
- Fintech (2 projects)
- SaaS applications (3 projects)
- Developer tools (1 project)

**Skill Progression:**
- Evidence of learning and adopting new technologies
- Recent projects show more sophisticated patterns
- Growing complexity and scope over time

---

## What We Excluded

**Not analyzed (23 repos):**
- 10 repos: Updated more than 12 months ago
- 6 repos: Forks (not original work)
- 4 repos: Different tech stack (PHP, Java vs. required JS/TS)
- 3 repos: Tutorial/learning projects

**Why focus on these 5:**
Recent, relevant, substantial original work that demonstrates current capabilities

---

## Match to Job Requirements

**Required Skills vs. Evidence:**

✅ React - **Strong evidence** (multiple production-quality projects)
✅ TypeScript - **Strong evidence** (primary language in recent work)
✅ Node.js - **Strong evidence** (backend experience clear)
✅ PostgreSQL - **Moderate evidence** (used in 1 project, MongoDB in others)
⚠️ AWS - **Limited evidence** (not visible in analyzed repos)
❌ CI/CD - **No evidence** (no GitHub Actions or similar visible)

**Skill Gaps to Explore:**
- PostgreSQL vs. MongoDB experience depth
- AWS/cloud deployment experience
- CI/CD pipeline setup experience

---

## Interview Questions

Based on the analysis, ask:

**Technical Questions:**
1. "In [project-name], you used [specific pattern]. Walk me through why you chose that approach and what trade-offs you considered."

2. "I noticed you primarily use MongoDB. How would you approach migrating to PostgreSQL for [use case]? What challenges would you anticipate?"

3. "Your testing coverage is strong - walk me through your testing philosophy and how you decide what to test."

4. "I don't see CI/CD in your public repos. What's your experience with deployment pipelines and DevOps practices?"

**Experience Questions:**
5. "These projects appear to be [small/medium] scale. Tell me about the largest application you've worked on and your role."

6. "How do you approach code review? What do you look for?"

**Based on Additional Context:**
[Any custom questions based on user's additional input]

---

## Overall Assessment

**Final Recommendation:** ✅ Strong candidate - proceed to technical interview

**Summary:**
This candidate demonstrates high-quality coding practices, strong fundamentals in the required tech stack, and active engagement in the developer community. Code is clean, well-tested, and follows modern best practices. Some gaps exist (AWS, CI/CD) but these are addressable through training or may simply not be visible in public repos.

**Why Interview:**
- Excellent code quality and testing discipline
- Strong match to core tech requirements (React, TypeScript, Node)
- Evidence of continuous learning and growth
- Professional development practices

**What to Watch For:**
- Production scaling experience (projects analyzed are relatively small)
- CI/CD and DevOps capabilities (not evident in repos)
- PostgreSQL depth (primarily uses MongoDB)
- Team collaboration at scale (limited evidence in public work)

**Expected Level:**
Based on code quality and complexity: **Solid Mid-Level, approaching Senior**

Could be Senior if:
- Private/company work shows large-scale production experience
- Has strong system design and architecture experience
- Demonstrates leadership/mentorship capabilities

---

## Analysis Metadata

**Analysis Date:** [Date]
**Repos Analyzed:** 5
**Total Repos Found:** 28
**Analysis Duration:** 8 minutes
**GitHub API Calls:** 47
**Tests Executed:** 2 projects (3 skipped - required API keys)

---

[End of Report]
```

---

## Technical Stack (Web App)

### Frontend
- Framework: React + TypeScript
- UI: Clean, professional design (Tailwind CSS recommended)
- State management: React hooks
- Form validation: Zod or similar

### Backend
- Framework: Next.js API routes OR separate Express server
- Analysis engine: Claude Agent SDK (Python)
  - Either: Next.js calls Python backend
  - Or: Pure Python backend with FastAPI

### Document Generation
- Markdown → HTML (for display)
- HTML → DOCX (using mammoth or docx library)
- HTML → PDF (using puppeteer or similar)

### Deployment
- Web app: Vercel, Netlify, or similar
- Backend: Railway, Render, or similar (if separate)

---

## Non-Functional Requirements

### Performance
- Analysis completes in 5-15 minutes
- Progress updates every 30 seconds
- Handle repos up to reasonable size (agent decides limits)
- Timeout individual repo analysis if taking too long

### Error Handling
- Clear error messages if GitHub username doesn't exist
- Handle API rate limits gracefully
- If analysis fails, explain why and suggest alternatives
- Validate inputs before starting analysis

### Security
- No storage of analysis results (stateless)
- No authentication required (public tool)
- Rate limiting to prevent abuse (if deployed publicly)

### User Experience
- Responsive design (works on mobile/tablet/desktop)
- Clear loading states
- Downloadable reports in multiple formats
- Easy to share results

---

## Edge Cases

### Candidate has 100+ repos
- Apply filters aggressively
- Select top 10 by relevance
- Note in report: "Analyzed 10 of 100+ repos, selected by relevance"

### Candidate has NO repos in past year
- Generate "insufficient data" report
- List what was found and why it was excluded
- Provide constructive next steps

### All selected repos need API keys
- Perform static analysis on all
- Note limitation clearly
- Still provide value from static analysis

### GitHub API rate limit hit
- Show clear error message
- Suggest trying again later
- If possible, cache results and resume

### User provides unclear JD
- Agent does best effort extraction
- Note in report if JD was vague
- Make reasonable assumptions and state them

---

## Success Criteria

**The tool is successful if:**

✅ Recruiters can quickly assess technical candidates (vs. manual GitHub browsing)
✅ Reports provide clear hire/no-hire signal
✅ Interview questions are specific and useful
✅ Tool is honest about limitations (doesn't fake analysis)
✅ Handles edge cases gracefully without breaking
✅ Output is professional and shareable

**The report should answer:**
1. Should we interview this candidate? (clear recommendation)
2. What are their technical strengths?
3. What are the potential gaps/concerns?
4. What specific things should we ask in the interview?

---

## Future Enhancements (NOT V1)

- User accounts (save analyses)
- Compare multiple candidates side-by-side
- Integration with ATS systems (Greenhouse, Lever)
- Custom scoring weights (let users adjust priorities)
- Team collaboration (share analyses with colleagues)
- Ongoing monitoring (track candidate's new commits)
- Bulk analysis (upload multiple usernames)

---

## Explicitly Out of Scope

❌ Deep analysis of OSS contributions (high-level summary only)
❌ Analyzing private repos (public only)
❌ Personality or culture fit assessment
❌ Salary recommendations
❌ Skills testing or challenges
❌ Video/phone interview scheduling
❌ Background checks or verification

---

## Implementation Approach

**Build this as a web application with:**
1. Clean, professional UI (React + TypeScript)
2. Backend API for analysis (Python with Claude Agent SDK)
3. Document generation (Word/PDF export)
4. Deployed and accessible via browser

**Testing Strategy:**
Test on diverse GitHub profiles:
- Junior dev with 5 recent projects
- Senior dev with 50+ repos (mostly old)
- Someone with no activity in past year
- Someone with only forks
- Someone with perfect JD match
- Someone with zero JD match

Ensure reports are useful and honest in each case.

---

## UI Wireframes (Text Description)

### Input Screen
```
┌─────────────────────────────────────────────┐
│                                             │
│   GitHub Candidate Analyzer                │
│   Evaluate technical candidates instantly   │
│                                             │
│   ┌───────────────────────────────────────┐ │
│   │ GitHub Username *                     │ │
│   │ [octocat________________]             │ │
│   └───────────────────────────────────────┘ │
│                                             │
│   ┌───────────────────────────────────────┐ │
│   │ Job Description *                     │ │
│   │ ┌───────────────────────────────────┐ │ │
│   │ │Senior Full-Stack Engineer.        │ │ │
│   │ │Required: React, TypeScript...     │ │ │
│   │ │                                   │ │ │
│   │ │                                   │ │ │
│   │ └───────────────────────────────────┘ │ │
│   └───────────────────────────────────────┘ │
│                                             │
│   ┌───────────────────────────────────────┐ │
│   │ Additional Context (Optional)         │ │
│   │ ┌───────────────────────────────────┐ │ │
│   │ │Focus on backend skills...         │ │ │
│   │ └───────────────────────────────────┘ │ │
│   └───────────────────────────────────────┘ │
│                                             │
│          [  Analyze Candidate  ]            │
│                                             │
└─────────────────────────────────────────────┘
```

### Loading Screen
```
┌─────────────────────────────────────────────┐
│                                             │
│   Analyzing @username...                    │
│                                             │
│   ████████████░░░░░░░░░ 60%                │
│                                             │
│   ✓ Fetched GitHub repos                   │
│   ✓ Filtered to 5 relevant repos           │
│   ⏳ Analyzing project 3 of 5...            │
│                                             │
│   This may take 5-15 minutes                │
│                                             │
└─────────────────────────────────────────────┘
```

### Results Screen
```
┌─────────────────────────────────────────────┐
│  [Download Word] [Download PDF] [Copy MD]  │
│                 [New Analysis]              │
├─────────────────────────────────────────────┤
│                                             │
│  # Technical Evaluation: @username          │
│                                             │
│  ## Summary                                 │
│  **Recommendation:** ✅ Interview           │
│  **Match:** 85%                             │
│  ...                                        │
│                                             │
│  [Scrollable report content]                │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Example User Journey

**Step 1:** User visits app homepage

**Step 2:** Fills out form:
- Username: "kentcdodds"
- JD: "Senior Frontend Engineer. React, TypeScript, Testing. Open source experience preferred."
- Additional context: "Prioritize teaching/education experience"

**Step 3:** Clicks "Analyze Candidate"

**Step 4:** Sees progress updates for 8 minutes

**Step 5:** Report displays on screen showing:
- Kent is an excellent match (9/10)
- Strong React, TypeScript, testing expertise
- Massive OSS contributions (epic-react, testing-library)
- Teaching/education is primary focus (matches additional context!)
- Recommendation: Definitely interview

**Step 6:** Downloads as PDF to share with hiring manager

**Step 7:** Uses suggested interview questions in actual interview

---

**End of Spec - Ready for Claude Code**
```

Just copy all of this, save it as a `.md` file, and upload to Claude Code!