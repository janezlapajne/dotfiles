# Pipe my public key to my clipboard.
alias pubkey="more ~/.ssh/id_rsa.pub | xclip -selection clipboard && echo '=> Public key copied to pasteboard.'"
