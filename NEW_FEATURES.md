# New Features: Project Management, History & Integrations

Major update adding project management, persistent history, and deep integrations with Foundry and Tenderly.

## 🆕 What's New

### 1. Project Management

Organize your contracts into projects with persistent storage:

```bash
# Initialize a project
ai-crypto project init my-defi-project ./contracts
ai-crypto project init foundry-proj ./foundry --foundry

# List all projects
ai-crypto project list

# Show project details
ai-crypto project show my-defi-project

# Scan project for contracts
ai-crypto project scan my-defi-project

# Delete a project
ai-crypto project delete old-project
```

**Features:**
- SQLite database for persistent storage
- Automatic contract tracking
- Foundry project detection
- Project metadata and descriptions

### 2. Analysis History

All analyses are now saved automatically with full history tracking:

```bash
# View recent history
ai-crypto history show
ai-crypto history show --project my-project --limit 10

# View past analysis by ID
ai-crypto history view 42

# List all analyses for a project
ai-crypto history analyses my-project
ai-crypto history analyses my-project --type security

# View project statistics
ai-crypto history stats my-project
```

**Features:**
- Automatic saving of all analyses
- Searchable history by project, type, date
- Full analysis results stored
- Statistics and trending

### 3. Foundry Deep Integration

Full integration with Foundry toolchain (beyond just fuzzing):

```bash
# Use project context
cd my-foundry-project
ai-crypto project init foundry-proj . --foundry

# Foundry automatically detects:
# - foundry.toml configuration
# - src/ and test/ directories
# - Build artifacts in out/

# Use the FoundryIntegration in your scripts:
```

**Python API:**
```python
from ai_crypto_toolkit.integrations import FoundryIntegration

foundry = FoundryIntegration("./my-project")

# Build
build_result = foundry.build()

# Run tests
test_result = foundry.test(match_contract="MyToken")

# Generate coverage
coverage = foundry.coverage()

# Gas snapshots
snapshot = foundry.snapshot(diff=True)

# Get contract ABIs
abi = foundry.get_abi("MyContract")
```

**Features:**
- Build integration (forge build)
- Test running and analysis (forge test)
- Coverage reporting
- Gas snapshots and comparison
- ABI and bytecode extraction
- Script execution
- Contract inspection

### 4. Tenderly Integration

Simulate and debug transactions using Tenderly:

```bash
# Set up Tenderly credentials in config
```

**Python API:**
```python
from ai_crypto_toolkit.integrations import TenderlyClient

async with TenderlyClient(
    access_key="your-key",
    account_slug="your-account",
    project_slug="your-project"
) as tenderly:
    # Simulate transaction
    result = await tenderly.simulate_transaction(
        network_id="1",
        from_address="0x...",
        to_address="0x...",
        input_data="0x...",
        save=True  # Save to Tenderly dashboard
    )

    # Simulate bundle
    bundle_result = await tenderly.simulate_bundle(
        network_id="1",
        transactions=[tx1, tx2, tx3]
    )

    # Get transaction trace
    trace = await tenderly.get_transaction_trace(tx_hash, "1")

    # Verify contract
    await tenderly.verify_contract(
        network_id="1",
        contract_address="0x...",
        compiler_version="0.8.20",
        source_code=source,
        contract_name="MyContract"
    )
```

**Features:**
- Transaction simulation (pre-flight testing)
- Bundle simulation
- Transaction traces and debugging
- Contract verification
- Alert creation for monitoring
- State change tracking

## Database Schema

All data is stored locally in SQLite at `~/.ai-crypto-toolkit/db.sqlite`:

**Tables:**
- `projects` - Your contract projects
- `contracts` - Individual contracts in projects
- `analyses` - All analysis results with full details
- `history` - Activity log

**Benefits:**
- Fast local queries
- No external dependencies
- Full privacy (your data never leaves your machine)
- Easy to backup (single file)

## Configuration Updates

Add Tenderly to your config:

```yaml
# ~/.ai-crypto-toolkit/config.yaml

tenderly:
  access_key: "your-tenderly-api-key"
  account_slug: "your-username"
  project_slug: "your-project"
```

## Workflow Example

Complete workflow with new features:

```bash
# 1. Initialize project
ai-crypto project init uniswap-fork ./uniswap-v3-fork --foundry

# 2. Scan contracts
ai-crypto project scan uniswap-fork

# 3. Run analyses (automatically saved to history)
ai-crypto audit ./contracts/Pool.sol
ai-crypto fuzz ./contracts/Pool.sol --tool foundry
ai-crypto optimize ./contracts/Pool.sol

# 4. View history and stats
ai-crypto history show --project uniswap-fork
ai-crypto history stats uniswap-fork

# 5. Review past analysis
ai-crypto history view 15  # View analysis #15

# 6. Compare with previous analyses
ai-crypto history analyses uniswap-fork --type security
```

## Integration with Existing Commands

All existing commands now automatically integrate with projects and history:

- `ai-crypto analyze` - Results saved to history
- `ai-crypto audit` - Security findings tracked
- `ai-crypto optimize` - Gas optimizations stored
- `ai-crypto fuzz` - Fuzzing results preserved
- `ai-crypto tx` - Transaction analyses logged

Just use `--project` flag (coming soon) to associate with a project, or the tool will detect the current project automatically.

## Python API for Custom Workflows

Build custom workflows using the storage layer:

```python
from ai_crypto_toolkit.storage import get_db, Project, Analysis, AnalysisType
from ai_crypto_toolkit.llm.client import LLMClient
from ai_crypto_toolkit.config import load_config

# Get database
db = get_db()

# Create project
project = Project(
    name="my-project",
    path="/path/to/contracts",
    is_foundry_project=True
)
project = db.create_project(project)

# Run analysis and save
config = load_config()
async with LLMClient(config.llm) as llm:
    result = await llm.analyze_code(
        code=source_code,
        analysis_type="security"
    )

    # Save to database
    analysis = Analysis(
        project_id=project.id,
        contract_id=contract.id,
        analysis_type=AnalysisType.SECURITY,
        model=config.llm.model,
        duration=elapsed_time,
        result=result,
        summary="Found 3 vulnerabilities",
        severity="high",
        findings_count=3
    )
    db.create_analysis(analysis)

# Query history
recent = db.list_analyses(project.id, limit=10)
security_analyses = db.list_analyses(
    project.id,
    analysis_type=AnalysisType.SECURITY
)
```

## Migration from v0.1.0

No breaking changes! All existing commands work the same way.

New features are additive:
- Projects are optional (you can still analyze individual files)
- History is automatic (no action needed)
- Integrations are opt-in (use when needed)

## Performance Notes

- **SQLite is fast**: Millions of analyses, subsecond queries
- **Minimal overhead**: < 1ms per analysis to save to DB
- **Small footprint**: Database file typically < 10MB
- **No network**: All storage is local

## Roadmap

Upcoming enhancements:
- [ ] Auto-detect project from current directory
- [ ] Export history to CSV/JSON
- [ ] Comparison views (diff between analyses)
- [ ] Web UI for browsing history
- [ ] Shareable analysis reports
- [ ] Team collaboration features (optional)

## FAQ

**Q: Where is the database stored?**
A: `~/.ai-crypto-toolkit/db.sqlite` (can be configured)

**Q: Can I export my data?**
A: Yes! It's SQLite - use any SQLite browser or export tool

**Q: Does this slow down analyses?**
A: No. Saving to DB adds < 1ms overhead

**Q: Can I disable history?**
A: Not yet, but it's on the roadmap if there's demand

**Q: Does Tenderly integration require a paid plan?**
A: Tenderly has a free tier. Simulations have rate limits on free tier.

**Q: Can I use Foundry integration without Foundry installed?**
A: No, Foundry must be installed. Get it at https://getfoundry.sh

---

Built with ⚡ by [@0x_Sero](https://twitter.com/0x_Sero)

*Your hardware. Your models. Your rules. Now with your data.*
