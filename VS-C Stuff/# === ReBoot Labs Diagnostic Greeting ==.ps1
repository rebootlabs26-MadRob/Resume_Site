# === ReBoot Labs Diagnostic Greeting ===
function Write-SegmentedLine {
	param([array]$Segments)
	for ($i = 0; $i -lt $Segments.Count; $i++) {
		$seg = $Segments[$i]
		$opts = @{}
		if ($seg.ContainsKey('Foreground')) { $opts.Add('ForegroundColor', $seg.Foreground) }
		if ($seg.ContainsKey('Background')) { $opts.Add('BackgroundColor', $seg.Background) }
		$noNewline = if ($i -lt $Segments.Count - 1) { $true } else { $false }
		if ($noNewline) {
			Write-Host $seg.Text @opts -NoNewline
		} else {
			Write-Host $seg.Text @opts
		}
	}
}

# Define lines as arrays of segment hashtables (Text, Foreground, optional Background)
$lines = @(
	@(@{ Text = '      ______'; Foreground = 'Green' }),
	@(@{ Text = '   .-        -.'; Foreground = 'Blue' }),
	@(@{ Text = ' //            \\'; Foreground = 'Blue' }),
	@(@{ Text = ' |,  .-.  .-.  ,|'; Foreground = 'Blue' }),
	@(@{ Text = ' |)(_o//  \\o_)(|'; Foreground = 'Blue' }),  # combined face/eyes into one literal
	@(@{ Text = '  |//   /\   \\|'; Foreground = 'Blue' }),
	@(@{ Text = ' (_     ^^     _)'; Foreground = 'Blue' }),
	@(@{ Text = '  \__|IIIIII|__/'; Foreground = 'White' }),
	@(@{ Text = '   | \IIIIII/ |'; Foreground = 'White' }),
	@(@{ Text = '    \        /'; Foreground = 'Green' }),
	@(@{ Text = '     --------'; Foreground = 'Green' }),
	@(@{ Text = '=== ]:< *Nameless WastedTime* >:[ ==='; Foreground = 'Red'; Background = 'Black' })
)

foreach ($line in $lines) {
	Write-SegmentedLine -Segments $line
}
