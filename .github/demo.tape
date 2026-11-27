# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR MIT

# The README demo: the MT940 diagnostic engine on the repository's own
# example statements, then the server's lint-and-publish path. Render
# with `make demo`.

Output .github/demo.gif

Set Shell "bash"
Set FontSize 15
Set Width 1200
Set Height 600
Set Padding 20
Set Theme "Catppuccin Mocha"
Set TypingSpeed 35ms

Hide
Type "export PS1='$ ' && clear"
Enter
Show

Type "poetry run python -c 'import bankstatementparser_lsp as l; print(l.__version__)'"
Enter
Wait /\$$/
Sleep 1s

Type "poetry run python examples/01_lsp_helpers.py"
Enter
Wait /\$$/
Sleep 2s

Type "poetry run python examples/04_server_publish.py"
Enter
Wait /\$$/
Sleep 4s
