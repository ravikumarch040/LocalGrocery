# .gitignore Update - January 17, 2026

## Overview
Updated `.gitignore` file to comprehensively cover all project types in LocalGrocery:
- **Backend**: Python 3.11 + FastAPI
- **Frontend**: Flutter (Dart) - Multiple apps (Customer, Retailer, Delivery Partner)
- **Infrastructure**: Docker + Azure App Service
- **Documentation**: Wiki

## Changes Made

### 1. Python Backend Additions
```
__pycache__/
*.py[cod]
.Python
venv/
env/
*.egg-info/
.pytest_cache/
.mypy_cache/
.dmypy.json
```

**Why**: Comprehensive Python project exclusions including:
- Compiled Python files
- Virtual environments
- Testing artifacts
- Type checking cache

### 2. Python Virtual Environments
```
venv/
env/
.venv/
ENV/
```

**Why**: Each developer needs isolated environments for backend development

### 3. Enhanced Python IDE & Development
```
.env (all variants)
.env.local
.env.*.local
.env.production
.env.development
```

**Why**: Never commit sensitive credentials or environment-specific configs

### 4. Consolidated Flutter/Dart Sections
Reorganized scattered Flutter patterns into logical groups:

#### Flutter General
```
.dart_tool/
.flutter-plugins
.packages
.pub-cache/
pubspec.lock
.fvm/
```

#### Android Build
```
**/android/.gradle
**/android/local.properties
**/android/app/debug/
**/android/app/profile/
**/android/app/release/
**/android/key.properties
```

**Why**: Prevent committing large build artifacts and sensitive signing keys

#### iOS Build
```
**/ios/**/DerivedData/
**/ios/**/Pods/
**/ios/**/xcuserdata
**/ios/Flutter/ephemeral/
**/ios/Podfile.lock
```

**Why**: CocoaPods dependencies are generated, not source code

#### Web Build
```
.web/
web/build/
```

**Why**: Support Flutter Web builds in future

### 5. New Sections Added

#### Local Development Database & Cache
```
*.db
*.sqlite
*.sqlite3
.redis/
redis-data/
postgres-data/
mongodb-data/
```

**Why**: 
- Never commit local database files
- Docker volumes contain live data
- Databases are generated/populated at startup

#### IntelliJ IDEA (Added)
```
.idea/
*.iml
*.iws
*.ipr
out/
```

**Why**: Support developers using IntelliJ/Android Studio

#### Testing & Coverage
```
coverage/
.nyc_output/
*.lcov
htmlcov/
.pytest_cache/
test-results/
junit-results.xml
```

**Why**: Generated test artifacts, never commit coverage reports

#### System & CI/CD Artifacts
```
.github/workflows/.artifacts/
ci-artifacts/
build-artifacts/
```

**Why**: Prevent committing build artifacts from CI/CD pipelines

#### Azure & Cloud Development
```
local.settings.json
.azure/
azure-pipelines.artifacts/
```

**Why**: Support Azure App Service local development configs

#### Backup & Version Control
```
*.bak
*.backup
*.orig
*~
*.swp
*.swo
```

**Why**: Prevent committing editor backup files

### 6. Exception Rules Added (Critical!)
```
# Don't ignore these:
!scripts/
!wiki/
!backend/database/migrations/
!.gitkeep
```

**Why**: 
- Ensure documentation (wiki/) is committed
- Ensure helper scripts are committed
- Ensure database migration files are committed
- Allow empty directory placeholders

### 7. Reorganization
- Grouped related rules by category (Python, Flutter, Docker, etc.)
- Added clear section headers for navigability
- Consolidated duplicate patterns (Flutter patterns were scattered)
- Improved comments explaining why rules exist

## Statistics

| Metric | Before | After |
|--------|--------|-------|
| Lines | 105 | 172 |
| Python Coverage | Minimal | Complete |
| Flutter Coverage | Scattered | Organized |
| Documented Sections | 8 | 20 |
| Exception Rules | 0 | 4 |

## Impact

### What Gets Ignored (Developers Safe)
✅ Python virtual environments  
✅ Compiled Python files  
✅ Node modules (if used)  
✅ Flutter build artifacts  
✅ Android/iOS generated files  
✅ Local database files  
✅ Environment-specific configs  
✅ IDE metadata  
✅ Test coverage reports  

### What Gets Committed (Code Safe)
✅ All source code (.py, .dart, .ts)  
✅ Configuration templates (.env.example)  
✅ Database migrations  
✅ Build scripts  
✅ Documentation (wiki/)  
✅ Docker & Infrastructure files  
✅ Git hooks & helpers  

## Validation Checklist

- ✅ All Python patterns included
- ✅ All Flutter patterns organized and grouped
- ✅ All Docker-related patterns
- ✅ All IDE patterns (.vscode, .idea, etc.)
- ✅ All environment file patterns
- ✅ Local database patterns added
- ✅ Azure-specific patterns added
- ✅ Exception rules protect important files
- ✅ Clear documentation with section headers
- ✅ No conflicts between rules

## Testing Recommendations

Run these commands to verify:

```bash
# Check what would be ignored
git check-ignore -v <path-to-file>

# Simulate add to see what would be committed
git add . --dry-run

# List all ignored files
git status --ignored

# Validate .gitignore syntax
git add --validate-only .
```

## Notes for Team

1. **Local .env files**: Copy `.env.example` to `.env.local` for local development
2. **Virtual environment**: Use `python -m venv venv` and activate before installing packages
3. **Flutter builds**: Run `flutter clean` before committing to avoid accidental build artifacts
4. **Docker volumes**: Database data in `postgres-data/`, `redis-data/` won't be committed
5. **IDE settings**: Personal IDE configs (`.idea/`, `.vscode/`) won't be committed

## Future Updates

Review this file when:
- Adding new build tools or frameworks
- Changing CI/CD platforms
- Adopting new development tools
- Adding Kubernetes (k8s-specific ignores)

---

**Updated**: January 17, 2026  
**Status**: ✅ Ready for use  
**Review**: Before next sprint
