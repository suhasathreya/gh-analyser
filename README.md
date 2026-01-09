# GitHub Candidate Analyzer

An autonomous AI-powered tool for analyzing GitHub profiles of technical candidates. Built with Claude Agent SDK and FastAPI.

## Features

- 🤖 **Autonomous Analysis** - Claude Agent SDK analyzes repos, runs tests, examines code quality
- 📊 **Comprehensive Reports** - Detailed evaluation with hire/no-hire recommendations
- ⚡ **Smart Filtering** - Focuses on recent, relevant projects (past 12 months)
- 🧪 **Full Execution** - Clones repos, installs dependencies, runs tests when possible
- 📄 **Multiple Export Formats** - Download as PDF, Word, or Markdown
- 🎯 **Interview Questions** - Generates specific questions based on actual code

## Prerequisites

- Python 3.13+ (you have this installed)
- Node.js (for Claude Code CLI - you already have this)
- Git
- Claude Code CLI (you're using it right now!)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/suhasathreya/gh-analyser.git
cd gh-analyser
```

### 2. Install Dependencies

```bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Set Up API Keys

Create a `.env` file (copy from `.env.example`) and add your API keys:

```env
# Required - Get from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional - Get from https://github.com/settings/tokens
# Recommended for higher rate limits (60/hour -> 5000/hour)
GITHUB_TOKEN=ghp_your-token-here
```

**To get your Anthropic API key:**
1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to API Keys
4. Create a new key
5. Copy and paste into `.env`

**To get a GitHub token (optional but recommended):**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Generate and copy the token
5. Paste into `.env`

### 4. Run the Application

```bash
# Start the server
uvicorn app.main:app --reload

# Or use Python directly
python -m app.main
```

The application will be available at http://localhost:8000

### 4. Analyze a Candidate

1. Open http://localhost:8000 in your browser
2. Enter:
   - GitHub username (e.g., "torvalds", "gvanrossum")
   - Job description with requirements
   - Additional context (optional)
3. Click "Analyze Candidate"
4. Wait 5-15 minutes for the analysis to complete
5. View the comprehensive report
6. Download as PDF, Word, or copy Markdown

## How It Works

```
User submits form
      ↓
FastAPI spawns background task
      ↓
Claude Agent SDK runs autonomously:
  1. Fetches repos from GitHub API
  2. Filters by recency, relevance, forks
  3. Scores and selects top 10 repos
  4. For each repo:
     - Clones it
     - Examines code structure
     - Runs tests (if possible)
     - Analyzes quality, patterns, practices
  5. Generates comprehensive markdown report
      ↓
User sees progress updates every 10 seconds
      ↓
Report displays with export options
```

## Project Structure

```
gh-analyser/
├── app/
│   ├── main.py              # FastAPI application
│   ├── agent.py             # Claude Agent SDK wrapper
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── progress.html
│   │   └── results.html
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/progress.js
│   └── utils/
│       └── export.py        # PDF/DOCX generation
├── analyses/                # Analysis results (git ignored)
├── requirements.txt
├── .env                     # API keys (git ignored)
└── README.md
```

## Analysis Criteria

The agent automatically:

- **Excludes:**
  - Forks (not original work)
  - Repos not updated in 12+ months
  - Repos with < 5 commits in past year
  - Tutorial/learning projects

- **Scores (0-100):**
  - Tech stack match to JD: 70%
  - Recency: 20%
  - Activity level: 10%

- **Selects:**
  - Top 10 repos with score ≥ 30

## Report Contents

Each analysis includes:

1. **Summary** - Overall score, recommendation, strengths, red flags
2. **Projects Analyzed** - Detailed analysis of top repos
3. **Contribution Patterns** - Commit frequency, velocity, work style
4. **Technical Profile** - Skills, specialization, growth
5. **Match to JD** - Skill-by-skill comparison
6. **Interview Questions** - Specific questions based on code
7. **Overall Assessment** - Final recommendation with justification

## Troubleshooting

### "Analysis failed" Error

- **Check API Keys:** Ensure `ANTHROPIC_API_KEY` is set in `.env`
- **Verify Username:** Make sure the GitHub username is valid
- **Public Repos:** User must have public repositories
- **Check Logs:** Look at the terminal output for detailed error messages

### Tests Not Running

This is normal! The agent attempts to run tests but gracefully handles failures:
- Missing dependencies
- Requires API keys
- Long installation times

The agent will note this in the report and continue with static analysis.

### Analysis Taking Too Long

- **Normal:** 5-15 minutes is expected
- **Check Progress:** Status updates every 10 seconds
- **Network:** Ensure stable internet connection
- **Large Repos:** The agent may skip extremely large repos

## Configuration

### Adjusting Analysis Behavior

Edit `app/agent.py` to customize:
- Number of repos analyzed (default: 10)
- Score threshold (default: 30/100)
- Time filters (default: 12 months)
- Hard filters (tutorials, forks, etc.)

### Changing Server Port

```bash
uvicorn app.main:app --port 3000 --reload
```

## Export Formats

### PDF
- Styled, professional layout
- Preserves formatting and code blocks
- Ready to share with stakeholders

### Word (.docx)
- Editable format
- Compatible with Microsoft Word, Google Docs
- Can add comments and annotations

### Markdown
- Raw format
- Easy to copy into Notion, Confluence, etc.
- Version control friendly

## Development

### Running in Development Mode

```bash
# Auto-reload on file changes
uvicorn app.main:app --reload
```

### Testing with Different Profiles

Good test candidates:
- `torvalds` - Linux creator (many old repos)
- `gvanrossum` - Python creator
- `tj` - Node.js ecosystem contributor
- `addyosmani` - Frontend expert

## Limitations (MVP)

- ⏱️ **Execution Time:** 5-15 minutes per analysis
- 📦 **Static Analysis Only for Some:** Can't run tests if deps require API keys
- 💾 **No Database:** File-based storage, no analysis history
- 🔐 **No Authentication:** Public tool, anyone can use
- 📊 **No Caching:** Re-analyzes same user each time

## Future Enhancements

- User accounts and analysis history
- Compare multiple candidates side-by-side
- WebSocket progress streaming
- Docker isolation for repo execution
- Integration with ATS systems (Greenhouse, Lever)
- Custom scoring weights
- Bulk analysis (multiple candidates)

## Tech Stack

- **Backend:** FastAPI + Python 3.13
- **AI:** Claude Agent SDK (Opus 4.5)
- **Frontend:** Jinja2 templates + Tailwind CSS
- **Export:** python-docx, weasyprint
- **Markdown:** marked.js

## License

MIT License - See LICENSE file

## Support

- **Issues:** Report bugs or request features
- **Questions:** Check the spec.md for detailed requirements

## Credits

Built with:
- [Claude Agent SDK](https://platform.claude.com/docs/agent-sdk)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Happy Recruiting!** 🚀
