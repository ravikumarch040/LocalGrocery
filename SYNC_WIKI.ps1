param(
    [string]$WikiRepoUrl = "https://github.com/ravikumarch040/LocalGrocery.wiki.git",
    [string]$WikiCloneDir = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $WikiCloneDir) {
    $WikiCloneDir = Join-Path (Split-Path -Parent $root) "LocalGrocery.wiki"
}

$copyMapPath = Join-Path $root "WIKI_COPY_MAP.md"
$sidebarPath = Join-Path $root "WIKI_SIDEBAR.md"
$orderPath = Join-Path $root "GITHUB_WIKI_PAGE_ORDER.md"

if (-not (Test-Path $copyMapPath)) {
    throw "Missing file: $copyMapPath"
}
if (-not (Test-Path $sidebarPath)) {
    throw "Missing file: $sidebarPath"
}

function Ensure-WikiRepo {
    param(
        [string]$RepoUrl,
        [string]$CloneDir,
        [switch]$NoWrite
    )

    if (-not (Test-Path $CloneDir)) {
        if ($NoWrite) {
            Write-Host "[DRY RUN] Would clone wiki repo into: $CloneDir"
            return
        }
        Write-Host "Cloning wiki repo to: $CloneDir"
        git clone $RepoUrl $CloneDir | Out-Host
        return
    }

    $gitDir = Join-Path $CloneDir ".git"
    if (-not (Test-Path $gitDir)) {
        throw "Path exists but is not a git repo: $CloneDir"
    }

    if ($NoWrite) {
        Write-Host "[DRY RUN] Would pull latest changes in: $CloneDir"
        return
    }

    Write-Host "Pulling latest wiki changes in: $CloneDir"
    git -C $CloneDir pull --ff-only | Out-Host
}

function Parse-CopyMap {
    param(
        [string]$MapFile
    )

    $pairs = @()
    $lines = Get-Content -Path $MapFile
    foreach ($line in $lines) {
        if ($line -match '^\-\s+`([^`]+)`\s+\-\>\s+`([^`]+)`$') {
            $pairs += [PSCustomObject]@{
                Source = $Matches[1]
                Target = $Matches[2]
            }
        }
    }
    return $pairs
}

function Copy-DocsToWiki {
    param(
        [string]$SourceRoot,
        [string]$WikiDir,
        [array]$Pairs,
        [switch]$NoWrite
    )

    $copied = 0
    $missing = 0

    foreach ($pair in $Pairs) {
        $sourcePath = Join-Path $SourceRoot $pair.Source
        $targetPath = Join-Path $WikiDir $pair.Target

        if (-not (Test-Path $sourcePath)) {
            Write-Warning "Missing source: $($pair.Source)"
            $missing++
            continue
        }

        if ($NoWrite) {
            Write-Host "[DRY RUN] $($pair.Source) -> $($pair.Target)"
            $copied++
            continue
        }

        Copy-Item -Path $sourcePath -Destination $targetPath -Force
        Write-Host "Copied: $($pair.Source) -> $($pair.Target)"
        $copied++
    }

    if ($NoWrite) {
        Write-Host "[DRY RUN] Would copy _Sidebar.md from WIKI_SIDEBAR.md"
        Write-Host "[DRY RUN] Would copy wiki order doc to Wiki-Page-Order.md"
    } else {
        Copy-Item -Path $sidebarPath -Destination (Join-Path $WikiDir "_Sidebar.md") -Force
        if (Test-Path $orderPath) {
            Copy-Item -Path $orderPath -Destination (Join-Path $WikiDir "Wiki-Page-Order.md") -Force
        }
    }

    Write-Host ""
    Write-Host "Done."
    Write-Host "Mapped files: $($Pairs.Count)"
    Write-Host "Processed: $copied"
    Write-Host "Missing sources: $missing"
}

Write-Host "Workspace root: $root"
Write-Host "Wiki repo URL: $WikiRepoUrl"
Write-Host "Wiki clone dir: $WikiCloneDir"

Ensure-WikiRepo -RepoUrl $WikiRepoUrl -CloneDir $WikiCloneDir -NoWrite:$DryRun
$mapPairs = Parse-CopyMap -MapFile $copyMapPath
if ($mapPairs.Count -eq 0) {
    throw "No copy mappings found in $copyMapPath"
}

Copy-DocsToWiki -SourceRoot $root -WikiDir $WikiCloneDir -Pairs $mapPairs -NoWrite:$DryRun

if ($DryRun) {
    Write-Host ""
    Write-Host "Dry run complete. Re-run without -DryRun to perform the sync."
} else {
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1) cd `"$WikiCloneDir`""
    Write-Host "2) git status"
    Write-Host "3) git add ."
    Write-Host "4) git commit -m `"docs: sync wiki pages from main repo`""
    Write-Host "5) git push"
}
