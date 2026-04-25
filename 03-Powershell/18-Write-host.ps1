# Write-Host: print coloured output to the console
# -ForegroundColor sets the text colour (Green, Red, Yellow, Cyan, White, etc.)
# -BackgroundColor sets the background colour
# -NoNewline suppresses the line break after output

write-host "Hello gagan" -ForegroundColor Green
write-host "Warning: something happened" -ForegroundColor Yellow
write-host "Error: operation failed" -ForegroundColor Red
write-host "Info: " -ForegroundColor Cyan -NoNewline; write-host "inline continuation"
