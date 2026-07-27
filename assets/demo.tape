Output assets/demo.gif

Set Shell "bash"
Set FontSize 15
Set Width 1200
Set Height 680
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 45ms
Set PlaybackSpeed 1.0

Type "cat examples/progress_updates.md | head -14"
Enter
Sleep 2500ms

Type "python3 skill/scripts/render_status.py examples/status.json --outdir /tmp/exec-status-demo"
Enter
Sleep 1500ms

Type "cat /tmp/exec-status-demo/status_report.md | head -27"
Enter
Sleep 4500ms
