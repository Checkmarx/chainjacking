# ChainJacking
Find which of your go lang direct GitHub dependencies is susceptible to ChainJacking attack

### Requirements
- Go and it's binaries >= 1.13
- GitHub token, to run queries on GitHub API 


### Installation
```
pip install chainjacking
```

### Usage

CLI
```
python -m chainjacking -gt $GH_TOKEN
```

Arguments
- `-gt <token>` - GitHub access token, to run queries on GitHub API (required)
- `-p <path>` - Path to scan. (default=current directory)
- `-v` - Verbose output mode
- `-url <url>` - Scan one or more GitHub URLs
- `-f <path>` - Scan one or more GitHub URLs from a file separated by new-line
