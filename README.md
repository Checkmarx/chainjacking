![Frame 237 (2)](https://user-images.githubusercontent.com/1287098/142014140-1e04d384-56aa-4277-9137-687ca0ad957e.png)

A tool to find which of your Go lang direct GitHub dependencies is susceptible to ChainJacking attack


### CI Workflows
You may find this tool also useful when testing new code contributions.  


#### GitHub Actions

https://user-images.githubusercontent.com/1287098/142009618-5eb5d87c-a001-4536-abf3-c5d06216e1b6.mp4

Example configuration:
```yaml
name: Pull Request

on:
  pull_request

jobs:

  build:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: ChainJacking tool test
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m pip install -q chainjacking
          python -m chainjacking -gt $GITHUB_TOKEN
```


### CLI

#### Requirements
- Python 3.6+ and pip
- Go and it's binaries >= 1.13
- GitHub token, to run queries on GitHub API 

#### Installation
```
pip install chainjacking
```

#### CLI Arguments
- `-gt <token>` - GitHub access token, to run queries on GitHub API (required)
- `-p <path>` - Path to scan. (default=current directory)
- `-v` - Verbose output mode
- `-url <url>` - Scan one or more GitHub URLs
- `-f <path>` - Scan one or more GitHub URLs from a file separated by new-line


#### Scan a project
navigate your shell into a Go project's directory, and run:
```
python -m chainjacking -gt $GH_TOKEN
```

