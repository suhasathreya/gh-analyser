# GitHub Candidate Analyzer: Technical Architecture and Business Analysis

**Author:** Technical Architecture Team
**Date:** January 2026
**Classification:** Internal Technical Document

---

## Executive Summary

This document presents the technical architecture, design decisions, and business analysis for the GitHub Candidate Analyzer, an autonomous AI-powered system designed to evaluate software engineering candidates by analyzing their public GitHub profiles. The system addresses a critical inefficiency in technical recruiting: the time-intensive, inconsistent, and subjective nature of manual GitHub profile reviews.

The solution leverages Claude Agent SDK to perform autonomous code analysis, executing a sophisticated workflow that includes repository discovery, filtering, cloning, static and dynamic analysis, test execution, and comprehensive report generation. Initial development required approximately ten hours and demonstrates significant cost savings potential, reducing per-candidate screening time from three hours to fifteen minutes while providing objective, consistent technical evaluation.

---

## Problem Statement

### Current State of Technical Recruiting

Technical recruiting organizations face substantial challenges in evaluating software engineering candidates. The typical hiring process requires recruiters to manually review candidates' GitHub profiles to assess technical competency, code quality, and fit for specific roles. This manual review process is characterized by several critical inefficiencies.

First, the time investment is substantial. A thorough review of a candidate's GitHub profile requires between two and three hours per candidate. Recruiters must navigate dozens or hundreds of repositories, identify which projects are relevant to the position, examine code quality, assess testing practices, and form opinions about the candidate's technical capabilities. For organizations screening ten candidates per quarter, this represents thirty hours of recruiter time dedicated solely to GitHub profile analysis.

Second, the quality and consistency of these evaluations varies significantly. Non-technical recruiters struggle to assess code quality, architectural decisions, and testing practices. Even technical recruiters apply subjective criteria that vary between individuals. There is no standardized methodology for evaluating candidates, leading to inconsistent hiring decisions and potential loss of qualified candidates.

Third, distinguishing signal from noise presents a persistent challenge. Candidates' GitHub profiles typically contain a mixture of original work, forked repositories, tutorial projects, old abandoned code, and recent active development. Manually filtering this content to identify relevant, recent, substantive work requires significant effort and domain expertise.

Fourth, the output of manual reviews rarely includes actionable insights. Recruiters may form general impressions about a candidate's abilities but struggle to generate specific, code-based interview questions that probe actual demonstrated competencies.

### Quantified Impact

The economic impact of these inefficiencies is measurable. Consider a mid-sized technology company hiring ten engineers per quarter. At a loaded recruiter cost of seventy-five dollars per hour, manual GitHub screening represents $2,250 in direct costs per quarter, or $9,000 annually. This calculation excludes opportunity costs from slower hiring processes, the risk of inconsistent evaluation leading to poor hiring decisions, and the inability to screen larger candidate pools due to time constraints.

Poor hiring decisions carry particularly high costs. Industry research suggests the cost of a bad engineering hire ranges from $50,000 to $100,000 when accounting for salary, onboarding time, productivity loss, and eventual replacement. If inconsistent screening contributes to even one poor hire per year, the total cost significantly exceeds the direct screening costs.

### The Opportunity

An automated solution capable of performing consistent, objective technical evaluation would address these challenges directly. Such a system would need to autonomously identify relevant repositories, analyze code quality, assess testing practices, evaluate fit against job requirements, and generate actionable insights for interview preparation. The system would need to complete this analysis in a fraction of the time required for manual review while maintaining or exceeding the quality of human evaluation.

---

## Solution Architecture

### System Design Philosophy

The GitHub Candidate Analyzer implements an autonomous agent architecture rather than a traditional rules-based system. This design choice reflects the inherently subjective and context-dependent nature of code quality assessment. Rather than attempting to codify rigid evaluation criteria, the system leverages large language model reasoning to make nuanced judgments about code organization, testing practices, documentation quality, and technical fit.

The architecture consists of three primary components: a web application layer built with FastAPI, an autonomous analysis agent powered by Claude Agent SDK, and a file-based storage system for analysis results and progress tracking.

### Web Application Layer

The web application layer serves as the user interface and orchestration layer. Built using FastAPI, a modern Python web framework, it provides REST API endpoints for initiating analyses, tracking progress, and retrieving results. The choice of FastAPI over alternatives such as Flask or Django reflects several technical requirements.

FastAPI provides native support for asynchronous request handling, which is essential for managing long-running background tasks without blocking the web server. The framework's built-in Pydantic validation ensures type safety at the API boundary, preventing runtime errors from malformed inputs. Additionally, FastAPI automatically generates OpenAPI documentation, simplifying future API integrations and debugging.

The application uses Jinja2 templating for server-side HTML rendering rather than implementing a separate JavaScript frontend. This architectural decision prioritizes simplicity and development velocity. The analysis workflow is fundamentally backend-heavy, with the frontend serving primarily to collect input parameters and display results. A single-page application framework would introduce complexity without corresponding benefits for this use case.

When a user submits an analysis request, the application generates a unique identifier, creates a working directory for that analysis, and spawns a background task to execute the agent. The application immediately returns a response to the user with the analysis identifier and a URL for tracking progress. This asynchronous pattern ensures the web server remains responsive even during lengthy analysis operations.

### Autonomous Analysis Agent

The analysis agent represents the core intelligence of the system. Built using Claude Agent SDK, it executes a sophisticated multi-step workflow without human intervention. The agent has access to several tools that enable it to interact with the file system and execute commands: Bash for running shell commands, Read for examining file contents, Write for creating output files, Grep for searching within files, and Glob for file pattern matching.

The agent's workflow begins with repository discovery. It queries the GitHub API to retrieve all public repositories for the specified username, handling pagination to ensure complete data collection. The API response provides metadata including repository names, descriptions, primary language, last update timestamp, fork status, and star count.

Following discovery, the agent applies a filtering methodology to identify relevant repositories. Hard filters eliminate repositories that are forks rather than original work, repositories not updated within the past twelve months, repositories with fewer than five commits in the past year, and repositories whose names suggest they are tutorial or learning projects. These filters ensure the analysis focuses on recent, substantial, original work.

The agent then scores remaining repositories on a scale of zero to one hundred. The scoring algorithm weights technical stack alignment with job requirements at seventy percent, recency of activity at twenty percent, and overall activity level at ten percent. Repositories scoring below thirty are excluded. The agent selects up to ten repositories with the highest scores for detailed analysis.

For each selected repository, the agent clones the codebase to a temporary directory and performs both static and dynamic analysis. Static analysis includes examining project structure and organization, identifying architectural patterns, reviewing dependency management, assessing documentation quality, and analyzing git commit history. The agent uses the Read tool to examine key files such as README documentation, package manifests, and configuration files. It uses Glob to identify source files, test files, and configuration artifacts. It uses Grep to search for specific patterns indicating good or poor practices.

Dynamic analysis attempts to execute the project's test suite when possible. The agent identifies the project's technology stack from manifest files and attempts appropriate installation and test commands. For JavaScript projects with package.json files, it executes npm install followed by npm test. For Python projects with requirements.txt files, it executes pip install followed by pytest. For Go projects, it executes go test. When test execution succeeds, the agent captures output including pass/fail status and coverage metrics. When execution fails due to missing API keys, external service dependencies, or other environmental requirements, the agent notes the limitation and continues with static analysis.

Throughout the analysis, the agent maintains a status file indicating current progress. After completing repository analysis, the agent generates a comprehensive markdown report. The report includes an executive summary with an overall score, match percentage to job requirements, code quality assessment, experience level estimation, and a hire/no-hire recommendation. It provides detailed analysis of the top three repositories, including architecture assessment, testing practices, code quality observations, and specific strengths and weaknesses. It summarizes contribution patterns such as commit frequency and collaboration style. It maps evidence of required skills against the job description. It generates specific interview questions based on actual code patterns observed in the candidate's repositories.

### Storage Architecture

The system uses file-based storage rather than a traditional database. Each analysis creates a directory identified by a unique UUID. Within that directory, the system stores a status.json file for progress tracking, a report.md file containing the generated analysis, and a repos subdirectory containing cloned repositories.

This storage architecture prioritizes simplicity for the initial implementation. File-based storage requires no schema migrations, no database connection management, and no object-relational mapping complexity. The storage is transparent and easily debugged by directly examining files. Analysis results are self-contained within their directories, simplifying backup and archival processes.

The trade-off is the inability to perform complex queries across analyses. Features such as comparing multiple candidates, tracking trends over time, or searching historical analyses would require scanning all directories. For production deployment at scale, migration to a relational database such as PostgreSQL would be necessary.

---

## Technology Selection Rationale

### Claude Agent SDK versus Alternatives

The selection of Claude Agent SDK as the core analysis engine represents a critical architectural decision. Several alternatives were considered, including LangChain with various language models, OpenAI Assistants API, AutoGPT, and custom integration with language model APIs.

Claude Agent SDK provides several distinct advantages for this use case. First, it is explicitly designed for autonomous, long-running tasks. The analysis workflow requires five to fifteen minutes of execution without human intervention. The SDK handles the complexity of tool execution loops, error recovery, and state management. Alternative frameworks such as LangChain would require custom implementation of these orchestration concerns.

Second, the SDK provides a comprehensive built-in tool suite including file system operations and command execution. The analysis workflow fundamentally requires the ability to clone repositories, read source files, execute builds and tests, and write output files. These capabilities are native to Claude Agent SDK. Alternative solutions would require implementing custom tools or working within more restrictive sandboxes.

Third, Claude Opus 4.5, the language model underlying the SDK, demonstrates sophisticated reasoning capabilities essential for nuanced code quality assessment. The model can identify architectural patterns, recognize testing anti-patterns, assess documentation completeness, and make contextual judgments about code organization. These capabilities exceed what is achievable with purely rule-based systems.

The primary trade-off is cost. Claude Opus pricing is approximately three to four times higher than GPT-4 pricing for equivalent token volumes. A typical analysis consumes approximately thirty-three thousand tokens including input context, tool use, and output generation, resulting in a cost of approximately $1.10 per analysis. A comparable implementation using GPT-4 might cost $0.30 to $0.50. However, the development time savings and superior reasoning capabilities justify this premium for the initial implementation.

An additional consideration is vendor dependency. The system requires an Anthropic API key and is tightly coupled to Claude's tool-use patterns and capabilities. Migration to a different language model would require substantial re-architecture. This dependency is acceptable given Anthropic's strong track record and the rapidly evolving nature of the language model landscape.

### FastAPI versus Alternatives

The selection of FastAPI for the web application layer reflects requirements for asynchronous task handling, type safety, and development velocity. Flask, a popular Python web framework, lacks native async/await support, requiring additional libraries for background task management. Django, while feature-rich, introduces unnecessary complexity for this application's relatively simple web layer.

FastAPI's Pydantic integration provides compile-time type checking and runtime validation, preventing entire classes of bugs related to malformed inputs. The framework automatically generates OpenAPI specifications, simplifying API documentation and future integration work.

The decision to use server-side rendering with Jinja2 templates rather than a JavaScript single-page application framework represents a pragmatic choice. The initial implementation included plans for a Next.js frontend with React components. Analysis of requirements revealed that the application's complexity resides almost entirely in the backend analysis logic. The frontend primarily collects three text inputs and displays a markdown report with progress tracking. Introducing a separate JavaScript build pipeline, managing frontend-backend API contracts, and coordinating two separate deployment artifacts would add complexity without commensurate benefits.

This decision does impose limitations. The current polling-based progress updates create a ten-second lag between agent progress and user visibility. A WebSocket-based implementation would provide real-time updates. However, the implementation complexity of WebSockets, including connection management, reconnection logic, and firewall traversal, is not justified for the current use case.

### File-based Storage versus Database

The file-based storage architecture represents a deliberate choice to minimize implementation complexity for the initial version. Each analysis is independent and self-contained. There are no relationships between analyses, no need for transactional integrity, and no complex queries required.

File-based storage provides several advantages. Implementation is trivial, requiring only directory creation and JSON serialization. Debugging is transparent, as developers can directly examine status files and reports. Backup and archival operations use standard file system tools. There is no database server to install, configure, or maintain.

The limitations become apparent when considering features beyond basic analysis execution. User authentication would require storing user records. Analysis history would require indexing and searching across directories. Comparing multiple candidates would require loading and correlating multiple result files. These operations are inefficient with file-based storage.

The appropriate migration path is to introduce PostgreSQL when implementing user-facing features such as authentication, history, and comparison. The analysis execution logic can remain file-based for isolation and simplicity, while metadata and user information move to the database.

---

## Cost Structure and Economic Analysis

### Per-Analysis Cost Breakdown

The direct cost of performing an analysis consists primarily of API usage charges from Anthropic. A typical analysis workflow includes the initial prompt describing the analysis task (approximately eight thousand tokens), tool use operations as the agent executes Bash commands, reads files, and searches code (approximately twenty thousand tokens), and the generated report output (approximately five thousand tokens). At Claude Opus 4.5 pricing of fifteen dollars per million input tokens and seventy-five dollars per million output tokens, this results in approximately $1.10 per analysis.

Infrastructure costs depend on deployment architecture. For local development, infrastructure costs are zero. For cloud deployment on a platform-as-a-service such as Railway or Render, costs would approximate ten to twenty dollars per month for light usage, supporting hundreds of analyses. For self-managed infrastructure on AWS EC2, a t3.medium instance adequate for this workload costs approximately thirty dollars per month.

GitHub API usage remains within the free tier limits (five thousand requests per hour with authentication) for reasonable usage patterns. Each analysis requires five to fifteen API calls depending on pagination requirements.

### Return on Investment Analysis

The economic value proposition becomes clear when comparing automated analysis costs to manual screening costs. Consider a recruiting organization screening ten candidates per quarter. Under the current manual process, each candidate requires three hours of recruiter time at a loaded cost of seventy-five dollars per hour, totaling $225 per candidate or $2,250 per quarter.

With automated analysis, the time requirement decreases to fifteen minutes of recruiter time to review the generated report, plus the API cost of $1.10. The recruiter cost becomes $18.75, for a total of $19.85 per candidate. For ten candidates, the quarterly cost is $198.50, representing savings of $2,051.50 or ninety-one percent.

The break-even point is reached on the first analysis. The payback period is immediate. The system justifies its development and operational costs with a single use.

Beyond direct cost savings, the system provides several additional value drivers. The ability to screen candidates more quickly reduces time-to-hire, a critical metric in competitive technical recruiting markets. The consistency of evaluation reduces the risk of poor hiring decisions, which carry costs ranging from $50,000 to $100,000. The generation of specific, code-based interview questions increases the signal extracted from technical interviews.

### Pricing Strategy for Commercial Offering

If developed as a commercial product, the system could support several pricing tiers. A pay-as-you-go tier at five dollars per analysis serves occasional users and provides a low-friction entry point. A subscription tier at ninety-nine dollars per month including thirty analyses (effective cost of $3.30 per analysis) targets individual recruiters and small agencies. A team tier at $299 per month including one hundred analyses (effective cost of $3.00 per analysis) provides volume pricing for larger organizations. An enterprise tier with custom pricing addresses organizations requiring unlimited analyses, private repository access, and API integration.

At these price points, gross margins would approximate sixty to seventy percent, accounting for direct API costs and infrastructure overhead. The primary cost structure is variable (API usage) rather than fixed, creating favorable unit economics.

Conservative projections suggest fifty customers at the individual tier and ten customers at the team tier would generate monthly recurring revenue of approximately $7,940, or annual recurring revenue of $95,280. At 2,500 total analyses per month and $1.10 cost per analysis, monthly API costs would be $2,750, yielding gross margin of sixty-five percent. Break-even would occur at approximately fifteen to twenty customers, depending on operational overhead.

---

## Technical Implementation Challenges and Solutions

### Challenge: Agent File Path Handling

The initial implementation encountered an issue where the agent wrote output files to incorrect locations. Analysis logs revealed the agent was creating files at paths such as /Users/user/repos/report.md rather than using the configured working directory.

Investigation revealed that the Claude Agent SDK's working directory parameter functions as a suggestion to the agent but does not strictly constrain file operations. The agent has access to the Bash, Read, and Write tools and can specify any file path when invoking these tools. The language model's training data likely includes many examples of absolute file paths in Unix-like environments, leading it to generate absolute paths rather than relative paths.

The solution was to explicitly instruct the agent in the prompt to use relative file paths. The prompt now includes specific directives: "Use Write tool to save markdown report to: ./report.md (current directory). DO NOT use absolute paths like /Users/user/repos/report.md. ALWAYS use relative paths starting with ./"

This approach proved more reliable than attempting to configure path handling through parameters alone. The lesson is that autonomous agents require explicit instruction about behaviors that might seem implicit from configuration. The language model follows the patterns it observes in its prompt more reliably than it respects configuration parameters.

### Challenge: Unicode Encoding on Windows

Analysis execution failed on Windows systems with encoding errors when attempting to write files containing emoji characters. The error message indicated that the 'charmap' codec could not encode certain Unicode characters.

The root cause was Windows' default file encoding, which uses the system's code page (typically cp1252 for Western European locales) rather than UTF-8. When the agent generated reports containing emoji characters such as checkmarks, warning symbols, and status indicators, Python's file writing operations failed because these characters do not exist in the cp1252 encoding.

The solution required explicitly specifying UTF-8 encoding when opening files for writing. All file writing operations now use the pattern: open(file_path, "w", encoding="utf-8"). This ensures consistent behavior across operating systems and supports the full range of Unicode characters that language models may generate.

The broader lesson is that systems integrating with language model outputs must handle Unicode robustly. Language models are trained on internet-scale text corpora that include extensive use of Unicode characters, and their outputs will naturally include these characters unless explicitly constrained.

### Challenge: Development Server Interference

During testing, analysis execution would consistently fail with cryptic error messages about command failures and exit codes. The errors were non-deterministic and difficult to reproduce. Investigation of the server logs revealed that the FastAPI development server was restarting during analysis execution.

The cause was Uvicorn's auto-reload feature, which monitors the file system for changes and automatically restarts the server when files are modified. During analysis, the agent clones repositories into the analyses directory, creating and modifying numerous files. These file system changes triggered Uvicorn to restart, terminating the agent process mid-execution.

The immediate solution was to run the server without the --reload flag during analysis execution. The more robust solution for development workflows is to configure Uvicorn to exclude the analyses directory from reload monitoring using the --reload-exclude parameter.

This issue highlights an important consideration for systems that perform file system operations as part of their core functionality. Development tools that assume file system changes indicate code modifications can interfere with application logic that legitimately creates and modifies files during normal operation.

### Challenge: Progress Tracking and User Experience

The asynchronous nature of the analysis process creates a user experience challenge. After submitting an analysis request, users must wait five to fifteen minutes for completion. Without feedback, users cannot distinguish between normal processing, system failure, or indefinite hanging.

The solution implements a polling-based progress tracking system. The agent writes progress updates to a status.json file after completing major workflow steps. The web application provides an endpoint that returns the current status. The frontend polls this endpoint every ten seconds and updates a progress bar and status message.

This approach has limitations. Progress updates lag by up to ten seconds. The agent may spend several minutes on a single step, creating periods where visible progress stalls. More sophisticated approaches such as WebSocket-based streaming would provide real-time updates but introduce significant implementation complexity.

The key insight is that the progress tracking system serves primarily to reassure users that processing is ongoing rather than to provide precise completion estimates. Approximate progress indication with regular updates proves sufficient for user satisfaction.

---

## System Limitations and Future Development

### Current System Constraints

The current implementation includes several limitations that would require addressing for production deployment at scale.

PDF export functionality requires system library dependencies that are platform-specific and difficult to install on Windows. The WeasyPrint library depends on GTK libraries for rendering. While Word document export and Markdown copying function correctly, the PDF export feature is not reliable across all platforms. Future implementations should consider browser-based PDF rendering or pure-Python PDF generation libraries.

The system maintains no persistent state beyond individual analysis results. There is no user authentication, no analysis history, and no ability to compare multiple candidates. These features would be essential for a production offering but were explicitly deferred from the initial implementation to minimize complexity.

Analysis execution is single-threaded. The system processes one analysis at a time. While the web server can handle multiple concurrent requests, background task execution is serial. Implementing parallel analysis would require a job queue system such as Celery with Redis, adding infrastructure complexity.

The analysis executes cloned repositories in temporary directories without isolation or sandboxing. While the system analyzes only public repositories from established GitHub accounts, there exists theoretical risk from malicious repository content. Production deployment should consider executing analyses within Docker containers for isolation.

The system can only analyze public repositories. Many strong candidates work primarily on proprietary codebases and maintain limited public GitHub presence. Accessing private repositories would require implementing an OAuth flow to obtain user authorization, adding authentication complexity.

Analysis criteria such as the twelve-month recency filter and scoring weights are hardcoded. Different organizations may have different priorities. A production system should allow customization of filtering and scoring parameters.

The cost per analysis of approximately $1.10 is higher than alternatives using less expensive language models. Organizations performing hundreds of analyses monthly may prefer a lower-cost option with acceptable quality trade-offs. Offering a choice between Claude Opus (premium quality, higher cost) and Claude Sonnet (good quality, lower cost) would provide flexibility.

### Development Roadmap

Future development would logically proceed in phases addressing these limitations.

Phase two development would introduce persistent storage and user management. This phase would add PostgreSQL for storing user accounts, analysis metadata, and system configuration. User authentication would enable features such as analysis history, saved job descriptions, and usage tracking. A dashboard interface would display historical analyses with search and filtering capabilities. Multi-candidate comparison would allow side-by-side evaluation of multiple candidates against the same job requirements.

Phase three development would focus on scalability and integration. Implementation of a job queue system would enable parallel analysis execution and better resource utilization. Private repository support via OAuth integration would expand the candidate pool. Integration with applicant tracking systems such as Greenhouse and Lever would embed analysis capabilities directly into existing recruiting workflows. Team collaboration features would allow sharing analyses among hiring team members.

Phase four development would add advanced capabilities and intelligence. Bulk analysis from CSV uploads would streamline processing of candidate lists. Ongoing monitoring of analyzed candidates would detect new repository activity and update assessments. Machine learning models trained on hire/no-hire outcomes would refine scoring algorithms. Custom report templates would adapt output format to organizational preferences. API access would enable programmatic integration with custom tools and workflows.

---

## Conclusion

The GitHub Candidate Analyzer demonstrates the viability of autonomous AI agents for complex, multi-step analytical workflows. The system successfully automates a time-intensive manual process, reducing screening time by ninety-one percent while providing consistent, objective evaluation. The technical architecture leverages Claude Agent SDK's autonomous capabilities to execute sophisticated analysis without human intervention. The implementation validates the business case for AI-powered recruiting tools and establishes a foundation for commercial development.

The technology selection reflects pragmatic trade-offs between development velocity, operational cost, and system capabilities. Claude Agent SDK provides powerful autonomous capabilities at premium pricing. FastAPI offers modern Python web development with minimal complexity. File-based storage simplifies initial implementation while creating a clear migration path to database-backed features.

The primary technical challenges encountered—file path handling, Unicode encoding, development server interference, and progress tracking—were resolved through explicit prompt engineering, proper encoding specification, configuration adjustments, and polling-based status updates. These solutions inform best practices for building systems that integrate autonomous AI agents into traditional web applications.

The economic analysis demonstrates clear value proposition with immediate return on investment. Direct cost savings of ninety-one percent create compelling justification. Additional value from faster hiring, consistent evaluation, and improved interview preparation strengthens the business case. Commercial pricing strategies with sixty to seventy percent gross margins indicate sustainable business model potential.

Future development would address current limitations through phased enhancements to storage architecture, scalability infrastructure, integration capabilities, and analytical sophistication. The clear roadmap from minimal viable product to full-featured commercial offering provides confidence in the long-term viability of this approach.

The development process required approximately ten hours from initial planning through working implementation, demonstrating that sophisticated AI-powered tools can be built rapidly with modern frameworks and APIs. This efficiency suggests significant opportunities for applying similar architectural patterns to other domain-specific analytical workflows.
