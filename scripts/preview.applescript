on run
    set repositoryPath to "/Users/jaap/sandbox/web/blauwedinsdag.github.io"
    do shell script "/usr/bin/open -a Terminal " & quoted form of (repositoryPath & "/scripts/preview.command")
end run
