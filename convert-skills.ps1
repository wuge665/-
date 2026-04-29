$sourceDir = "D:\agency-agents-zh"
$targetDir = "C:\Users\tsj\.opencode\skills"

$ErrorActionPreference = "SilentlyContinue"

function ConvertTo-KebabCase {
    param([string]$text)

    $result = $text
    $result = $result -replace [char]0x5de5, "-specialist"
    $result = [regex]::Replace($result, "[^a-zA-Z0-9\-]", "-")
    $result = $result -replace '-+', '-'
    $result = $result.Trim('-')
    $result = $result.ToLower()

    if ($result -match '^-*-specialist' -or $result -eq '') {
        $result = "skill-" + [guid]::NewGuid().ToString("N").Substring(0,8)
    }

    return $result
}

$files = Get-ChildItem -Path $sourceDir -Recurse -Filter "*.md"
$converted = 0

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    if ($content -match '(?m)^---\s*$' -and $content -match '(?m)^name:\s' -and $content -match '(?m)^description:\s') {
        $skillName = $null
        $skillDesc = $null

        if ($content -match '(?m)^name:\s*(.+)$') { $skillName = $matches[1].Trim() }
        if ($content -match '(?m)^description:\s*(.+)$') { $skillDesc = $matches[1].Trim() }

        if ($skillName -and $skillDesc) {
            $converted++
            $folderName = ConvertTo-KebabCase $skillName

            $skillFolder = Join-Path $targetDir $folderName
            if (-not (Test-Path $skillFolder)) {
                New-Item -ItemType Directory -Path $skillFolder -Force | Out-Null
            }

            $newFrontmatter = "---`nname: $skillName`ndescription: $skillDesc`n---`n`n"

            $contentStart = $content.IndexOf("---", 3)
            if ($contentStart -gt 0 -and $contentStart + 3 -lt $content.Length) {
                $bodyContent = $content.Substring($contentStart + 3)
            } else {
                $bodyContent = ""
            }

            $newContent = $newFrontmatter + $bodyContent
            $newFile = Join-Path $skillFolder "SKILL.md"
            [System.IO.File]::WriteAllText($newFile, $newContent, [System.Text.Encoding]::UTF8)
        }
    }
}

Write-Output "Converted $converted skills to $targetDir"
Get-ChildItem -Path $targetDir -Directory | Select-Object Name | Sort-Object Name | Select-Object -First 20